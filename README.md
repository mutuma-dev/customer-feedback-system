# Company X Feedback System (Devthon)

```
devthon-feedback/
├── backend/    FastAPI + PostgreSQL + Alembic     -> http://localhost:8000   (backend/README.md)
├── frontend/   Next.js 16 (React 19, TypeScript)  -> http://localhost:3000   (frontend/README.md)
├── docker-compose.yml        optional: run everything in containers
└── .github/workflows/ci.yml  the pipeline (see below)
```

Tests live next to the code they test (`test_*.py` in each backend feature folder, `*.test.ts(x)` beside each frontend file).

## Run it

```bash
# 1. Backend (needs your local PostgreSQL and an empty database called "feedback")
cd backend
psql -U postgres -c "CREATE DATABASE feedback;"
python -m venv .venv && source .venv/bin/activate        # Windows: .venv\Scripts\Activate.ps1
pip install -r requirements.txt
cp .env.example .env      # then fill in your values (or keep the .env you already have)
alembic upgrade head && python -m app.seed
uvicorn app.main:app --reload --port 8000

# 2. Frontend (new terminal)
cd frontend
cp .env.local.example .env.local
npm install && npm run dev
```
Survey http://localhost:3000 · Dashboard http://localhost:3000/dashboard · API docs http://localhost:8000/docs

## Tests

```bash
cd backend  && pip install -r requirements-dev.txt && pytest -q    # 62 tests
cd frontend && npm test                                            # 73 tests
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
