"""
SQLAlchemy database setup and models.

Supports any SQLAlchemy-compatible database:
  SQLite    (default) : DATABASE_URL=sqlite:///./data/resume_iq.db
  PostgreSQL          : DATABASE_URL=postgresql://user:pass@localhost/resume_iq
  MySQL               : DATABASE_URL=mysql+pymysql://user:pass@localhost/resume_iq
"""

import os
from dotenv import load_dotenv
load_dotenv()

from sqlalchemy import (
    Column, Float, ForeignKey, Integer, String, Text,
    create_engine, event,
)
from sqlalchemy.orm import DeclarativeBase, Session, relationship, sessionmaker

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./data/resume_iq.db")

# SQLite-specific: enable WAL mode and foreign keys on every connection
_is_sqlite = DATABASE_URL.startswith("sqlite")

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False} if _is_sqlite else {},
    echo=False,
)

if _is_sqlite:
    @event.listens_for(engine, "connect")
    def _sqlite_pragmas(conn, _):
        conn.execute("PRAGMA journal_mode=WAL")
        conn.execute("PRAGMA foreign_keys=ON")

SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)


class Base(DeclarativeBase):
    pass


# ── Models ─────────────────────────────────────────────────────────────────────

class JDModel(Base):
    __tablename__ = "jds"

    jd_id         = Column(String, primary_key=True)
    title         = Column(String, nullable=False)
    text          = Column(Text,   nullable=False)
    created_at    = Column(String, nullable=False)
    session_count = Column(Integer, default=0)
    jd_summary    = Column(Text, nullable=False)   # JSON blob

    sessions = relationship("SessionModel", back_populates="jd")


class SessionModel(Base):
    __tablename__ = "sessions"

    session_id    = Column(String, primary_key=True)
    job_title     = Column(String, nullable=False)
    created_at    = Column(String, nullable=False)
    jd_id         = Column(String, ForeignKey("jds.jd_id", ondelete="SET NULL"), nullable=True)
    jd_summary    = Column(Text, nullable=False)   # JSON blob
    avg_score     = Column(Float,  default=0.0)
    top_candidate = Column(String, nullable=True)

    jd         = relationship("JDModel", back_populates="sessions")
    candidates = relationship(
        "CandidateModel", back_populates="session",
        cascade="all, delete-orphan", order_by="CandidateModel.overall_score.desc()",
    )


class CandidateModel(Base):
    __tablename__ = "candidates"

    candidate_id    = Column(String, primary_key=True)
    session_id      = Column(String, ForeignKey("sessions.session_id", ondelete="CASCADE"), nullable=False)
    filename        = Column(String)
    candidate_name  = Column(String)
    email           = Column(String)
    overall_score   = Column(Float)
    sub_scores      = Column(Text, nullable=False)   # JSON blob
    matched_skills  = Column(Text, nullable=False)   # JSON array
    missing_skills  = Column(Text, nullable=False)   # JSON array
    bonus_skills    = Column(Text, nullable=False)   # JSON array
    years_experience = Column(Float, nullable=True)
    recommendation  = Column(String)
    summary         = Column(Text, nullable=False)   # JSON blob

    session = relationship("SessionModel", back_populates="candidates")


def create_tables() -> None:
    """Create all tables if they don't exist (idempotent)."""
    import pathlib
    if _is_sqlite:
        db_path = DATABASE_URL.replace("sqlite:///", "")
        pathlib.Path(db_path).parent.mkdir(parents=True, exist_ok=True)
    Base.metadata.create_all(bind=engine)


def get_db() -> Session:
    """Dependency-injection helper — yields a session and closes it after use."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
