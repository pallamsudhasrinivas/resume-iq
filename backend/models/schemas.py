from pydantic import BaseModel
from typing import Any, Dict, List, Optional


class SubScores(BaseModel):
    skills: float
    experience: float
    domain: float
    bonus: float


class EducationEntry(BaseModel):
    degree: str
    field: Optional[str] = None
    year: Optional[str] = None


class CandidateSummary(BaseModel):
    overview: str
    core_capabilities: List[str]
    education: List[EducationEntry]
    certifications: List[str]
    strengths: List[str]
    gaps: List[str]


class CandidateResult(BaseModel):
    candidate_id: str
    filename: str
    candidate_name: str
    email: str
    overall_score: float
    sub_scores: SubScores
    matched_skills: List[str]
    missing_skills: List[str]
    bonus_skills: List[str]
    years_experience: Optional[float]
    recommendation: str
    summary: CandidateSummary


class JDSummary(BaseModel):
    required_skills: List[str]
    years_required: Optional[int]
    role_level: Optional[str]
    domain: Optional[str]


class SessionResponse(BaseModel):
    session_id: str
    job_title: str
    created_at: str
    jd_summary: JDSummary
    candidates: List[CandidateResult]
    candidate_count: int
    avg_score: float
    top_candidate: Optional[str]


class SessionIndex(BaseModel):
    session_id: str
    job_title: str
    created_at: str
    candidate_count: int
    avg_score: float
    top_candidate: Optional[str]
    jd_id: Optional[str] = None


class SessionListResponse(BaseModel):
    sessions: List[SessionIndex]
    total: int
    limit: int
    offset: int


class JDIndex(BaseModel):
    jd_id: str
    title: str
    created_at: str
    session_count: int = 0


class JDEntry(BaseModel):
    jd_id: str
    title: str
    text: str
    created_at: str
    jd_summary: JDSummary
    session_count: int = 0


class JDDetail(JDEntry):
    sessions: List[SessionIndex] = []


class JDListResponse(BaseModel):
    jds: List[JDIndex]
    total: int
    limit: int
    offset: int


class ScoreDistribution(BaseModel):
    strong: int
    good: int
    partial: int
    poor: int


class DashboardStats(BaseModel):
    total_sessions: int
    total_candidates: int
    avg_score: float
    sessions_this_month: int
    score_distribution: ScoreDistribution
    top_missing_skills: List[Dict[str, Any]]
