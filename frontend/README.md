# Company X Feedback (frontend)

A small **Next.js 16 (React 19 + TypeScript)** app with two separate pages. They are intentionally **not
linked to each other**, because customers and Company X staff are different audiences:
give customers `/` and staff `/dashboard`.

1. **`/` the survey** - three questions with a 1-5 **star rating**, one per screen, then name/email/phone and a confirmation.
2. **`/dashboard` the dashboard** - total respondents, average ratings, "How customers feel" (donut), "Satisfaction over time" (trend + forecast), recent responses, and an **alerts bell** with an unread-count badge. It refreshes itself every 5 seconds.

| | |
|---|---|
| Port | **3000** |
| Talks to | the FastAPI backend at **http://localhost:8000** (`NEXT_PUBLIC_API_URL`) |
| Tests | **Vitest** + React Testing Library: 73 tests, each beside the file it tests |
| Checks | `npm run lint` (ESLint), `npm run build` (also type-checks) |
| Mobile | mobile-first CSS; panels are full screen on phones; tap targets 40px+ |

All source code and CSS is commented. (`package.json` / `tsconfig.json` are JSON, which cannot hold comments; see section 6.)

---

## 1. Run it

Start the backend first (see `../backend/README.md`), then:

```bash
cd frontend
cp .env.local.example .env.local      # Windows: copy .env.local.example .env.local
npm install
npm run dev                           # http://localhost:3000
```
Survey: http://localhost:3000 · Dashboard: http://localhost:3000/dashboard · Production: `npm run build && npm start` (needs Node 20.9+).

The backend address lives in **`.env.local`** (`NEXT_PUBLIC_API_URL=http://localhost:8000`). Restart `npm run dev` after changing it.

---

## 2. The dashboard, explained

| Part | What it shows |
|---|---|
| **Bell** (top right) | Red badge = number of **unread** alerts. It disappears at zero. Click to open the alerts panel |
| **Alerts panel** | Tabs *Unread (n)* / *All (n)*, a **Mark all as read** link, and one card per alert |
| **Alert card** | Name · time ago · average score and verdict · labelled **Email / Phone / Answered via** · the three ratings as stars · chips *Email sent / SMS not sent* · buttons **Write reply** and **Mark as read** |
| **Mark as read** | Tells the backend the alert is handled. The blue unread dot goes, the bell number drops by one, and the card leaves the *Unread* tab (it stays under *All*, marked "✓ Read"). It does not delete or send anything |
| **Write reply** | Asks the backend for a draft (Groq AI, or a template if the AI is unavailable). The rep edits it and opens it in their own email app. **Nothing is sent automatically** |
| **Total respondents** | One big number |
| **Average ratings** | Overall average and one row per question, as stars |
| **How customers feel** | Donut of *Unhappy (detractors) / Neutral (passives) / Happy (promoters)* |
| **Satisfaction over time** | Daily average score; dashed line = 7-day forecast |
| **Recent responses** | Table; tap a row for the full details panel |

---

## 3. Routes and ports (the contract with the backend)

All defined in `lib/api.ts`.

| Frontend call | Request to port 8000 | Used for |
|---|---|---|
| `api.submitFeedback(body)` | `POST /api/feedback` | survey submit |
| `api.stats()` | `GET /api/stats` | summary cards |
| `api.trend(30)` | `GET /api/trend?days=30` | trend chart |
| `api.responses(25)` | `GET /api/responses?limit=25` | table |
| `api.alerts()` | `GET /api/alerts` | bell + alerts panel |
| `api.markAlertRead(id)` | `POST /api/alerts/{id}/read` | Mark as read |
| `api.markAllAlertsRead()` | `POST /api/alerts/read-all` | Mark all as read |
| `api.draftReply(id)` | `POST /api/alerts/{id}/draft-reply` | Write reply |

The backend must list this site in `FRONTEND_ORIGIN` or the browser reports a CORS error.

---

## 4. Structure (each test sits next to its code)

```
frontend/
├── app/
│   ├── layout.tsx  globals.css          page shell + ALL the styling (commented by section)
│   ├── page.tsx                         survey                      page.test.tsx
│   └── dashboard/page.tsx               dashboard                   page.test.tsx
├── components/
│   ├── Stars.tsx                        StarRating (input) + StarsDisplay      Stars.test.tsx
│   ├── Charts.tsx                       Donut + TrendChart (SVG)               Charts.test.tsx
│   ├── SidePanel.tsx                    slide-in panel (full screen on phones) SidePanel.test.tsx
│   ├── NotificationBell.tsx             bell + unread badge                    NotificationBell.test.tsx
│   ├── AlertCard.tsx                    one labelled alert                     AlertCard.test.tsx
│   ├── AlertsPanel.tsx                  tabs + list + mark all                 AlertsPanel.test.tsx
│   └── ResponseDetail.tsx               details of one response                ResponseDetail.test.tsx
├── lib/
│   ├── api.ts                           backend address, types, every call     api.test.ts
│   ├── format.ts                        "5 min ago", Unhappy/Neutral/Happy     format.test.ts
│   ├── rating.ts                        Poor ... Excellent                     rating.test.ts
│   └── testData.ts                      sample data builders used only by tests
└── vitest.config.mts  vitest.setup.ts  eslint.config.mjs  next.config.mjs  Dockerfile
```

How the pieces fit: `app/dashboard/page.tsx` keeps the data (stats, trend, responses, alerts) in React **state**, refreshes it
every 5 seconds, and passes it down to the components as **props**. Components only display data and call the
functions they were given (`onMarkRead`, `onDraft`...). That is why they are easy to test: a test passes fake functions.

---

## 5. Tests (73)

```bash
npm test               # run once
npm run test:watch     # re-run when you save
```
Vitest is the runner named in the brief (it works like Jest: `describe`, `it`, `expect`, `vi.fn()`). React Testing Library renders components in a
fake browser and finds things the way a user would (by role and label). The backend is replaced by fakes, so no server is needed.

| File | What it proves |
|---|---|
| `lib/api.test.ts` | port 8000 by default; survey sent as JSON; every route's method and URL; errors become clear exceptions |
| `lib/format.test.ts` | "just now / 5 min ago / 3 h ago / 3 d ago / date"; Unhappy/Neutral/Happy; source and customer labels |
| `components/Stars.test.tsx` | five labelled stars, click, checked state, read-only stars announced |
| `components/Charts.test.tsx` | donut counts and plain-language labels; trend line + dashed forecast; empty state |
| `components/SidePanel.test.tsx` | closed = nothing; Escape, X and background close it; clicks inside do not; page scroll locked |
| `components/NotificationBell.test.tsx` | badge number, hidden at 0, "9+" cap, accessible label, click |
| `components/AlertCard.test.tsx` | labelled details; stars; delivery chips; missing email shown as "Not provided"; unread vs read; reply draft (AI/template/saved), editing, mail/call links, errors |
| `components/AlertsPanel.test.tsx` | Unread/All tabs and counts; mark all; empty states |
| `components/ResponseDetail.test.tsx` | closed when empty; every detail under a label; close |
| `app/page.test.tsx` | the whole survey flow and the exact data sent; back; errors keep the form; **no link to the dashboard** |
| `app/dashboard/page.test.tsx` | summary cards; "How customers feel" (no "split"); details panel; **bell number goes down when alerts are read and disappears at zero**; reply draft; API-down message; **no link to the survey** |

## 6. Reading the code

* `.tsx` = TypeScript + HTML-like markup (JSX). `{ ... }` inside markup means "run this JavaScript here".
* `useState` keeps a value that, when changed, redraws the screen. `useEffect` runs code after drawing (we use it for the 5-second refresh).
* `"use client"` at the top marks a file that runs in the browser.
* JSON files cannot contain comments, so here is what the important ones do: `package.json` lists the libraries and the commands (`dev`, `build`, `lint`, `test`); `tsconfig.json` sets the TypeScript rules; `package-lock.json` pins exact versions (used by `npm ci`).

## 7. Troubleshooting

| Symptom | Fix |
|---|---|
| "Can't reach the API" | backend not running on port 8000, or wrong `NEXT_PUBLIC_API_URL` (restart `npm run dev`) |
| Browser CORS error | set `FRONTEND_ORIGIN` in `backend/.env` to the exact browser address and restart the API. If the backend log shows a 500, fix that first |
| Dashboard empty | `python -m app.seed` in the backend, or submit a survey |
| Bell shows no number | all alerts are read (or none exist yet): submit a survey with low ratings |
| Port 3000 busy | `npm run dev -- -p 3001` and add `http://localhost:3001` to `FRONTEND_ORIGIN` |

## 8. Limitations

* The dashboard has **no login**: anyone with the `/dashboard` address sees customer names and emails.
* "Live" is polling every 5 seconds, not WebSockets.
* The alerts list holds the newest 50, so the bell can undercount beyond 50 unread.
* Charts are simple SVG: no zoom or export.
