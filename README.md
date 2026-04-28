# Resume IQ

A recruiter-focused resume screening tool. Paste a job description, upload PDF/DOCX resumes, and get a ranked candidate list with match scores, skill gaps, and sub-score breakdowns — all without AI/LLM calls.

## Stack

| Layer    | Tech |
|----------|------|
| Backend  | Python 3.11 · FastAPI · pdfplumber · python-docx |
| Scoring  | Pure Python keyword matching + weighted scoring |
| Storage  | JSON files in `./data/` |
| Frontend | React 18 · TypeScript · Vite · Tailwind CSS v3 |
| Charts   | Recharts |
| State    | TanStack React Query v5 · Axios |

## Quick Start

### Backend

```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

Open **http://localhost:5173** — the Vite dev server proxies `/api` requests to the FastAPI backend.

## How Scoring Works

| Component | Weight | Description |
|-----------|--------|-------------|
| Skills    | 50%    | Matched required skills ÷ total required skills |
| Experience| 25%    | Candidate years ÷ required years (capped at 100%) |
| Domain    | 15%    | Domain-relevant skills found (3+ = full score) |
| Bonus     | 10%    | Extra skills beyond the JD requirements |

**Recommendation thresholds:**

| Score | Label |
|-------|-------|
| ≥ 80  | Strong Match |
| ≥ 60  | Good Match |
| ≥ 40  | Partial Match |
| < 40  | Poor Match |

## API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| POST   | `/api/analyze` | Upload JD + resumes, returns scored session |
| GET    | `/api/sessions` | List sessions (supports `limit`, `offset`, `search`) |
| GET    | `/api/sessions/{id}` | Get full session detail |
| DELETE | `/api/sessions/{id}` | Delete a session |
| GET    | `/api/dashboard/stats` | Aggregate stats |

## Project Structure

```
resume-iq/
├── backend/
│   ├── main.py                  # FastAPI app entry point
│   ├── routers/
│   │   ├── analyze.py           # POST /api/analyze
│   │   ├── sessions.py          # GET/DELETE /api/sessions
│   │   └── dashboard.py         # GET /api/dashboard/stats
│   ├── services/
│   │   ├── parser.py            # PDF/DOCX text extraction
│   │   ├── scorer.py            # Scoring engine
│   │   ├── db.py                # JSON file persistence
│   │   └── skills_vocab.py      # 500+ skill vocabulary set
│   ├── models/schemas.py        # Pydantic models
│   ├── data/                    # Runtime data (auto-created)
│   │   ├── index.json
│   │   └── sessions/
│   └── requirements.txt
└── frontend/
    └── src/
        ├── pages/               # AnalyzePage, Dashboard, History, SessionDetail
        ├── components/          # CandidateCard, ScoreCircle, SkillBadge, etc.
        ├── hooks/               # useAnalyze, useSessions, useDashboard
        ├── api/                 # Axios client + typed endpoints
        └── types/               # TypeScript interfaces
```

## Constraints

- Max 10 resumes per session
- Supported formats: PDF and DOCX only
- Scanned/image-only PDFs will return a 422 error
- All data stored locally in `backend/data/` as JSON files
