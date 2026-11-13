# Company X Feedback System (Devthon)

devthon-feedback/
├── backend/    FastAPI + PostgreSQL + Alembic   -> http://localhost:8000  (backend/README.md)
├── frontend/   Next.js 16 (React 19, TypeScript) -> http://localhost:3000  (frontend/README.md)
├── docker-compose.yml        run everything in containers
└── .github/workflows/ci.yml  ONE pipeline: lint, test, build, scan, migrate, staging, production
```

## Running app

```bash
# 1. Backend (needs local PostgreSQL and an empty database called "feedback")
cd backend
psql -U postgres -c "CREATE DATABASE feedback;"
python -m venv .venv && source .venv/bin/activate 
pip install -r requirements.txt
alembic upgrade head && python -m app.seed
uvicorn app.main:app --reload --port 8000

# 2. Frontend
cd frontend
npm install && npm run dev


Survey: http://localhost:3000 · Dashboard: http://localhost:3000/dashboard · API docs: http://localhost:8000/docs

## Run the tests

```bash
cd backend  && pip install -r requirements-dev.txt && pytest -q 
cd frontend && npm test                                        
```
