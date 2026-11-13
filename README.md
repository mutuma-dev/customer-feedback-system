# Company X Feedback System (Devthon)

```
devthon-feedback/
├── backend/    FastAPI + PostgreSQL + Alembic   -> http://localhost:8000  (backend/README.md)
├── frontend/   Next.js 16 (React 19, TypeScript) -> http://localhost:3000  (frontend/README.md)
├── docker-compose.yml        optional: run everything in containers
└── .github/workflows/ci.yml  ONE pipeline: lint, test, build, scan, migrate, staging, production
```

Tests live next to the code they test (`test_*.py` in each backend feature folder, `*.test.ts(x)` beside each frontend file).

## Run it

```bash
# 1. Backend (needs your local PostgreSQL and an empty database called "feedback")
cd backend
psql -U postgres -c "CREATE DATABASE feedback;"
python -m venv .venv && source .venv/bin/activate     # Windows: .venv\Scripts\Activate.ps1
pip install -r requirements.txt
#   backend/.env is already filled in (postgres / 0000). Edit it if your login differs.
alembic upgrade head && python -m app.seed
uvicorn app.main:app --reload --port 8000

# 2. Frontend (new terminal)
cd frontend
npm install && npm run dev
```

Survey: http://localhost:3000 · Dashboard: http://localhost:3000/dashboard · API docs: http://localhost:8000/docs

## Run the tests

```bash
cd backend  && pip install -r requirements-dev.txt && pytest -q     # 61 tests
cd frontend && npm test                                             # 32 tests
```
