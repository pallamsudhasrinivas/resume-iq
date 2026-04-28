"""
Data-access layer — all persistence goes through here.
Backed by SQLAlchemy (SQLite by default; swap DATABASE_URL for Postgres/MySQL).
"""

import json
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from sqlalchemy import func, select, update

from services.database import (
    CandidateModel,
    JDModel,
    SessionLocal,
    SessionModel,
    create_tables,
)

# Ensure tables exist on first import
create_tables()


# ── Helpers ────────────────────────────────────────────────────────────────────

def _j(obj: Any) -> str:
    return json.dumps(obj)

def _p(text: str) -> Any:
    return json.loads(text) if text else None


def _session_to_index(row: SessionModel) -> Dict[str, Any]:
    return {
        "session_id":     row.session_id,
        "job_title":      row.job_title,
        "created_at":     row.created_at,
        "candidate_count": len(row.candidates),
        "avg_score":      row.avg_score,
        "top_candidate":  row.top_candidate,
        "jd_id":          row.jd_id,
    }


def _candidate_to_dict(row: CandidateModel) -> Dict[str, Any]:
    return {
        "candidate_id":   row.candidate_id,
        "filename":       row.filename,
        "candidate_name": row.candidate_name,
        "email":          row.email,
        "overall_score":  row.overall_score,
        "sub_scores":     _p(row.sub_scores),
        "matched_skills": _p(row.matched_skills),
        "missing_skills": _p(row.missing_skills),
        "bonus_skills":   _p(row.bonus_skills),
        "years_experience": row.years_experience,
        "recommendation": row.recommendation,
        "summary":        _p(row.summary),
    }


def _session_to_full(row: SessionModel) -> Dict[str, Any]:
    return {
        "session_id":      row.session_id,
        "job_title":       row.job_title,
        "created_at":      row.created_at,
        "jd_id":           row.jd_id,
        "jd_summary":      _p(row.jd_summary),
        "candidates":      [_candidate_to_dict(c) for c in row.candidates],
        "candidate_count": len(row.candidates),
        "avg_score":       row.avg_score,
        "top_candidate":   row.top_candidate,
    }


def _jd_to_dict(row: JDModel, include_sessions: bool = False) -> Dict[str, Any]:
    d = {
        "jd_id":       row.jd_id,
        "title":       row.title,
        "text":        row.text,
        "created_at":  row.created_at,
        "session_count": row.session_count,
        "jd_summary":  _p(row.jd_summary),
    }
    if include_sessions:
        d["sessions"] = [_session_to_index(s) for s in row.sessions]
    return d


# ══════════════════════════════════════════════════════════════════════════════
# Sessions
# ══════════════════════════════════════════════════════════════════════════════

def save_session(session: Dict[str, Any]) -> None:
    with SessionLocal() as db:
        sid = session["session_id"]
        existing = db.get(SessionModel, sid)
        if existing:
            db.delete(existing)
            db.flush()

        row = SessionModel(
            session_id    = sid,
            job_title     = session["job_title"],
            created_at    = session["created_at"],
            jd_id         = session.get("jd_id"),
            jd_summary    = _j(session["jd_summary"]),
            avg_score     = session.get("avg_score", 0.0),
            top_candidate = session.get("top_candidate"),
        )
        for c in session.get("candidates", []):
            row.candidates.append(CandidateModel(
                candidate_id    = c["candidate_id"],
                filename        = c["filename"],
                candidate_name  = c["candidate_name"],
                email           = c["email"],
                overall_score   = c["overall_score"],
                sub_scores      = _j(c["sub_scores"]),
                matched_skills  = _j(c["matched_skills"]),
                missing_skills  = _j(c["missing_skills"]),
                bonus_skills    = _j(c["bonus_skills"]),
                years_experience = c.get("years_experience"),
                recommendation  = c["recommendation"],
                summary         = _j(c["summary"]),
            ))
        db.add(row)

        # Increment session_count on the linked JD
        if session.get("jd_id"):
            db.execute(
                update(JDModel)
                .where(JDModel.jd_id == session["jd_id"])
                .values(session_count=JDModel.session_count + 1)
            )
        db.commit()


def get_session(session_id: str) -> Optional[Dict[str, Any]]:
    with SessionLocal() as db:
        row = db.get(SessionModel, session_id)
        return _session_to_full(row) if row else None


def list_sessions(
    limit: int = 20,
    offset: int = 0,
    search: Optional[str] = None,
) -> Dict[str, Any]:
    with SessionLocal() as db:
        q = select(SessionModel).order_by(SessionModel.created_at.desc())
        if search:
            q = q.where(SessionModel.job_title.ilike(f"%{search}%"))
        total = db.scalar(select(func.count()).select_from(q.subquery()))
        rows  = db.scalars(q.offset(offset).limit(limit)).all()
        return {
            "sessions": [_session_to_index(r) for r in rows],
            "total":    total,
            "limit":    limit,
            "offset":   offset,
        }


def delete_session(session_id: str) -> bool:
    with SessionLocal() as db:
        row = db.get(SessionModel, session_id)
        if not row:
            return False
        db.delete(row)
        db.commit()
        return True


# ══════════════════════════════════════════════════════════════════════════════
# JDs
# ══════════════════════════════════════════════════════════════════════════════

def save_jd(jd: Dict[str, Any]) -> None:
    with SessionLocal() as db:
        existing = db.get(JDModel, jd["jd_id"])
        if existing:
            db.delete(existing)
            db.flush()
        db.add(JDModel(
            jd_id         = jd["jd_id"],
            title         = jd["title"],
            text          = jd["text"],
            created_at    = jd["created_at"],
            session_count = jd.get("session_count", 0),
            jd_summary    = _j(jd["jd_summary"]),
        ))
        db.commit()


def get_jd(jd_id: str) -> Optional[Dict[str, Any]]:
    with SessionLocal() as db:
        row = db.get(JDModel, jd_id)
        return _jd_to_dict(row) if row else None


def list_jds(limit: int = 50, offset: int = 0) -> Dict[str, Any]:
    with SessionLocal() as db:
        q     = select(JDModel).order_by(JDModel.created_at.desc())
        total = db.scalar(select(func.count()).select_from(q.subquery()))
        rows  = db.scalars(q.offset(offset).limit(limit)).all()
        return {
            "jds":    [_jd_to_dict(r) for r in rows],
            "total":  total,
            "limit":  limit,
            "offset": offset,
        }


def delete_jd(jd_id: str) -> bool:
    with SessionLocal() as db:
        row = db.get(JDModel, jd_id)
        if not row:
            return False
        db.delete(row)
        db.commit()
        return True


def get_sessions_for_jd(jd_id: str) -> List[Dict[str, Any]]:
    with SessionLocal() as db:
        rows = db.scalars(
            select(SessionModel)
            .where(SessionModel.jd_id == jd_id)
            .order_by(SessionModel.created_at.desc())
        ).all()
        return [_session_to_index(r) for r in rows]


# ══════════════════════════════════════════════════════════════════════════════
# Dashboard stats
# ══════════════════════════════════════════════════════════════════════════════

def get_stats() -> Dict[str, Any]:
    with SessionLocal() as db:
        total_sessions   = db.scalar(select(func.count(SessionModel.session_id))) or 0
        total_candidates = db.scalar(select(func.count(CandidateModel.candidate_id))) or 0
        avg_score        = db.scalar(select(func.avg(CandidateModel.overall_score))) or 0.0

        current_month = datetime.now(timezone.utc).strftime("%Y-%m")
        sessions_this_month = db.scalar(
            select(func.count(SessionModel.session_id))
            .where(SessionModel.created_at.like(f"{current_month}%"))
        ) or 0

        # Score distribution
        candidates = db.scalars(select(CandidateModel.overall_score)).all()
        dist = {"strong": 0, "good": 0, "partial": 0, "poor": 0}
        for score in candidates:
            if score >= 80:   dist["strong"] += 1
            elif score >= 60: dist["good"]   += 1
            elif score >= 40: dist["partial"] += 1
            else:             dist["poor"]   += 1

        # Top missing skills across all candidates
        missing_counts: Dict[str, int] = {}
        for row_text in db.scalars(select(CandidateModel.missing_skills)).all():
            for skill in (_p(row_text) or []):
                missing_counts[skill] = missing_counts.get(skill, 0) + 1

        top_missing = [
            {"skill": k, "count": v}
            for k, v in sorted(missing_counts.items(), key=lambda x: x[1], reverse=True)[:10]
        ]

        return {
            "total_sessions":     total_sessions,
            "total_candidates":   total_candidates,
            "avg_score":          round(avg_score, 1),
            "sessions_this_month": sessions_this_month,
            "score_distribution": dist,
            "top_missing_skills": top_missing,
        }
