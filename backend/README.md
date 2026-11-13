# Company X Feedback API (backend)

FastAPI + PostgreSQL service that receives customer feedback, scores it, raises alerts for unhappy
customers, sends email/SMS, drafts AI replies and serves the numbers the dashboard needs.

| | |
|---|---|
| Language / framework | Python 3.12 to 3.14, **FastAPI** |
| Database | **PostgreSQL** (database `feedback`) via **SQLAlchemy 2** + **psycopg 3** |
| Migrations | **Alembic** (`alembic/versions/0001_initial.py`) |
| SMS | **Africa's Talking** sandbox |
| Email | Any SMTP server (Gmail app password works, free) |
| AI (bonus) | Smart reply drafts through any OpenAI-compatible provider (Groq free tier by default) |
| Port | **8000** |
| Tests | `pytest`, 61 tests, no PostgreSQL needed. Test files sit **inside each feature folder** |

The frontend (`../frontend`, port **3000**) calls this API. Its address is `NEXT_PUBLIC_API_URL` in the frontend's `.env.local`.

---

## 1. Quick start

You need Python 3.12 or newer and your local PostgreSQL.

```bash
cd backend

# 1. Create the empty database once (use your own postgres user)
psql -U postgres -c "CREATE DATABASE feedback;"

# 2. Virtual environment + libraries
python3 -m venv .venv
source .venv/bin/activate            # Windows PowerShell: .venv\Scripts\Activate.ps1
pip install -r requirements.txt      # add -dev to also get pytest and ruff: requirements-dev.txt

# 3. Settings: the app reads ".env" (NOT .env.example). Edit DATABASE_URL in it.
#    .env.example is only a template to copy from: cp .env.example .env

# 4. Create the tables
alembic upgrade head


# 6. Run
uvicorn app.main:app --reload --port 8000
```

Check http://localhost:8000/api/health and browse http://localhost:8000/docs (interactive API docs).

Restart uvicorn after you edit `.env` (auto-reload watches Python files, not `.env`).

---

## 2. Project structure, for someone who knows Spring Boot

The code is grouped by **feature** (like Spring packages `feedback`, `alerts`, `dashboard`, `sms`).
Inside each feature the layers are the same ones you know from Spring:

| Spring Boot | This project | What it is |
|---|---|---|
| `@RestController` | `router.py` | URLs, reads the request, returns the response. No business rules |
| `@Service` | `service.py` | Business logic and the transaction (`db.commit()`) |
| `JpaRepository` | `repository.py` | Database queries only |
| `@Entity` | `models.py` | Python classes mapped to tables |
| DTOs + `@Valid` | `schemas.py` | Request/response shapes, validated automatically (422 on bad input) |
| `application.properties` | `core/config.py` + `.env` | Settings |
| DataSource / EntityManager | `core/database.py` | Connection pool and sessions |
| `@Autowired` | `Depends(get_db)` / `DbSession` | Dependency injection: FastAPI hands the route a database session |
| `@ControllerAdvice` | `core/errors.py` | `NotFoundError` becomes HTTP 404 |
| Flyway / Liquibase | `alembic/` | Versioned schema migrations |
| `@Async` / events | `BackgroundTasks` | Work that runs after the response is sent |
| `pom.xml` | `requirements.txt` | Dependencies |
| `@SpringBootApplication` | `app/main.py` | App assembly. Started by `uvicorn app.main:app` |
| JUnit + MockMvc + Mockito | `pytest` + `TestClient` + `monkeypatch` | Tests |

```
backend/
├── app/
│   ├── main.py                 assemble the app: CORS, error handler, all routers
│   ├── seed.py                 demo data            (test_seed.py beside it)
│   ├── core/                   shared plumbing
│   │   ├── config.py           settings            (test_config.py)
│   │   ├── database.py         engine, sessions, DbSession
│   │   ├── clock.py            utcnow()
│   │   ├── errors.py           NotFoundError -> 404
│   │   └── health.py           GET /api/health     (test_health.py)
│   ├── feedback/               the survey
│   │   ├── models.py           entities Customer, Response
│   │   ├── schemas.py          DTOs FeedbackIn / FeedbackOut / ResponseOut
│   │   ├── scoring.py          mean + detractor/passive/promoter   (test_scoring.py)
│   │   ├── repository.py  service.py  router.py                    (test_router.py)
│   ├── alerts/                 unhappy customers
│   │   ├── models.py           entity Alert
│   │   ├── schemas.py  repository.py  service.py  router.py        (test_router.py)
│   │   ├── notifications.py    email + SMS to the care rep         (test_notifications.py)
│   │   └── ai.py               AI reply drafts + template          (test_ai.py)
│   ├── dashboard/              numbers for the dashboard
│   │   ├── schemas.py  repository.py  service.py  router.py        (test_router.py)
│   │   └── analytics.py        trend projection                    (test_analytics.py)
│   └── sms/                    painters on feature phones
│       ├── parser.py           reads "4 5 4"                       (test_parser.py)
│       ├── client.py           sends via Africa's Talking
│       ├── messages.py         the SMS texts
│       ├── schemas.py  service.py  router.py                       (test_router.py)
├── alembic/                    migrations
├── conftest.py                 shared test fixtures
├── pytest.ini  ruff.toml  Dockerfile  requirements*.txt  .env  .env.example
```

### What happens when the survey is submitted (request lifecycle)

```
POST /api/feedback
  feedback/router.py     FastAPI validates the JSON against FeedbackIn (400/422 if invalid)
  feedback/service.py    find or create the Customer (same email, else same phone)
                         classify(ratings) -> mean + category          (scoring.py)
                         save the Response                              (repository.py)
                         if detractor: alerts/service.py creates an Alert
                         db.commit()  <- customer, response and alert saved together
  feedback/router.py     queues notifications.dispatch_alert as a BACKGROUND task
                         returns 201 {id, mean, category, alert_created}   <- customer is done
  (after the response)   alerts/notifications.py emails the care rep and optionally sends an SMS
                         then stores email_sent / sms_sent on the alert
```

---

## 3. The database

PostgreSQL, database `feedback`, three tables created by Alembic.

```
customers 1 ──────< responses 1 ────── 0..1 alerts
```

**customers**: id, name, email (unique, nullable), phone (unique, nullable, `+254...`), kind (`buyer`/`painter`), created_at

**responses**: id, customer_id (FK), product_rating, care_rating, happy_rating (each `CHECK 1..5`), mean `numeric(4,2)`, category (`detractor`/`passive`/`promoter`, indexed), source (`web`/`sms`), created_at (indexed)

**alerts**: id, response_id (FK, **unique**: one alert per response), is_read, email_sent, sms_sent, draft_reply, created_at

Inspect: `psql -U postgres -d feedback -c "SELECT * FROM responses ORDER BY id DESC LIMIT 5;"`

### Demo data (`python -m app.seed`)

Deterministic (`Random(42)`): 15 days, 3 to 7 customers per day, about 70 responses. About 30% are painters (source `sms`), the rest buyers (source `web`). Ratings come from a bell curve whose centre rises from 3.2 to about 3.8, so the dashboard trend visibly climbs. Every detractor gets an alert; alerts older than 2 days are marked read. Sample rows:

```
customers                                                        responses
id name            email                           phone         id cust p c h mean category  source
1  Amina Achieng   amina.achieng.140@example.com   +254728728463 1  1    3 2 4 3.00 passive   sms
2  Amina Otieno    amina.otieno.141@example.com    +254741227216 2  2    3 3 3 3.00 passive   sms
3  Irene Mutua     irene.mutua.142@example.com     +254789089901 3  3    3 5 3 3.67 promoter  sms
5  ...                                                           5  5    1 3 2 2.00 detractor web   -> alert #1
```

---

## 4. API reference: 11 endpoints

Base URL `http://localhost:8000`. All paths start with `/api`.

| # | Method and path | Feature | Purpose |
|---|---|---|---|
| 1 | `GET /api/health` | core | API and database alive |
| 2 | `POST /api/feedback` | feedback | Submit survey. **201** |
| 3 | `GET /api/stats` | dashboard | Totals, split, averages |
| 4 | `GET /api/trend?days=30` | dashboard | Daily means + 7-day projection |
| 5 | `GET /api/responses?limit=50&offset=0` | dashboard | Newest first, with customer |
| 6 | `GET /api/responses/{id}` | dashboard | One response (drill-down), 404 if missing |
| 7 | `GET /api/alerts?unread_only=false` | alerts | Detractor alerts |
| 8 | `POST /api/alerts/{id}/read` | alerts | Mark handled |
| 9 | `POST /api/alerts/{id}/draft-reply` | alerts | AI/template draft. Sends nothing |
| 10 | `POST /api/sms/invite` | sms | Send the "Rate us 1-5… Reply e.g. 4 5 4" SMS |
| 11 | `POST /api/sms/incoming` | sms | Africa's Talking webhook (form-encoded) |

Examples:

```
POST /api/feedback
{ "name":"Amina Otieno", "email":"amina@example.com", "phone":"+254712345678", "kind":"buyer",
  "product_rating":2, "care_rating":3, "happy_rating":2 }
-> 201 { "id":1, "mean":2.33, "category":"detractor", "alert_created":true }

GET /api/stats
-> { "total":69, "detractors":10, "passives":13, "promoters":46,
     "avg_product":3.3, "avg_care":3.59, "avg_happy":3.29, "avg_mean":3.4 }

GET /api/trend?days=30
-> { "points":[{"date":"2026-10-29","mean":3.22,"count":3}, ...],
     "projection":[{"date":"2026-11-13","mean":3.9,"count":0}, ...] }

POST /api/sms/incoming     (form fields, not JSON)   from=+254799999999&text=1 1 2
-> { "status":"saved" }      (or {"status":"ignored"} if the text is not three digits 1-5)
```

Errors: invalid input gives **422** with details; unknown id gives **404** `{"detail":"Alert not found"}`.

### Schemas (DTOs)

| Schema | Fields |
|---|---|
| `FeedbackIn` | name (1-120), email (valid), phone?, kind `buyer`/`painter`, product_rating, care_rating, happy_rating (1-5) |
| `FeedbackOut` | id, mean, category, alert_created |
| `ResponseOut` | id, customer{id,name,email,phone,kind}, three ratings, mean, category, source, created_at |
| `AlertOut` | id, is_read, email_sent, sms_sent, draft_reply, created_at, response{ResponseOut} |
| `DraftOut` | draft, ai_used |
| `StatsOut` | total, detractors, passives, promoters, avg_product, avg_care, avg_happy, avg_mean |
| `TrendOut` | points[{date,mean,count}], projection[{date,mean}] |
| `SmsInviteIn / Out` | phone (E.164) / sent |

---

## 5. Settings (`.env`) and free services

The app reads **`.env`** only. **`.env.example`** is a copy-from template.

| Variable | Meaning |
|---|---|
| `DATABASE_URL` | `postgresql+psycopg://USER:PASSWORD@localhost:5432/feedback` (URL-encode special characters: `@` is `%40`) |
| `FRONTEND_ORIGIN` | Allowed browser origins (CORS), comma separated, exact (no trailing slash) |
| `CARE_REP_EMAIL` | Who receives detractor emails |
| `CARE_REP_PHONE` | E.164 number for the SMS alert. Empty = no SMS alert |
| `SMTP_HOST/PORT/USER/PASSWORD/FROM` | Email server. Empty host = emails are only logged |
| `AT_USERNAME`, `AT_API_KEY`, `AT_SENDER_ID` | Africa's Talking |
| `AI_API_KEY`, `AI_BASE_URL`, `AI_MODEL`, `AI_TIMEOUT_SECONDS` | AI provider (OpenAI-compatible) |

Everything optional degrades gracefully: with only `DATABASE_URL` set the whole app works. Emails/SMS are written to the terminal and replies use a template.

### Free AI: Groq (recommended)
1. Go to **console.groq.com**, sign up (email, Google or GitHub). No credit card is needed for the free tier.
2. Open **API Keys** (console.groq.com/keys), click **Create API Key**, copy it now (shown once).
3. In `.env`:
   ```
   AI_API_KEY=gsk_...your key...
   AI_BASE_URL=https://api.groq.com/openai/v1
   AI_MODEL=llama-3.3-70b-versatile
   ```
4. Restart the backend. On the dashboard, "Draft reply" now says **AI draft**.

Alternative, Google Gemini: create a key at **aistudio.google.com/apikey**, then
`AI_BASE_URL=https://generativelanguage.googleapis.com/v1beta/openai` and `AI_MODEL=gemini-2.5-flash` (model names and free limits change, check Google's current docs).
Free tiers have rate limits and can change; the app falls back to the template if a call fails.

### Free email: Gmail
1. Turn on **2-Step Verification** in your Google account (required for app passwords).
2. Open **myaccount.google.com/apppasswords**, create an app password (name it e.g. "feedback"), copy the 16 characters.
3. In `.env`:
   ```
   SMTP_HOST=smtp.gmail.com
   SMTP_PORT=587
   SMTP_USER=yourname@gmail.com
   SMTP_PASSWORD=the16characterapppassword
   SMTP_FROM=yourname@gmail.com
   CARE_REP_EMAIL=the address that should receive alerts
   ```
4. Restart. Submit a survey with low ratings: the care rep receives the alert email.
Any other SMTP provider works the same way (host, port, user, password).

### Free SMS: Africa's Talking sandbox
1. Register at **account.africastalking.com** and open the **Sandbox** app.
2. **Settings, API Key**: generate a key (it asks for your password and may send a confirmation email).
3. In `.env`: `AT_USERNAME=sandbox` (exactly) and `AT_API_KEY=your key`. Optionally `CARE_REP_PHONE=+2547...`.
4. Sandbox messages go to the dashboard's **simulator**, not to real phones.
5. Painter replies: AT must reach your computer. Run `ngrok http 8000` and set the SMS **Incoming Messages callback URL** in the AT dashboard to `https://<ngrok-host>/api/sms/incoming` (sandbox may require creating a test shortcode first). Or skip AT and call `POST /api/sms/incoming` yourself from `/docs`.
(AT's menus change; their docs at developers.africastalking.com are authoritative.)

---

## 6. How every line works (file by file)

### core/config.py
- `Settings(BaseSettings)`: each attribute is a setting; `database_url` is read from env var `DATABASE_URL`. `model_config` says "also read `.env`, ignore unknown variables".
- Defaults after `=` apply when nothing is set. `cors_origins` splits `FRONTEND_ORIGIN` on commas.
- `@lru_cache get_settings()` returns one shared object (a singleton bean).

### core/database.py
- `create_engine(url, pool_pre_ping=True)` creates the connection pool, testing connections before use.
- `SessionLocal` builds sessions (`autoflush=False`: we decide when SQL is sent; `expire_on_commit=False`: objects stay usable after commit).
- `Base`: parent of all entities. `get_db()` opens a session, `yield`s it, and `finally` closes it.
- `DbSession = Annotated[Session, Depends(get_db)]`: write `db: DbSession` in a route and FastAPI injects a session.

### core/errors.py, core/clock.py, core/health.py
- `NotFoundError` is raised by services; the registered handler returns `404 {"detail": ...}`.
- `utcnow()` is the single source of timezone-aware time. `GET /api/health` runs `SELECT 1`.

### feedback/models.py
- `Customer` and `Response` are tables. `Mapped[int] = mapped_column(...)` declares typed columns.
- `unique=True` on nullable email/phone: PostgreSQL allows many NULLs but no duplicate real values.
- `CheckConstraint("... BETWEEN 1 AND 5")`: the database itself rejects bad ratings.
- `Numeric(4, 2)` stores exact decimals. `index=True` on `category`, `created_at`, `customer_id` speeds the dashboard queries.
- `relationship(...)` lets code write `customer.responses` / `response.customer`.

### feedback/scoring.py
- `classify()` adds the three ratings, computes `mean = round(total/3, 2)` and compares the **integer sum** with 9 (sum < 9 detractor, == 9 passive, > 9 promoter), avoiding float errors. Example 2,3,2 gives sum 7, `(2.33, "detractor")`.

### feedback/schemas.py
- `Rating = Field(ge=1, le=5)` is reused for the three ratings. `EmailStr` validates email. `Literal["buyer","painter"]` restricts `kind`.
- `from_attributes=True` lets Pydantic read straight from entity objects.

### feedback/repository.py
- Small functions, each one query: find customer by email/phone, save customer/response (`db.flush()` sends the INSERT so the id exists, without committing), find one response, list responses (`joinedload` fetches the customer in the same SQL, newest first, `limit/offset`).

### feedback/service.py
- `_find_or_create_customer`: same email, else same phone, else create.
- `submit_feedback`: strip spaces from phone, find/create customer, `classify`, save response, create an alert only for detractors, then **one** `db.commit()`.

### feedback/router.py
- `POST /feedback` (status 201): validates `FeedbackIn`, lowercases the email, calls the service, queues `dispatch_alert` as a background task, returns `FeedbackOut`.

### alerts/models.py, repository.py, service.py, router.py
- `Alert` has `response_id` **unique** (one alert per response).
- Repository loads alert, response and customer in one query and lists newest first (`unread_only` adds a filter).
- Service: `create_for_detractor` (flush only; the caller commits), `mark_read`, `create_draft` (asks AI, stores the text). Missing ids raise `NotFoundError`.
- Router: `GET /alerts`, `POST /alerts/{id}/read`, `POST /alerts/{id}/draft-reply`.

### alerts/notifications.py
- `build_alert_email` builds the text with the customer's name, email, phone, ratings and mean.
- `send_email`: with no `SMTP_HOST` it only logs. Otherwise `SMTP` connect, `starttls()`, `login()`, `send_message()`. Any error is caught and returns `False`.
- `dispatch_alert(alert_id, session_factory)`: opens its **own** session (the request's is closed), emails the care rep, optionally texts `CARE_REP_PHONE`, saves `email_sent`/`sms_sent`. The `session_factory` parameter exists so tests can pass a test database.

### alerts/ai.py
- Uses the OpenAI-style `POST {AI_BASE_URL}/chat/completions` with `Authorization: Bearer <key>`, a system prompt (short, warm, no invented promises) and a user message with **only first name and three ratings**.
- Reads `choices[0].message.content`. No key, an error, a timeout or empty text returns `fallback_draft` and `ai_used=False`.

### dashboard/analytics.py, repository.py, service.py, router.py
- `linear_projection`: least-squares line through `(date, mean)` points (dates become day numbers, so gaps count), extended 7 days and clamped to 1-5. Fewer than 2 points returns `[]`.
- Repository: `count_all`, `count_by_category` (GROUP BY), `averages` (AVG), `daily_means` (group by `date(created_at)`, accepts PostgreSQL dates and SQLite strings).
- Service turns those into `StatsOut` / `TrendOut`. Router: `/stats`, `/trend` (`days` 1-365), `/responses`, `/responses/{id}`.

### sms/parser.py, client.py, messages.py, service.py, router.py
- Regex: three digits 1-5 separated by optional space, comma, dot or dash. `4 5 4`, `454`, `4,5,4` pass; `hello`, `4 5 6` do not.
- `send_sms`: no key means log only; `AT_USERNAME == "sandbox"` selects the sandbox URL; form-encoded POST with header `apiKey`; errors are caught.
- `process_incoming`: normalises the sender to `+254...`, parses; junk returns "ignored" plus a help text; otherwise saves a painter response through the **same** feedback service (so scoring and alerts are identical to the web form) and returns a thank-you text.
- Router: `/sms/invite` sends the invitation; `/sms/incoming` reads form fields `from` and `text`, queues the reply SMS and, for detractors, the alert.

### main.py
- Creates the app, adds `CORSMiddleware` (allowed origins from settings), registers the 404 handler and includes the five routers.

### seed.py
- `seed(db)` returns `False` if responses already exist, else creates the demo data described in section 3.

### alembic/
- `env.py` imports both entity modules so Alembic sees all tables and uses the same `DATABASE_URL`. `0001_initial.py` creates tables, constraints and indexes (`downgrade` drops them). For a schema change: edit `models.py`, then `alembic revision --autogenerate -m "what changed"` and `alembic upgrade head`.

---

## 7. Tests

`pytest` finds every `test_*.py`. They sit **beside the code they test**, for example `app/dashboard/test_router.py` tests the dashboard folder.

```bash
pytest -q                 # all 61 tests (about 1 second)
pytest app/sms -q         # only one feature
ruff check . && ruff format --check .
```

- `conftest.py` gives every test a fresh in-memory SQLite database and replaces real email/SMS sending with lists (`sent_alerts`, `sent_sms`), so tests never need PostgreSQL, internet or keys.
- Tests cover: scoring and its boundaries, validation errors (422), 404s, repeat customers, SMS parsing and replies, alert creation and delivery flags, AI success / failure / empty / template fallback (and that the surname and email are not sent to the AI), SMTP call order, the projection maths, pagination and seeding.
- Test files are excluded from the Docker image through `.dockerignore`.

## 8. Troubleshooting

| Symptom | Fix |
|---|---|
| `password authentication failed` | wrong user/password in `.env` `DATABASE_URL` |
| `database "feedback" does not exist` | `psql -U postgres -c "CREATE DATABASE feedback;"` |
| `relation "customers" does not exist` (and a browser "CORS error") | run `alembic upgrade head`. A crashing API returns no CORS header, so the browser mislabels it |
| Real CORS error | `FRONTEND_ORIGIN` must match the browser address exactly (`localhost` and `127.0.0.1` differ); restart after editing |
| `ModuleNotFoundError: app` | run commands from inside `backend/` |
| No emails/SMS arrive | check the terminal: "SMTP not configured; would email..." means the settings are empty |
| AI draft says "Template draft" | `AI_API_KEY` empty, wrong model name, or the call failed (see the terminal log) |

## 9. Limitations (harden before real production)

- Dashboard endpoints have **no login**; add authentication for care staff.
- `/api/sms/incoming` is open; verify requests come from Africa's Talking (shared secret or IP allow-list).
- "Day" in the trend follows the database session timezone; set PostgreSQL `timezone` deliberately.
- The deploy jobs in `.github/workflows/ci.yml` are placeholders for your hosting provider.
