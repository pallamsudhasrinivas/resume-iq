"""
LLM-powered extraction using Ollama.
Each function returns None on failure; callers fall back to keyword-based logic.
"""

import logging
from typing import Any, Dict, List, Optional

from services.llm_client import chat, extract_json

logger = logging.getLogger(__name__)

_SYSTEM_JD = (
    "You are a technical recruiter assistant. "
    "Extract structured data from job descriptions exactly as instructed. "
    "Respond with valid JSON only — no markdown, no explanation."
)

_SYSTEM_RESUME = (
    "You are a technical recruiter assistant. "
    "Extract structured data from resumes exactly as instructed. "
    "Respond with valid JSON only — no markdown, no explanation."
)


def extract_jd(jd_text: str) -> Optional[Dict[str, Any]]:
    """
    Returns:
      required_skills: list[str]  — all specific technologies, frameworks, tools required
      years_required:  int | null
      role_level:      "junior"|"mid"|"senior"|"lead"|"principal" | null
      domain:          "backend"|"frontend"|"full stack"|"data science"|"data engineering"|
                       "DevOps"|"mobile"|"QA"|"security"|"cloud" | null
    """
    prompt = f"""Extract data from this job description and return JSON with these exact keys:

{{
  "required_skills": ["list every specific technology, framework, tool, language mentioned"],
  "years_required": <integer or null>,
  "role_level": "<junior|mid|senior|lead|principal or null>",
  "domain": "<backend|frontend|full stack|data science|data engineering|DevOps|mobile|QA|security|cloud or null>"
}}

Job description:
{jd_text[:4000]}"""

    result = extract_json([
        {"role": "system", "content": _SYSTEM_JD},
        {"role": "user",   "content": prompt},
    ])
    if not result:
        return None

    # Normalise — ensure required_skills is a list of strings
    skills = result.get("required_skills", [])
    if isinstance(skills, list):
        result["required_skills"] = [s for s in skills if isinstance(s, str) and s.strip()]
    else:
        result["required_skills"] = []

    logger.info("LLM JD extraction: %d skills, domain=%s", len(result["required_skills"]), result.get("domain"))
    return result


def extract_resume(resume_text: str) -> Optional[Dict[str, Any]]:
    """
    Returns:
      candidate_name:  str
      email:           str | null
      skills:          list[str]  — all technologies, tools, languages found
      years_experience: float | null
      education:       list[{degree, field, institution, year}]
      certifications:  list[str]  — canonical full names
      overview:        str        — 3-4 sentence recruiter-facing summary (resume's own words only)
    """
    prompt = f"""Extract data from this resume and return JSON with these exact keys:

{{
  "candidate_name": "full name",
  "email": "email or null",
  "skills": ["every technical skill, tool, framework, language, platform mentioned"],
  "years_experience": <total years of professional work experience as number, or null>,
  "education": [
    {{"degree": "e.g. B.Tech", "field": "e.g. Computer Science", "institution": "university name or null", "year": "graduation year or null"}}
  ],
  "certifications": ["full canonical certification names, e.g. AWS Certified Solutions Architect"],
  "overview": "3-4 sentence professional summary for a recruiter. Use only facts from this resume — candidate's own summary section if present, supplemented by key skills and experience. Do not invent details."
}}

Resume:
{resume_text[:5000]}"""

    result = extract_json([
        {"role": "system", "content": _SYSTEM_RESUME},
        {"role": "user",   "content": prompt},
    ])
    if not result:
        return None

    # Normalise types
    skills = result.get("skills", [])
    result["skills"] = [s for s in skills if isinstance(s, str) and s.strip()] if isinstance(skills, list) else []

    edu = result.get("education", [])
    result["education"] = edu if isinstance(edu, list) else []

    certs = result.get("certifications", [])
    result["certifications"] = [c for c in certs if isinstance(c, str) and c.strip()] if isinstance(certs, list) else []

    yrs = result.get("years_experience")
    try:
        result["years_experience"] = float(yrs) if yrs is not None else None
    except (TypeError, ValueError):
        result["years_experience"] = None

    logger.info(
        "LLM resume extraction: name=%s, skills=%d, yrs=%s",
        result.get("candidate_name"), len(result["skills"]), result.get("years_experience"),
    )
    return result
