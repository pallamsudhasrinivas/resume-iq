import logging
import os
from typing import List, Optional

from fastapi import APIRouter, File, Form, HTTPException, UploadFile

from services import db, scorer

logger = logging.getLogger(__name__)

router = APIRouter()

MAX_RESUMES = int(os.getenv("MAX_RESUMES", "10"))
ALLOWED_EXTENSIONS = {"pdf", "docx", "doc", "rtf", "txt"}


@router.post("/analyze")
async def analyze(
    resumes: List[UploadFile] = File(...),
    job_description: Optional[str] = Form(None),
    jd_id: Optional[str] = Form(None),
):
    # Resolve JD text — either from the saved library or directly pasted
    jd_text: str = ""
    resolved_jd_id: Optional[str] = None

    if jd_id:
        saved = db.get_jd(jd_id)
        if not saved:
            raise HTTPException(status_code=404, detail="Saved job description not found.")
        jd_text = saved["text"]
        resolved_jd_id = jd_id
    elif job_description and job_description.strip():
        jd_text = job_description.strip()
    else:
        raise HTTPException(
            status_code=400,
            detail="Provide either a job_description or a jd_id.",
        )

    if not resumes:
        raise HTTPException(status_code=400, detail="At least one resume file is required.")
    if len(resumes) > MAX_RESUMES:
        raise HTTPException(
            status_code=400,
            detail=f"Maximum {MAX_RESUMES} resumes allowed per session.",
        )

    resume_data = []
    for upload in resumes:
        filename = upload.filename or "unknown"
        ext = filename.rsplit(".", 1)[-1].lower() if "." in filename else ""
        if ext not in ALLOWED_EXTENSIONS:
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported file type for '{filename}'. Only PDF and DOCX are supported.",
            )
        content = await upload.read()
        if len(content) == 0:
            raise HTTPException(
                status_code=400,
                detail=f"'{filename}' appears to be empty (0 bytes).",
            )
        resume_data.append((filename, content))

    try:
        session = scorer.run_session(jd_text, resume_data)
    except ValueError as exc:
        logger.warning("Parse/score error: %s", exc)
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    except Exception as exc:
        logger.exception("Unexpected error during analysis: %s", exc)
        raise HTTPException(
            status_code=500,
            detail=f"An unexpected error occurred while processing the files: {exc}",
        ) from exc

    if resolved_jd_id:
        session["jd_id"] = resolved_jd_id

    db.save_session(session)
    return session
