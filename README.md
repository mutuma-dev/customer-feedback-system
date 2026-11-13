# Company X Feedback System (Devthon)

```
devthon-feedback/
├── backend/    FastAPI + PostgreSQL + Alembic     -> http://localhost:8000   (backend/README.md)
├── frontend/   Next.js 16 (React 19, TypeScript)  -> http://localhost:3000   (frontend/README.md)
├── docker-compose.yml        optional: run everything in containers
└── .github/workflows/ci.yml  the pipeline 
```


## Run it

```bash
# 1. Backend need postgre database feedback ready
cd backend
psql -U postgres -c "CREATE DATABASE feedback;"
python3 -m venv .venv && source .venv/bin/activate        # Windows: .venv\Scripts\Activate.ps1
pip install -r requirements.txt
alembic upgrade head && python -m app.seed
uvicorn app.main:app --reload --port 8000

# 2. Frontend (new terminal)
cd frontend
cp .env.local.example .env.local
npm install && npm run dev
```

## Tests

```bash
cd backend  && pip install -r requirements-dev.txt && pytest -q   
cd frontend && npm test                                          
```

## The pipeline (`.github/workflows/ci.yml`)

One file, six jobs. It runs on every push / pull request, and the last three only after a push to `main`.

| Job | Runs | What it does |
|---|---|---|
| `backend` | always | install, Ruff lint, create the tables on a real PostgreSQL (tests the migration), pytest |
| `frontend` | always | `npm ci`, ESLint, Vitest, production build |
| `docker` | after both pass | builds the two Docker images |
| `scan` | `main` only | gitleaks (leaked secrets) + `pip-audit` + `npm audit` (vulnerable libraries) |
| `staging` | after `scan` | placeholder: put your deploy command here |
| `production` | after `staging` | placeholder; add "Required reviewers" to the `production` environment for manual approval |

A red job stops every job that depends on it, so broken code does not ship.
