# Company X Feedback System (Devthon)


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
