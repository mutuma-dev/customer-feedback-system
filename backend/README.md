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
| Tests | `pytest`, 62 tests, no PostgreSQL or internet needed. Test files sit **inside each feature folder** |

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

Check http://localhost:8000/api/health and browse http://localhost:8000/docs (interactive docs).

* The app reads **`.env`** (not `.env.example`). Restart uvicorn after editing it.
* `requirements.txt` holds exact versions (a `pip freeze`), so everyone installs the same libraries.

---

## 2. Structure, for someone who knows Spring Boot

The code is grouped by **feature** (like Spring packages). Each feature has the layers you know:

| Spring Boot | Here | What it is |
|---|---|---|
| `@RestController` | `router.py` | URLs, HTTP in/out. No business rules |
| `@Service` | `service.py` | Business logic and the transaction (`db.commit()`) |
| `JpaRepository` | `repository.py` | Database queries only |
| `@Entity` | `models.py` | Python classes mapped to tables |
| DTO + `@Valid` | `schemas.py` | Shape of requests/responses; bad input gets a 422 automatically |
| `application.properties` | `core/config.py` + `.env` | Settings |
| DataSource / EntityManager | `core/database.py` | Connection pool and sessions |
| `@Autowired` | `db: DbSession` | FastAPI injects a database session into a route |
| `@ControllerAdvice` | `core/errors.py` | `NotFoundError` becomes HTTP 404 |
| Flyway / Liquibase | `alembic/` | Versioned schema migrations |
| `@Async` | `BackgroundTasks` | Work that runs after the response is sent |
| JUnit + MockMvc | `pytest` + `TestClient` | Tests |
| `pom.xml` | `requirements.txt` | Dependencies |

```
backend/
├── app/
│   ├── main.py                 assembles the app: CORS, error handler, all routers
│   ├── seed.py                 demo data                          (test_seed.py)
│   ├── core/                   config.py  database.py  clock.py  errors.py  health.py
│   ├── feedback/               the survey: models, schemas, scoring, repository, service, router
│   ├── alerts/                 unhappy customers: models, schemas, repository, service, router,
│   │                           notifications.py (email + SMS), ai.py (reply drafts)
│   ├── dashboard/              numbers for the dashboard: schemas, repository, service, router,
│   │                           analytics.py (trend projection)
│   └── sms/                    painters on basic phones: parser, client, messages, service, router
├── alembic/                    migrations
├── conftest.py                 shared test setup
└── pytest.ini  ruff.toml  Dockerfile  requirements*.txt  .env.example
```
(each `test_*.py` sits beside the file it tests, e.g. `app/sms/test_parser.py`)

### What happens when a customer submits the survey
```
POST /api/feedback
  feedback/router.py    FastAPI checks the JSON against FeedbackIn (422 if invalid)
  feedback/service.py   find or create the customer (same email, else same phone)
                        classify() -> mean + verdict                     (scoring.py)
                        save the response                                 (repository.py)
                        if detractor: alerts/service.py creates an Alert
                        db.commit()   <- all saved together or not at all
  feedback/router.py    queues notifications.dispatch_alert in the BACKGROUND
                        replies 201 {id, mean, category, alert_created}   <- the customer is done
  (afterwards)          alerts/notifications.py emails the care rep, texts them if a phone is set,
                        and records email_sent / sms_sent on the alert
```

### When are emails and SMS sent?
| What | When | Triggered by |
|---|---|---|
| Alert **email** to the care rep | a detractor is saved (web form **or** SMS reply) | the backend, automatically |
| Alert **SMS** to the care rep | same moment, only if `CARE_REP_PHONE` is set | the backend, automatically |
| **Invitation SMS** to a painter | only when `POST /api/sms/invite` is called | a person/system (not automatic) |
| **Thank-you / help SMS** to a painter | right after their reply arrives | the backend, automatically |
| **AI call** | only when the care rep clicks "Write reply" | the dashboard |

---

## 3. Database

```
customers 1 ──────< responses 1 ────── 0..1 alerts
```
* **customers**: id, name, email (unique, optional), phone (unique, optional), kind (`buyer`/`painter`), created_at
* **responses**: id, customer_id, product_rating, care_rating, happy_rating (each `CHECK 1..5`), mean `numeric(4,2)`, category, source (`web`/`sms`), created_at. Indexed on customer, category and date
* **alerts**: id, response_id (**unique**, one alert per response), is_read, email_sent, sms_sent, draft_reply, created_at

`is_read` is what the dashboard bell counts: the badge number = alerts where `is_read` is false.

Demo data (`python -m app.seed`) is the same every time: 15 days, 3 to 7 customers a day (about 70 responses), about 30% painters (source `sms`), satisfaction rising slowly so the trend climbs. Every detractor gets an alert; alerts from the last 5 days start **unread**, so the bell shows a number straight away.

---

## 4. API: 12 endpoints

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
| 11 | `POST /api/sms/invite` | Send the "Rate us 1-5… Reply e.g. 4 5 4" SMS |
| 12 | `POST /api/sms/incoming` | Africa's Talking webhook (form: `from`, `text`) |

Errors: invalid input gives **422** with details; an unknown id gives **404** `{"detail": "Alert not found"}`.

---

## 5. Settings (`.env`) and free services

| Variable | Meaning |
|---|---|
| `DATABASE_URL` | `postgresql+psycopg://USER:PASSWORD@localhost:5432/feedback` (`@` in a password is written `%40`) |
| `FRONTEND_ORIGIN` | Allowed website addresses (CORS), comma separated, exact (no trailing slash) |
| `CARE_REP_EMAIL` | **A real inbox** that receives alert emails |
| `CARE_REP_PHONE` | E.164 number for the alert SMS. Empty = no SMS |
| `SMTP_HOST/PORT/USER/PASSWORD/FROM` | Email server. Empty host = emails are only logged |
| `AT_USERNAME`, `AT_API_KEY`, `AT_SENDER_ID` | Africa's Talking |
| `AI_API_KEY`, `AI_BASE_URL`, `AI_MODEL`, `AI_TIMEOUT_SECONDS` | AI provider (any OpenAI-compatible service) |

With only `DATABASE_URL` set, everything still works: emails/SMS are printed in the terminal and replies use a template.

* **Groq AI (free):** console.groq.com, create an API key, set `AI_API_KEY`. Keep `AI_BASE_URL=https://api.groq.com/openai/v1` and `AI_MODEL=llama-3.3-70b-versatile`.
* **Gmail email (free):** turn on 2-Step Verification, create an app password at myaccount.google.com/apppasswords, then `SMTP_HOST=smtp.gmail.com`, `SMTP_PORT=587`, `SMTP_USER` / `SMTP_FROM` = your Gmail, `SMTP_PASSWORD` = the app password. Gmail usually shows your own address as the sender whatever `SMTP_FROM` says.
* **Africa's Talking sandbox:** create an API key in the Sandbox app, `AT_USERNAME=sandbox`. Messages appear in their simulator. For painter replies expose the API with `ngrok http 8000` and set the callback to `https://<ngrok-host>/api/sms/incoming`, or call `/api/sms/incoming` yourself from `/docs`.
* **Never commit `.env`.** It is in `.gitignore`. Revoke any key you pasted in public places.

---

## 6. Tests

```bash
pytest -q                 # all 62 tests (about 1 second)
pytest app/sms -q         # only one feature
ruff check . && ruff format --check .
```
* `conftest.py` gives every test a fresh in-memory SQLite database and replaces sending with lists, so tests never need PostgreSQL, the internet or keys.
* It also **blanks your real keys while tests run**, so running `pytest` can never send a real email or SMS or call Groq.
* Covered: scoring and its boundaries, validation (422), 404s, repeat customers, SMS parsing and replies, alert creation and the read / read-all endpoints, delivery flags, SMTP call order, AI success/failure/empty/template fallback (and that the surname is never sent to the AI), the projection maths, pagination and seeding.
* Test files are excluded from the Docker image (`.dockerignore`).

## 7. Docker

`Dockerfile`: start from `python:3.14-slim`; copy `requirements.txt` first and install (cached between builds); copy the code; on start run `alembic upgrade head` then `uvicorn`. `.dockerignore` keeps `.env`, tests and caches out of the image.

## 8. Troubleshooting

| Symptom | Fix |
|---|---|
| `password authentication failed` | wrong user/password in `.env` |
| `database "feedback" does not exist` | `psql -U postgres -c "CREATE DATABASE feedback;"` |
| `relation "customers" does not exist` (and a browser "CORS error") | run `alembic upgrade head`; a crashing API sends no CORS header, so the browser mislabels it |
| Real CORS error | `FRONTEND_ORIGIN` must equal the browser address exactly; restart after editing |
| `ModuleNotFoundError: app` | run commands from inside `backend/` |
| No email arrives | `CARE_REP_EMAIL` must be a real inbox; check the terminal log |
| Draft says "Template draft" | `AI_API_KEY` empty/wrong, or the call failed (see the terminal) |

## 9. Limitations

* Dashboard endpoints have **no login**; add authentication for care staff.
* `/api/sms/incoming` is open; verify requests really come from Africa's Talking.
* Alerts run as background tasks: a restart in the middle could drop one. A real queue (with retries) fixes that.
* `GET /api/alerts` returns the newest 50, so the bell can undercount if more than 50 are unread.
* The staging/production jobs in `.github/workflows/ci.yml` are placeholders for your hosting provider.
