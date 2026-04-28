import logging
import re
import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Set, Tuple

from services.nlp import (
    ROLE_CLUSTERS,
    build_candidate_summary,
    expand_synonyms,
    extract_sections,
    score_skill_proficiency,
)
from services.parser import extract_text
from services.skills_vocab import SKILLS_VOCAB
import services.llm_extractor as llm_extractor

logger = logging.getLogger(__name__)

# ── Domain detection ───────────────────────────────────────────────────────────
DOMAIN_DETECTION: Dict[str, List[str]] = {
    "QA":                 ["quality assurance", "qa engineer", "sdet", "test engineer", "tester"],
    "performance testing":["performance testing", "load testing", "stress testing", "jmeter", "loadrunner", "gatling"],
    "backend":            ["backend", "server-side", "api development", "microservices", "rest api"],
    "frontend":           ["frontend", "ui engineer", "user interface"],
    "data science":       ["data science", "machine learning", "deep learning", "ai engineer", "ml engineer"],
    "data engineering":   ["data engineering", "etl", "data pipeline"],
    "DevOps":             ["devops", "platform engineer", "site reliability", "ci/cd pipeline"],
    "mobile":             ["mobile developer", "ios developer", "android developer"],
    "security":           ["security engineer", "cybersecurity", "penetration testing", "appsec"],
    "cloud":              ["cloud engineer", "cloud architect", "cloud infrastructure"],
}

DOMAIN_SKILLS: Dict[str, List[str]] = {
    "QA":                 ["Selenium","Cypress","pytest","JUnit","TestNG","Playwright","Appium","Robot Framework","test automation"],
    "performance testing":["JMeter","LoadRunner","Gatling","k6","Locust","Artillery","performance testing","load testing"],
    "backend":            ["Python","Java","Node.js","REST","GraphQL","gRPC","PostgreSQL","MySQL","MongoDB","Redis","microservices"],
    "frontend":           ["React","Angular","Vue","TypeScript","JavaScript","CSS","HTML","Redux","Next.js"],
    "data science":       ["Python","machine learning","deep learning","TensorFlow","PyTorch","Scikit-learn","Pandas","NumPy"],
    "data engineering":   ["Spark","Kafka","Airflow","dbt","Python","SQL","Hadoop","Flink","Databricks"],
    "DevOps":             ["Docker","Kubernetes","Terraform","Ansible","Jenkins","GitHub Actions","CI/CD","Helm","AWS"],
    "mobile":             ["React Native","Flutter","iOS","Android","Swift","Kotlin","SwiftUI","Jetpack Compose"],
    "security":           ["penetration testing","OWASP","SAST","DAST","JWT","OAuth","TLS","vulnerability assessment"],
    "cloud":              ["AWS","Azure","GCP","Terraform","Kubernetes","Docker","CloudFormation","serverless"],
}

ROLE_LEVELS: Dict[str, List[str]] = {
    "junior":    ["junior", "entry level", "entry-level", "associate", "jr."],
    "mid":       ["mid level", "mid-level", "intermediate"],
    "senior":    ["senior", "sr.", "sr "],
    "lead":      ["lead", "tech lead", "team lead"],
    "principal": ["principal", "staff engineer", "architect"],
}


# ── Core matching ──────────────────────────────────────────────────────────────

def _match_skills(text: str) -> Set[str]:
    """Match skills from vocab against text (after synonym expansion)."""
    expanded = expand_synonyms(text)
    lower    = expanded.lower()
    matched: Set[str] = set()
    for skill in SKILLS_VOCAB:
        if re.search(r"(?<!\w)" + re.escape(skill.lower()) + r"(?!\w)", lower):
            matched.add(skill)
    return matched


def _extract_years_required(text: str) -> Optional[int]:
    for pattern in [
        r"(\d+)\+?\s*years?\s+(?:of\s+)?(?:relevant\s+|related\s+|professional\s+)?experience",
        r"minimum\s+(?:of\s+)?(\d+)\s*years?",
        r"at\s+least\s+(\d+)\s*years?",
        r"(\d+)\+\s*years?",
    ]:
        m = re.search(pattern, text, re.IGNORECASE)
        if m:
            return int(m.group(1))
    return None


def _extract_role_level(text: str) -> Optional[str]:
    lower = text.lower()
    for level, kws in ROLE_LEVELS.items():
        for kw in kws:
            if re.search(r"(?<!\w)" + re.escape(kw) + r"(?!\w)", lower):
                return level
    return None


def _extract_domain(text: str) -> Optional[str]:
    lower = text.lower()
    for domain, kws in DOMAIN_DETECTION.items():
        for kw in kws:
            if re.search(r"(?<!\w)" + re.escape(kw) + r"(?!\w)", lower):
                return domain
    return None


def _extract_candidate_name(text: str) -> str:
    for line in text.strip().split("\n")[:15]:
        line = line.strip()
        if not line or "@" in line or len(line) > 60 or len(line) < 4:
            continue
        words = line.split()
        if 2 <= len(words) <= 4 and all(w[0].isupper() for w in words if w.isalpha()):
            return line
    return "Unknown"


def _extract_email(text: str) -> str:
    m = re.search(r"[\w.+-]+@[\w-]+\.[a-z]{2,}", text, re.IGNORECASE)
    return m.group(0) if m else ""


def _extract_years_experience(text: str) -> Optional[float]:
    total = 0.0
    for start, end in re.findall(
        r"(20\d{2})\s*[-–—]\s*(20\d{2}|present|current|now)", text, re.IGNORECASE
    ):
        s = int(start)
        e = 2025 if end.lower() in ("present", "current", "now") else int(end)
        total += max(0, e - s)

    # Fallback: explicit "X years of experience" in the resume itself
    if total == 0:
        m = re.search(r"(\d+)\+?\s*years?\s+of\s+(?:total\s+)?experience", text, re.IGNORECASE)
        if m:
            total = float(m.group(1))

    return min(total, 30) if total > 0 else None


# ── JD parsing ─────────────────────────────────────────────────────────────────

def parse_jd(jd_text: str) -> Dict[str, Any]:
    job_title = "Untitled Position"
    for line in jd_text.strip().split("\n")[:5]:
        line = line.strip()
        if line and len(line) < 100:
            job_title = line
            break

    # Try LLM extraction first
    llm = llm_extractor.extract_jd(jd_text)
    if llm and llm.get("required_skills"):
        logger.info("JD parsed via LLM (%d skills)", len(llm["required_skills"]))
        # Supplement LLM skills with keyword matcher to catch anything missed
        expanded = expand_synonyms(jd_text)
        kw_skills = _match_skills(expanded)
        llm_lower = {s.lower() for s in llm["required_skills"]}
        extra = [s for s in kw_skills if s.lower() not in llm_lower]
        combined = llm["required_skills"] + extra
        return {
            "job_title":       job_title,
            "required_skills": combined,
            "years_required":  llm.get("years_required") or _extract_years_required(jd_text),
            "role_level":      llm.get("role_level")     or _extract_role_level(jd_text),
            "domain":          llm.get("domain")         or _extract_domain(jd_text),
        }

    # Fallback: keyword-only
    logger.info("JD parsed via keyword matcher (LLM unavailable)")
    expanded = expand_synonyms(jd_text)
    return {
        "job_title":       job_title,
        "required_skills": list(_match_skills(expanded)),
        "years_required":  _extract_years_required(jd_text),
        "role_level":      _extract_role_level(jd_text),
        "domain":          _extract_domain(jd_text),
    }


# ── Enhanced scoring ───────────────────────────────────────────────────────────

def score_candidate(
    resume_data: Dict[str, Any],
    jd_data: Dict[str, Any],
) -> Dict[str, Any]:
    required: Set[str]  = {s.lower() for s in jd_data.get("required_skills", [])}
    found:    Set[str]  = {s.lower() for s in resume_data.get("skills_found", set())}
    sections: Dict[str, str] = resume_data.get("sections", {})
    full_text: str           = resume_data.get("full_text", "")

    domain     = jd_data.get("domain")
    domain_kws = {kw.lower() for kw in DOMAIN_SKILLS.get(domain, [])} if domain else set()

    matched_lower = required & found
    missing_lower = required - found
    bonus_lower   = found - required

    req_map   = {s.lower(): s for s in jd_data.get("required_skills", [])}
    found_map = {s.lower(): s for s in resume_data.get("skills_found", set())}

    matched_skills = sorted(req_map.get(s, s) for s in matched_lower)
    missing_skills = sorted(req_map.get(s, s) for s in missing_lower)
    bonus_skills   = sorted(found_map.get(s, s) for s in list(bonus_lower)[:25])

    # ── Skills score (50%) — proficiency-weighted ──────────────────────────────
    if required:
        weight_total = 0.0
        for skill_lower in matched_lower:
            canonical = req_map.get(skill_lower, skill_lower)
            w = score_skill_proficiency(canonical, full_text, sections)
            weight_total += w
        # Max possible weight if every required skill matched at 1.0
        max_weight   = len(required) * 1.0
        skills_score = min(weight_total / max_weight, 1.0) * 100
    else:
        skills_score = 50.0

    # ── Experience score (25%) ─────────────────────────────────────────────────
    years_req = jd_data.get("years_required")
    years_exp = resume_data.get("years_experience")
    if years_req is None:
        experience_score = 70.0
    elif years_exp is None:
        experience_score = 50.0
    else:
        experience_score = min(years_exp / years_req, 1.0) * 100

    # ── Domain score (15%) ────────────────────────────────────────────────────
    if not domain_kws:
        domain_score = 70.0
    else:
        matched_domain = domain_kws & found
        domain_score   = min(len(matched_domain) / 3.0, 1.0) * 100

    # ── Bonus score (10%) ────────────────────────────────────────────────────
    bonus_score = min(len(bonus_lower) / 5.0, 1.0) * 100

    overall = round(
        skills_score * 0.50
        + experience_score * 0.25
        + domain_score * 0.15
        + bonus_score * 0.10,
        1,
    )

    if overall >= 80:
        recommendation = "Strong Match"
    elif overall >= 60:
        recommendation = "Good Match"
    elif overall >= 40:
        recommendation = "Partial Match"
    else:
        recommendation = "Poor Match"

    # ── Candidate summary ─────────────────────────────────────────────────────
    summary = build_candidate_summary(
        candidate_name     = resume_data["candidate_name"],
        years_experience   = resume_data.get("years_experience"),
        skills_found       = resume_data.get("skills_found", set()),
        matched_skills     = matched_skills,
        missing_skills     = missing_skills,
        overall_score      = overall,
        recommendation     = recommendation,
        full_text          = full_text,
        sections           = sections,
        llm_education      = resume_data.get("llm_education"),
        llm_certifications = resume_data.get("llm_certifications"),
        llm_overview       = resume_data.get("llm_overview"),
    )

    return {
        "candidate_id":   str(uuid.uuid4()),
        "filename":       resume_data["filename"],
        "candidate_name": resume_data["candidate_name"],
        "email":          resume_data["email"],
        "overall_score":  overall,
        "sub_scores": {
            "skills":     round(skills_score, 1),
            "experience": round(experience_score, 1),
            "domain":     round(domain_score, 1),
            "bonus":      round(bonus_score, 1),
        },
        "matched_skills": matched_skills,
        "missing_skills": missing_skills,
        "bonus_skills":   bonus_skills,
        "years_experience": resume_data.get("years_experience"),
        "recommendation": recommendation,
        "summary":        summary,
    }


# ── Session entry point ────────────────────────────────────────────────────────

def run_session(
    jd_text: str,
    resumes: List[Tuple[str, bytes]],
) -> Dict[str, Any]:
    jd_data    = parse_jd(jd_text)
    candidates = []

    for filename, file_bytes in resumes:
        resume_text  = extract_text(filename, file_bytes)
        expanded     = expand_synonyms(resume_text)
        sections     = extract_sections(expanded)
        kw_skills    = _match_skills(expanded)

        # Try LLM extraction
        llm = llm_extractor.extract_resume(resume_text)
        if llm and llm.get("skills"):
            logger.info("Resume '%s' parsed via LLM (%d skills)", filename, len(llm["skills"]))
            # Merge LLM skills with keyword matches — match them against vocab for normalisation
            llm_skill_text = " ".join(llm["skills"])
            llm_matched    = _match_skills(expand_synonyms(llm_skill_text))
            skills_found   = kw_skills | llm_matched

            exp_text_for_years = sections.get("experience") or resume_text
            resume_data = {
                "filename":         filename,
                "candidate_name":   llm.get("candidate_name") or _extract_candidate_name(resume_text),
                "email":            llm.get("email")           or _extract_email(resume_text),
                "skills_found":     skills_found,
                "years_experience": llm.get("years_experience") or _extract_years_experience(exp_text_for_years),
                "llm_education":    llm.get("education", []),
                "llm_certifications": llm.get("certifications", []),
                "llm_overview":     llm.get("overview"),
                "sections":         sections,
                "full_text":        expanded,
            }
        else:
            logger.info("Resume '%s' parsed via keyword matcher (LLM unavailable)", filename)
            exp_text_for_years = sections.get("experience") or resume_text
            resume_data = {
                "filename":         filename,
                "candidate_name":   _extract_candidate_name(resume_text),
                "email":            _extract_email(resume_text),
                "skills_found":     kw_skills,
                "years_experience": _extract_years_experience(exp_text_for_years),
                "sections":         sections,
                "full_text":        expanded,
            }

        candidates.append(score_candidate(resume_data, jd_data))

    candidates.sort(key=lambda c: c["overall_score"], reverse=True)
    avg_score = (
        round(sum(c["overall_score"] for c in candidates) / len(candidates), 1)
        if candidates else 0.0
    )

    return {
        "session_id":     str(uuid.uuid4()),
        "job_title":      jd_data["job_title"],
        "created_at":     datetime.now(timezone.utc).isoformat(),
        "jd_summary": {
            "required_skills": jd_data["required_skills"],
            "years_required":  jd_data.get("years_required"),
            "role_level":      jd_data.get("role_level"),
            "domain":          jd_data.get("domain"),
        },
        "candidates":      candidates,
        "candidate_count": len(candidates),
        "avg_score":       avg_score,
        "top_candidate":   candidates[0]["candidate_name"] if candidates else None,
    }
