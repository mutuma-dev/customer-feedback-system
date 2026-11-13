# Company X Feedback API (backend)

FastAPI + PostgreSQL service that receives customer feedback, scores it, raises alerts for unhappy
customers, emails/texts the care team, drafts AI replies and serves the numbers the dashboard needs.

| | |
|---|---|
| Language / framework | Python 3.14 (3.12+ works), **FastAPI** |
| Database | **PostgreSQL**, database `feedback`, via **SQLAlchemy 2** + **psycopg 3** |
| Migrations | **Alembic** (`alembic/versions/0001_initial.py`) |
| Email | Any SMTP server (Gmail app password works, free) |
| SMS | **Africa's Talking** sandbox |
| AI (bonus) | Reply drafts through any OpenAI-compatible provider (Groq, free) |
| Port | **8000** |
| Tests | `pytest`, 70 tests, no PostgreSQL or internet needed. Test files sit **inside each feature folder** |

Every code file is commented to explain what it does and why. Start reading at `app/main.py`.

---

## 1. Run it

You need Python and your local PostgreSQL.

```bash
cd backend
psql -U postgres -c "CREATE DATABASE feedback;"      # once; creates an empty database

python -m venv .venv                                   # a private box for this project's libraries
source .venv/bin/activate                              # Windows PowerShell: .venv\Scripts\Activate.ps1
pip install -r requirements.txt                        # (use requirements-dev.txt to also get pytest + ruff)

cp .env.example .env                                   # then edit .env: DATABASE_URL, keys ...
alembic upgrade head                                   # creates the tables
python -m app.seed                                     # optional demo data
uvicorn app.main:app --reload --port 8000              # start the API
```


## 2. API: 12 endpoints

| # | Method and path | Purpose |
|---|---|---|
| 1 | `GET /api/health` | API and database alive |
| 2 | `POST /api/feedback` | Submit a survey. **201** `{id, mean, category, alert_created}` |
| 3 | `GET /api/stats` | Total, the three groups, averages |
| 4 | `GET /api/trend?days=30` | Daily means + 7-day projection |
| 5 | `GET /api/responses?limit=50&offset=0` | Newest first, with customer |
| 6 | `GET /api/responses/{id}` | One response (404 if missing) |
| 7 | `GET /api/alerts?unread_only=false` | Newest 50 alerts |
| 8 | `POST /api/alerts/{id}/read` | Mark one alert as read |
| 9 | `POST /api/alerts/read-all` | Mark every alert as read, returns `{updated: n}` |
| 10 | `POST /api/alerts/{id}/draft-reply` | AI/template draft. Sends nothing |
| 11 | `POST /api/sms/invite` | Send the "Rate us 1-5… Reply e.g. 4 5 4" SMS. Replies `{sent, detail}`: `detail` is Africa's Talking's real answer |
| 12 | `POST /api/sms/incoming` | Africa's Talking webhook (form: `from`, `text`) |

Errors: invalid input gives **422** with details; an unknown id gives **404** `{"detail": "Alert not found"}`.

---
