from typing import Optional

from fastapi import APIRouter, HTTPException, Query

from services import db

router = APIRouter()


@router.get("/sessions")
def list_sessions(
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    search: Optional[str] = Query(None),
):
    return db.list_sessions(limit=limit, offset=offset, search=search)


@router.get("/sessions/{session_id}")
def get_session(session_id: str):
    session = db.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail=f"Session '{session_id}' not found.")
    return session


@router.delete("/sessions/{session_id}")
def delete_session(session_id: str):
    if not db.delete_session(session_id):
        raise HTTPException(status_code=404, detail=f"Session '{session_id}' not found.")
    return {"message": "Session deleted successfully.", "session_id": session_id}
