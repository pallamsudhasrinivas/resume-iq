import uuid
from datetime import datetime, timezone

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from services import db, scorer

router = APIRouter()


class SaveJDRequest(BaseModel):
    title: str
    text: str


@router.post("/jds")
def save_jd(req: SaveJDRequest):
    if not req.text.strip():
        raise HTTPException(status_code=400, detail="Job description text cannot be empty.")
    if not req.title.strip():
        raise HTTPException(status_code=400, detail="Title cannot be empty.")

    jd_data = scorer.parse_jd(req.text)
    jd = {
        "jd_id": str(uuid.uuid4()),
        "title": req.title.strip(),
        "text": req.text,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "jd_summary": {
            "required_skills": jd_data["required_skills"],
            "years_required": jd_data.get("years_required"),
            "role_level": jd_data.get("role_level"),
            "domain": jd_data.get("domain"),
        },
        "session_count": 0,
    }
    db.save_jd(jd)
    return jd


@router.get("/jds")
def list_jds(limit: int = 50, offset: int = 0):
    return db.list_jds(limit=limit, offset=offset)


@router.get("/jds/{jd_id}")
def get_jd(jd_id: str):
    jd = db.get_jd(jd_id)
    if not jd:
        raise HTTPException(status_code=404, detail="Job description not found.")
    sessions = db.get_sessions_for_jd(jd_id)
    return {**jd, "sessions": sessions}


@router.get("/jds/{jd_id}/candidates")
def get_jd_candidates(jd_id: str):
    if not db.get_jd(jd_id):
        raise HTTPException(status_code=404, detail="Job description not found.")
    session_metas = db.get_sessions_for_jd(jd_id)
    candidates = []
    for meta in session_metas:
        session = db.get_session(meta["session_id"])
        if not session:
            continue
        for c in session.get("candidates", []):
            candidates.append({
                **c,
                "session_id": session["session_id"],
                "session_date": session["created_at"],
            })
    candidates.sort(key=lambda c: c["overall_score"], reverse=True)
    return {"candidates": candidates, "total": len(candidates)}


@router.delete("/jds/{jd_id}")
def delete_jd(jd_id: str):
    if not db.delete_jd(jd_id):
        raise HTTPException(status_code=404, detail="Job description not found.")
    return {"ok": True}
