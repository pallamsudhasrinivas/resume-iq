from fastapi import APIRouter

from services import db

router = APIRouter()


@router.get("/dashboard/stats")
def dashboard_stats():
    return db.get_stats()
