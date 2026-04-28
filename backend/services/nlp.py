"""
NLP utilities for resume analysis — pure Python, no model downloads required.
"""

import re
from typing import Any, Dict, List, Optional, Set, Tuple

# ── Synonym / abbreviation expansion ──────────────────────────────────────────
SKILL_SYNONYMS: Dict[str, str] = {
    # Languages
    "js": "JavaScript", "ts": "TypeScript", "py": "Python",
    "golang": "Go", "c sharp": "C#",
    # Cloud / infra
    "k8s": "Kubernetes", "kube": "Kubernetes",
    "tf": "Terraform", "iac": "infrastructure as code",
    "gh actions": "GitHub Actions", "gha": "GitHub Actions",
    "google cloud platform": "GCP",
    # Data / ML
    "ml": "machine learning", "dl": "deep learning",
    "nlp": "natural language processing", "cv": "computer vision",
    "rl": "reinforcement learning",
    # Frameworks (avoid over-expanding — only clear aliases)
    "express.js": "Express", "expressjs": "Express",
    "nextjs": "Next.js", "nuxtjs": "Nuxt.js",
    "vuejs": "Vue", "reactjs": "React", "react.js": "React",
    # DBs
    "postgres": "PostgreSQL",
    "mongo": "MongoDB",
    "dynamo": "DynamoDB", "dynamo db": "DynamoDB",
    # CI/CD
    "cicd": "CI/CD",
    # Testing
    "selenium webdriver": "Selenium",
    # Networking
    "rest api": "REST", "restful": "REST", "restful api": "REST",
    "microservice": "microservices", "micro-service": "microservices",
}

# ── Section detection ──────────────────────────────────────────────────────────
# Patterns are searched (not fullmatched) against the cleaned line.
# Non-keyword text on the line must be ≤ 25 chars, OR the line is ALL-CAPS.
_SECTION_PATTERNS: Dict[str, re.Pattern] = {
    name: re.compile(pat, re.IGNORECASE)
    for name, pat in {
        "summary": (
            r"(?:professional\s+|career\s+)?(?:summary|objective|profile|about\s+me|overview|introduction)"
        ),
        "skills": (
            r"(?:technical\s+|key\s+|core\s+|professional\s+)?(?:skills?|competencies|expertise|proficiencies)"
            r"|skills?\s+(?:&|and)\s+(?:technologies|tools?|expertise)"
            r"|technologies\s+(?:&|and)\s+tools?"
            r"|tools?\s+(?:&|and)\s+technologies"
        ),
        "experience": (
            r"(?:professional\s+|work\s+|relevant\s+)?(?:experience|employment|career)"
            r"|work\s+history"
            r"|professional\s+background"
        ),
        "education": (
            r"education(?:al\s+(?:background|qualifications?|details?))?"
            r"|education\s+(?:background|details?|qualifications?)"
            r"|academic\s+(?:background|qualifications?|history|profile)?"
            r"|academic$"
            r"|qualifications?"
            r"|degrees?\s+(?:&|and)\s+certifications?"
        ),
        "certifications": (
            r"certifications?\s*(?:&|and)?\s*(?:awards?|licenses?|credentials?)?"
            r"|licenses?\s*(?:&|and)?\s*certifications?"
            r"|credentials?"
            r"|professional\s+(?:certifications?|development|training)"
        ),
        "projects": (
            r"(?:key\s+|notable\s+|personal\s+|academic\s+)?projects?"
        ),
        "achievements": (
            r"achievements?|accomplishments?|awards?|honors?|recognitions?|publications?"
        ),
        "languages": (
            r"languages?\s+(?:known|spoken|skills?)?$"
            r"|spoken\s+languages?"
        ),
    }.items()
}


def _detect_section_header(line: str) -> Optional[str]:
    """
    Decide whether `line` is a resume section header.

    Accept if:
      (a) The line is ALL-CAPS (very strong signal in resumes), OR
      (b) A section keyword covers most of the line (non-keyword text ≤ 25 chars).
    Reject lines that are too long (likely prose) or too short.
    """
    stripped = line.strip()
    if len(stripped) > 75 or len(stripped) < 2:
        return None

    # Remove common decorators for matching, keep for length check
    clean = re.sub(r"[:\-–—_=*#•|\[\]()]+", " ", stripped)
    clean = re.sub(r"\s+", " ", clean).strip()
    if not clean:
        return None

    is_all_caps = clean.upper() == clean and any(c.isalpha() for c in clean)
    clean_lower = clean.lower()

    for name, pattern in _SECTION_PATTERNS.items():
        m = pattern.search(clean_lower)
        if not m:
            continue
        non_kw = (clean_lower[: m.start()] + clean_lower[m.end() :]).strip()
        # Remove common filler words from the non-keyword remainder
        non_kw = re.sub(r"\b(and|or|the|&|\/)\b", "", non_kw).strip()
        if is_all_caps or len(non_kw) <= 25:
            return name

    return None


def extract_sections(text: str) -> Dict[str, str]:
    """
    Split a resume into named sections.
    Returns {section_name: section_body_text, ...}.
    'other' holds everything before the first detected section.
    """
    lines = text.split("\n")
    buckets: Dict[str, List[str]] = {"other": []}
    current = "other"

    for line in lines:
        detected = _detect_section_header(line)
        if detected:
            current = detected
            buckets.setdefault(current, [])
        else:
            buckets.setdefault(current, []).append(line)

    return {k: "\n".join(v).strip() for k, v in buckets.items() if any(l.strip() for l in v)}


# ── Education ─────────────────────────────────────────────────────────────────
_DEGREE_PATTERNS: List[Tuple[re.Pattern, str]] = [
    (re.compile(r"Ph\.?D\.?|Doctor\s+of\s+Philosophy", re.I), "Ph.D."),
    (re.compile(r"M\.?B\.?A\.?|Master\s+of\s+Business\s+Administration", re.I), "MBA"),
    (re.compile(r"M\.?C\.?A\.?|Master\s+of\s+Computer\s+Applications", re.I), "MCA"),
    (re.compile(r"M\.?Tech\.?|Master\s+of\s+Technology", re.I), "M.Tech"),
    (re.compile(r"M\.?E\.?(?:\b|\.)|Master\s+of\s+Engineering", re.I), "M.E."),
    (re.compile(r"M\.?S\.?c?\.?|Master\s+of\s+Science|Master[\'s]*\s+(?:in\s+)?(?:Science|Sc)", re.I), "M.S."),
    (re.compile(r"Master[\'s]*\s+(?:in\s+|of\s+)[\w\s]+", re.I), "Master's"),
    (re.compile(r"B\.?C\.?A\.?|Bachelor\s+of\s+Computer\s+Applications", re.I), "BCA"),
    (re.compile(r"B\.?Tech\.?|Bachelor\s+of\s+Technology", re.I), "B.Tech"),
    (re.compile(r"B\.?E\.?(?:\b|\.)|Bachelor\s+of\s+Engineering", re.I), "B.E."),
    (re.compile(r"B\.?Sc?\.?|Bachelor\s+of\s+Science|Bachelor[\'s]*\s+(?:in\s+)?(?:Science|Sc)", re.I), "B.Sc."),
    (re.compile(r"B\.?A\.?(?:\b|\.)|Bachelor\s+of\s+Arts", re.I), "B.A."),
    (re.compile(r"Bachelor[\'s]*\s+(?:in\s+|of\s+|degree\s+in\s+)[\w\s]+", re.I), "Bachelor's"),
    (re.compile(r"Associate[\'s]*\s+(?:of|in|degree)\s+[\w\s]+", re.I), "Associate's"),
    (re.compile(r"Diploma\s+(?:in|of)\s+[\w\s]+", re.I), "Diploma"),
    (re.compile(r"High\s+School|HSC|SSC|Secondary", re.I), "High School"),
]

_FIELDS_OF_STUDY: List[str] = [
    "Computer Science and Engineering", "Computer Science", "Computer Engineering",
    "Software Engineering", "Information Technology", "Information Systems",
    "Computer Applications", "Data Science", "Artificial Intelligence",
    "Machine Learning", "Electrical Engineering", "Electronics and Communication",
    "Electronics", "Mathematics", "Statistics", "Physics",
    "Business Administration", "Management Information Systems",
    "Cybersecurity", "Network Engineering", "Mechanical Engineering",
    "Civil Engineering", "Biotechnology",
]

_INSTITUTION_RE = re.compile(
    r"\b("
    r"(?:University|Institute\s+of\s+Technology|College|School|Academy)\b[^,\n]{0,40}"
    r"|IIT[\s\w]*|NIT[\s\w]*|BITS[\s\w]*|VIT[\s\w]*"
    r"|MIT|Stanford|Harvard|Carnegie\s+Mellon|Georgia\s+Tech|Purdue"
    r"|Cornell|Princeton|Yale|Columbia|NYU|USC|UCLA|Caltech"
    r"|JNTU[\s\w]*|IIIT[\s\w]*|Osmania|Anna\s+University|Bangalore\s+University"
    r"|Manipal|Amrita|SRM|BITS\s+Pilani|Hyderabad\s+University"
    r")",
    re.IGNORECASE,
)


def _find_degree(text: str) -> Optional[str]:
    for pattern, label in _DEGREE_PATTERNS:
        if pattern.search(text):
            return label
    return None


def _find_field(text: str) -> Optional[str]:
    # Match longest field first to avoid "Computer Science" inside "Computer Science and Engineering"
    for field in sorted(_FIELDS_OF_STUDY, key=len, reverse=True):
        if re.search(r"(?<!\w)" + re.escape(field) + r"(?!\w)", text, re.IGNORECASE):
            return field
    return None


def _find_graduation_year(text: str) -> Optional[str]:
    """Return graduation year from a date range (takes the end year) or standalone year."""
    # Range — take the end year (graduation)
    m = re.search(
        r"\b((?:19|20)\d{2})\s*[-–—]\s*((?:19|20)\d{2}|present|current|now)\b",
        text, re.IGNORECASE,
    )
    if m:
        end = m.group(2)
        if end.lower() in ("present", "current", "now"):
            return f"{m.group(1)} – Present"
        return end
    # Standalone year
    s = re.search(r"\b((?:19|20)\d{2})\b", text)
    return s.group(1) if s else None


def _find_institution(text: str) -> Optional[str]:
    m = _INSTITUTION_RE.search(text)
    if not m:
        return None
    # Return the matched region trimmed of junk
    raw = m.group(0).strip().rstrip(".,|:;-– ")
    return raw if len(raw) > 2 else None


def extract_education(text: str, sections: Dict[str, str]) -> List[Dict[str, str]]:
    """
    Block-based extraction: group consecutive lines within the education
    section into per-degree blocks, then harvest degree/field/institution/year
    from ALL lines in each block (not just the line that contains the degree).
    """
    edu_text = sections.get("education", "")
    if not edu_text:
        return []

    results: List[Dict[str, str]] = []
    seen: Set[str] = set()

    # Build blocks: a blank line (or a line that starts a new degree) separates entries
    raw_blocks = re.split(r"\n\s*\n", edu_text)

    blocks: List[str] = []
    for raw in raw_blocks:
        lines = [l.strip() for l in raw.split("\n") if l.strip()]
        if not lines:
            continue
        # If the block contains multiple degree lines, split on each degree line
        degree_indices = [i for i, l in enumerate(lines) if _find_degree(l)]
        if len(degree_indices) > 1:
            for start, end in zip(degree_indices, degree_indices[1:] + [len(lines)]):
                blocks.append("\n".join(lines[start:end]))
        else:
            blocks.append("\n".join(lines))

    for block in blocks:
        if not block.strip():
            continue
        block_lines = [l.strip() for l in block.split("\n") if l.strip()]

        degree = institution = field = year = None
        for line in block_lines:
            degree      = degree      or _find_degree(line)
            field       = field       or _find_field(line)
            institution = institution or _find_institution(line)
            year        = year        or _find_graduation_year(line)

        if not degree:
            continue
        key = f"{degree}|{field or ''}"
        if key in seen:
            continue
        seen.add(key)
        entry: Dict[str, str] = {"degree": degree}
        if field:
            entry["field"] = field
        if institution:
            entry["institution"] = institution
        if year:
            entry["year"] = year
        results.append(entry)

    return results


# ── Certifications ────────────────────────────────────────────────────────────
# Each entry: (canonical display name, list of aliases/patterns to search for)
CERTIFICATIONS_DB: List[Tuple[str, List[str]]] = [
    # AWS
    ("AWS Certified Solutions Architect",       ["AWS Certified Solutions Architect", "AWS SAA", "AWS-SAA"]),
    ("AWS Certified Developer",                 ["AWS Certified Developer", "AWS-DVA"]),
    ("AWS Certified SysOps Administrator",      ["AWS Certified SysOps", "AWS-SOA"]),
    ("AWS Certified DevOps Engineer",           ["AWS Certified DevOps", "AWS-DOP"]),
    ("AWS Certified Cloud Practitioner",        ["AWS Certified Cloud Practitioner", "AWS-CLF", "Cloud Practitioner"]),
    ("AWS Certified Data Engineer",             ["AWS Certified Data Engineer"]),
    ("AWS Certified Machine Learning",          ["AWS Certified Machine Learning", "AWS-MLS"]),
    # Azure
    ("Azure Fundamentals (AZ-900)",             ["Azure Fundamentals", "AZ-900"]),
    ("Azure Administrator (AZ-104)",            ["Azure Administrator", "AZ-104"]),
    ("Azure Developer (AZ-204)",                ["Azure Developer Associate", "AZ-204"]),
    ("Azure Solutions Architect (AZ-305)",      ["Azure Solutions Architect", "AZ-305", "AZ-303", "AZ-304"]),
    ("Azure DevOps Engineer (AZ-400)",          ["Azure DevOps Engineer", "AZ-400"]),
    ("Azure Data Engineer (DP-203)",            ["Azure Data Engineer", "DP-203"]),
    # GCP
    ("GCP Associate Cloud Engineer",            ["Associate Cloud Engineer", "GCP ACE"]),
    ("GCP Professional Cloud Architect",        ["Professional Cloud Architect", "GCP PCA"]),
    ("GCP Professional Data Engineer",          ["Professional Data Engineer", "GCP PDE"]),
    # Kubernetes
    ("Certified Kubernetes Administrator (CKA)",         ["Certified Kubernetes Administrator", "CKA"]),
    ("Certified Kubernetes Application Developer (CKAD)",["Certified Kubernetes Application Developer", "CKAD"]),
    ("Certified Kubernetes Security Specialist (CKS)",   ["Certified Kubernetes Security Specialist", "CKS"]),
    # Docker
    ("Docker Certified Associate (DCA)",        ["Docker Certified Associate", "DCA"]),
    # Project / Agile
    ("Project Management Professional (PMP)",   ["Project Management Professional", "PMP"]),
    ("Certified ScrumMaster (CSM)",             ["Certified ScrumMaster", "CSM", "Scrum Master"]),
    ("Professional Scrum Master (PSM)",         ["Professional Scrum Master", "PSM I", "PSM II", "PSM"]),
    ("SAFe Agilist",                            ["SAFe Agilist", "SAFe 5", "SAFe 6"]),
    ("Certified Scrum Product Owner (CSPO)",    ["Certified Scrum Product Owner", "CSPO"]),
    ("PMI-ACP",                                 ["PMI-ACP", "Agile Certified Practitioner"]),
    # Security
    ("CISSP",                                   ["CISSP", "Certified Information Systems Security Professional"]),
    ("CISM",                                    ["CISM", "Certified Information Security Manager"]),
    ("CISA",                                    ["CISA", "Certified Information Systems Auditor"]),
    ("Certified Ethical Hacker (CEH)",          ["Certified Ethical Hacker", "CEH"]),
    ("OSCP",                                    ["OSCP", "Offensive Security Certified Professional"]),
    ("CompTIA Security+",                       ["Security+", "CompTIA Security"]),
    ("CompTIA Network+",                        ["Network+", "CompTIA Network"]),
    # Data / ML / Cloud-data
    ("TensorFlow Developer Certificate",        ["TensorFlow Developer Certificate", "TF Developer"]),
    ("Databricks Certified Associate",          ["Databricks Certified Associate", "Databricks Associate"]),
    ("Databricks Certified Professional",       ["Databricks Certified Professional", "Databricks Professional"]),
    ("Snowflake SnowPro Core",                  ["SnowPro Core", "Snowflake SnowPro"]),
    ("Tableau Desktop Specialist",              ["Tableau Desktop Specialist", "Tableau Specialist"]),
    ("Microsoft PL-300 (Power BI)",             ["PL-300", "Power BI Data Analyst", "Microsoft Certified.*Power BI"]),
    # Java / Oracle
    ("Oracle Certified Professional (Java)",    ["Oracle Certified Professional", "OCP Java", "Java SE.*Programmer"]),
    ("Spring Professional",                     ["Spring Professional Certification", "VMware Spring"]),
    # HashiCorp
    ("HashiCorp Terraform Associate",           ["Terraform Associate", "HashiCorp Certified.*Terraform"]),
    ("HashiCorp Vault Associate",               ["Vault Associate", "HashiCorp Certified.*Vault"]),
    # Linux / Red Hat
    ("RHCE",                                    ["RHCE", "Red Hat Certified Engineer"]),
    ("RHCSA",                                   ["RHCSA", "Red Hat Certified System Administrator"]),
    # Other
    ("ITIL Foundation",                         ["ITIL Foundation", "ITIL 4 Foundation", "ITIL v4"]),
    ("Six Sigma",                               ["Six Sigma", "Lean Six Sigma", "Black Belt", "Green Belt"]),
    ("PRINCE2",                                 ["PRINCE2"]),
]


def extract_certifications(text: str, sections: Dict[str, str]) -> List[str]:
    """
    Match certifications using the canonical DB (each entry has multiple aliases).
    Returns deduplicated canonical names; never double-counts abbreviation + full form.
    """
    # Search the certs section first; also scan full text for robustness
    cert_text = sections.get("certifications", "") + "\n" + text
    found: List[str] = []
    seen_canonical: Set[str] = set()

    for canonical, aliases in CERTIFICATIONS_DB:
        canonical_lower = canonical.lower()
        if canonical_lower in seen_canonical:
            continue
        for alias in aliases:
            # Use regex search so partial alias matches work
            try:
                pattern = re.compile(r"(?<!\w)" + re.escape(alias) + r"(?!\w)", re.IGNORECASE)
            except re.error:
                # alias may contain regex chars
                pattern = re.compile(re.escape(alias), re.IGNORECASE)
            if pattern.search(cert_text):
                found.append(canonical)
                seen_canonical.add(canonical_lower)
                break  # Found this cert; move to next canonical entry

    return found


# ── Role clusters ─────────────────────────────────────────────────────────────
# Each value: (required_skills_list, context_keywords_for_experience_boost)
ROLE_CLUSTERS: Dict[str, Tuple[List[str], List[str]]] = {
    "Frontend Developer": (
        ["React", "Angular", "Vue", "JavaScript", "TypeScript", "CSS", "HTML", "Next.js", "Svelte"],
        ["frontend", "ui", "user interface", "web app", "single page"],
    ),
    "Backend Developer": (
        ["Python", "Java", "Node.js", "Django", "FastAPI", "Spring Boot", "PostgreSQL", "MySQL", "REST", "microservices"],
        ["backend", "server", "api", "rest", "microservice", "service"],
    ),
    "Full Stack Developer": (
        ["React", "Node.js", "JavaScript", "TypeScript", "PostgreSQL", "MongoDB", "REST", "HTML", "CSS"],
        ["full stack", "fullstack", "end-to-end", "frontend and backend"],
    ),
    "DevOps / Platform Engineer": (
        ["Docker", "Kubernetes", "Terraform", "Ansible", "Jenkins", "GitHub Actions", "CI/CD", "Linux", "AWS"],
        ["devops", "platform", "deployment", "pipeline", "infrastructure", "cicd"],
    ),
    "Cloud Engineer": (
        ["AWS", "Azure", "GCP", "Terraform", "Kubernetes", "CloudFormation", "serverless", "Docker"],
        ["cloud", "aws", "azure", "gcp", "infrastructure"],
    ),
    "Site Reliability Engineer": (
        ["Kubernetes", "Docker", "Prometheus", "Grafana", "CI/CD", "Linux", "Python", "observability"],
        ["reliability", "sre", "on-call", "incident", "slo", "sla", "uptime"],
    ),
    "Data Engineer": (
        ["Python", "Spark", "Kafka", "Airflow", "dbt", "SQL", "Databricks", "data engineering"],
        ["data pipeline", "etl", "elt", "data warehouse", "data lake", "spark", "kafka"],
    ),
    "Data Scientist": (
        ["Python", "machine learning", "TensorFlow", "PyTorch", "Scikit-learn", "Pandas", "NumPy", "deep learning"],
        ["data science", "model", "prediction", "analysis", "machine learning", "neural"],
    ),
    "ML / AI Engineer": (
        ["Python", "TensorFlow", "PyTorch", "Scikit-learn", "MLflow", "deep learning", "feature engineering"],
        ["machine learning", "ml", "ai", "model training", "inference", "deep learning"],
    ),
    "QA / Test Automation Engineer": (
        ["Selenium", "Cypress", "pytest", "JUnit", "test automation", "API testing", "Playwright"],
        ["testing", "qa", "quality", "test automation", "test cases", "defect"],
    ),
    "Performance Engineer": (
        ["JMeter", "Gatling", "k6", "performance testing", "load testing", "Locust"],
        ["performance", "load test", "stress test", "latency", "throughput", "nfr"],
    ),
    "Security Engineer": (
        ["penetration testing", "OWASP", "SAST", "DAST", "JWT", "OAuth", "vulnerability assessment"],
        ["security", "vulnerability", "penetration", "exploit", "appsec"],
    ),
    "Mobile Developer": (
        ["React Native", "Flutter", "iOS", "Android", "Swift", "Kotlin", "SwiftUI", "Jetpack Compose"],
        ["mobile", "ios", "android", "app development", "flutter", "react native"],
    ),
    "Software Architect / Tech Lead": (
        ["microservices", "system design", "distributed systems", "domain-driven design", "leadership", "cloud"],
        ["architect", "tech lead", "principal", "design", "system design", "architecture"],
    ),
}


# ── Proficiency markers ────────────────────────────────────────────────────────
_EXPERT_RE   = re.compile(r"\b(expert|expertise|proficient|extensive|advanced|strong|deep|lead|architect|hands.on)\b", re.I)
_FAMILIAR_RE = re.compile(r"\b(basic|familiar|exposure|beginner|novice|elementary|learning|introductory|awareness)\b", re.I)
_NEGATION_RE = re.compile(r"\b(no|not|without|lack|never)\s+(?:\w+\s+){0,3}", re.I)


# ═══════════════════════════════════════════════════════════════════════════════
# Public API
# ═══════════════════════════════════════════════════════════════════════════════

def expand_synonyms(text: str) -> str:
    """Replace known abbreviations with their canonical skill name."""
    result = text
    for alias, canonical in SKILL_SYNONYMS.items():
        result = re.sub(
            r"(?<!\w)" + re.escape(alias) + r"(?!\w)",
            canonical,
            result,
            flags=re.IGNORECASE,
        )
    return result


def score_skill_proficiency(skill: str, full_text: str, sections: Dict[str, str]) -> float:
    """
    Return a weight multiplier (0.1 – 1.5) for a skill based on:
    - Section it appears in (skills section → highest signal)
    - Proficiency markers near the skill mention
    - Mention frequency
    """
    weight = 1.0
    skill_re = re.compile(r"(?<!\w)" + re.escape(skill.lower()) + r"(?!\w)", re.IGNORECASE)

    # Section boost
    if skill_re.search(sections.get("skills", "")):
        weight += 0.25
    elif skill_re.search(sections.get("experience", "")):
        weight += 0.10

    # Frequency boost (capped)
    freq = len(skill_re.findall(full_text))
    weight += min((freq - 1) * 0.05, 0.15)

    # Proficiency window (±80 chars around each mention)
    for m in skill_re.finditer(full_text):
        start  = max(0, m.start() - 80)
        window = full_text[start : m.end() + 80].lower()
        prefix = full_text[start : m.start()].lower()
        if _NEGATION_RE.search(prefix):
            weight -= 0.40
            break
        if _EXPERT_RE.search(window):
            weight += 0.15
            break
        if _FAMILIAR_RE.search(window):
            weight -= 0.20
            break

    return max(0.1, min(weight, 1.5))


def _dedupe_subset_skills(skills: List[str]) -> List[str]:
    """
    Remove any skill whose lowercase form is a proper substring of another skill in the list.
    E.g. 'GitHub' is removed when 'GitHub Actions' is also present.
    """
    lower = [s.lower() for s in skills]
    result = []
    for i, skill in enumerate(skills):
        is_subset = any(
            i != j and lower[i] in lower[j] and lower[i] != lower[j]
            for j in range(len(skills))
        )
        if not is_subset:
            result.append(skill)
    return result


def _pick_core_capabilities(
    skills_found: Set[str],
    sections: Dict[str, str],
    full_text: str = "",
    top_n: int = 10,
) -> List[str]:
    """
    Rank skills by depth signals:
      - Skills section presence (+5)
      - Experience section frequency (+1.5 per mention, capped at +4)
      - Summary section mention (+2)
      - Total document frequency (+0.2 per mention, capped at +2)
    Then deduplicate subsets and return top_n.
    """
    skills_text  = sections.get("skills", "")
    exp_text     = sections.get("experience", "")
    summary_text = sections.get("summary", "")

    scored: List[Tuple[float, str]] = []
    for skill in skills_found:
        score = 0.0
        skill_re = re.compile(r"(?<!\w)" + re.escape(skill.lower()) + r"(?!\w)", re.IGNORECASE)

        if skills_text and skill_re.search(skills_text):
            score += 5.0
        if exp_text:
            cnt = len(skill_re.findall(exp_text))
            score += min(cnt * 1.5, 4.0)
        if summary_text and skill_re.search(summary_text):
            score += 2.0
        if full_text:
            total = len(skill_re.findall(full_text))
            score += min(total * 0.2, 2.0)

        scored.append((score, skill))

    scored.sort(reverse=True)
    ranked = [s for _, s in scored]
    deduped = _dedupe_subset_skills(ranked)
    return deduped[:top_n]


def get_suitable_roles(
    skills_found: Set[str],
    sections: Optional[Dict[str, str]] = None,
    top_n: int = 4,
) -> List[str]:
    """
    Score each role by:
      1. Skill coverage ratio (must be ≥ 40% to qualify)
      2. Context boost: role-related keywords found in experience/summary sections
    Return the top_n best-matching roles.
    """
    sections = sections or {}
    found_lower = {s.lower() for s in skills_found}
    context_text = (
        sections.get("experience", "") + " " + sections.get("summary", "")
    ).lower()

    scored: List[Tuple[float, str]] = []
    for role, (required, ctx_kws) in ROLE_CLUSTERS.items():
        req_lower = [r.lower() for r in required]
        matched   = sum(1 for r in req_lower if r in found_lower)
        ratio     = matched / len(req_lower)

        if ratio < 0.40:   # minimum meaningful coverage
            continue

        score = ratio
        # Context boost: +0.25 if any role keyword appears in experience/summary
        if any(kw in context_text for kw in ctx_kws):
            score += 0.25

        scored.append((score, role))

    scored.sort(reverse=True)
    return [role for _, role in scored[:top_n]]


def build_candidate_summary(
    candidate_name: str,
    years_experience: Optional[float],
    skills_found: Set[str],
    matched_skills: List[str],
    missing_skills: List[str],
    overall_score: float,
    recommendation: str,
    full_text: str,
    sections: Dict[str, str],
    llm_education: Optional[List[Dict[str, str]]] = None,
    llm_certifications: Optional[List[str]] = None,
    llm_overview: Optional[str] = None,
) -> Dict[str, Any]:
    # Prefer LLM-extracted education/certifications; fall back to regex extraction
    education      = llm_education      if llm_education      is not None else extract_education(full_text, sections)
    certifications = llm_certifications if llm_certifications is not None else extract_certifications(full_text, sections)

    core_caps = _pick_core_capabilities(skills_found, sections, full_text)
    strengths = _derive_strengths(matched_skills, skills_found, sections, years_experience, certifications)

    # Prefer LLM-generated overview; fall back to template
    overview = llm_overview or _write_overview(
        candidate_name, years_experience, core_caps,
        education, certifications, sections,
    )

    return {
        "overview":          overview,
        "core_capabilities": core_caps,
        "education":         education,
        "certifications":    certifications,
        "strengths":         strengths,
        "gaps":              missing_skills[:6],
    }


# ── Internal helpers ───────────────────────────────────────────────────────────

def _write_overview(
    name: str,
    years: Optional[float],
    capabilities: List[str],
    education: List[Dict[str, str]],
    certifications: List[str],
    sections: Dict[str, str],
) -> str:
    own_summary = sections.get("summary", "").strip()

    if own_summary:
        # Use the candidate's own words — take up to 3 sentences (≤ 400 chars)
        sentences = re.split(r"(?<=[.!?])\s+", own_summary)
        sentences = [s.strip() for s in sentences if len(s.strip()) > 10]
        base = ""
        for s in sentences[:3]:
            if len(base) + len(s) + 1 <= 400:
                base = (base + " " + s).strip()
            else:
                break
        overview = base
    else:
        # No summary section — build a minimal factual sentence from extracted data only
        exp_str = f"{int(years)}+" if years and years >= 1 else None
        if exp_str:
            overview = f"{name} has {exp_str} years of professional experience."
        else:
            overview = f"No summary section detected in {name}'s resume."

    # Append education only if a degree was actually extracted and not already mentioned
    if education:
        edu = education[0]
        degree = edu.get("degree", "")
        field  = edu.get("field", "")
        inst   = edu.get("institution", "")
        year   = edu.get("year", "")
        if degree and degree.lower() not in overview.lower():
            edu_str = degree + (f" in {field}" if field else "")
            if inst:
                edu_str += f", {inst}"
            if year:
                edu_str += f" ({year})"
            overview += f" Holds a {edu_str}."

    # Append certifications only if actually found in the resume
    if certifications:
        first_word = certifications[0].split()[0].lower()
        if first_word not in overview.lower():
            cert_list = ", ".join(certifications[:3])
            suffix = f" and {len(certifications) - 3} more" if len(certifications) > 3 else ""
            overview += f" Certifications: {cert_list}{suffix}."

    return overview


def _derive_strengths(
    matched_skills: List[str],
    skills_found: Set[str],
    sections: Dict[str, str],
    years: Optional[float],
    certifications: List[str],
) -> List[str]:
    strengths: List[str] = []
    found_lower = {s.lower() for s in skills_found}

    # Experience level
    if years:
        label = (
            f"{int(years)}+ years of professional experience"
            if years >= 8
            else f"{int(years)}-year professional background"
        )
        strengths.append(label)

    # Which role clusters is this candidate strong in (≥ 60% coverage)?
    strong: List[str] = []
    for role, (required, _) in ROLE_CLUSTERS.items():
        req_lower = [r.lower() for r in required]
        ratio = sum(1 for r in req_lower if r in found_lower) / len(req_lower)
        if ratio >= 0.60:
            strong.append(role)
    for cluster in strong[:2]:
        strengths.append(f"Strong {cluster} skill set")

    # Certifications
    if certifications:
        strengths.append(f"Industry certified — {certifications[0]}")

    # Skill coverage
    if len(matched_skills) >= 8:
        strengths.append("Broad coverage of required job skills")
    elif len(matched_skills) >= 5:
        strengths.append("Good coverage of core requirements")

    # Presence in skills section
    skills_section = sections.get("skills", "")
    if skills_section and len(skills_section) > 100:
        strengths.append("Well-structured technical skills profile")

    return strengths[:5]
