# Company X Feedback (frontend)

A small **Next.js 16 (React 19 + TypeScript)** app with two separate screens. They are intentionally **not linked to each other**, because customers and Company X staff are different audiences: give customers `/` and staff `/dashboard`.

1. **`/` the survey**: three questions, one per screen, answered with a 1-5 **star rating**, then name/email/phone and a confirmation screen.
2. **`/dashboard` the dashboard**: total respondents, a donut of detractors/passives/promoters, a daily trend with a 7-day projection, detractor alerts with editable AI reply drafts, and a drill-down into each person's ratings. It refreshes itself every 5 seconds.

There are no runtime dependencies beyond Next.js and React. The charts are hand-drawn SVG.

| | |
|---|---|
| Port | **3000** |
| Talks to | the FastAPI backend at **http://localhost:8000** (`NEXT_PUBLIC_API_URL`) |
| Tests | **Vitest** + React Testing Library: 32 tests, each beside the file it tests |
| Checks | ESLint 9 (`npm run lint`), TypeScript (`npx tsc --noEmit`), `npm run build` |

---

## 1. Quick start

Start the backend first (see `../backend/README.md`), then:

```bash
cd frontend
cp .env.local.example .env.local     # Windows: copy .env.local.example .env.local
npm install
npm run dev                          # http://localhost:3000
```

Survey: http://localhost:3000 · Dashboard: http://localhost:3000/dashboard · Production: `npm run build && npm start`

Needs Node.js 20.9 or newer.

### Where the frontend learns the backend address

One place only, **`.env.local`**: `NEXT_PUBLIC_API_URL=http://localhost:8000`. `lib/api.ts` reads it. If you change it, restart `npm run dev`. (`NEXT_PUBLIC_` values are baked in at build time; in Docker it is a build argument.)

---

## 2. Routes and ports (the contract with the backend)

All defined in `lib/api.ts`.

| Frontend call | Request to port 8000 | Used on |
|---|---|---|
| `api.submitFeedback(body)` | `POST /api/feedback` | survey, last step |
| `api.stats()` | `GET /api/stats` | dashboard |
| `api.trend(30)` | `GET /api/trend?days=30` | dashboard |
| `api.responses(25)` | `GET /api/responses?limit=25` | dashboard table + drill-down |
| `api.alerts()` | `GET /api/alerts` | dashboard alerts |
| `api.markAlertRead(id)` | `POST /api/alerts/{id}/read` | "Mark handled" |
| `api.draftReply(id)` | `POST /api/alerts/{id}/draft-reply` | "Draft reply" |

The SMS routes are used by phones and Africa's Talking, not by this app. The backend must allow this app's origin in `FRONTEND_ORIGIN`, otherwise the browser reports a CORS error.

---

## 3. What was built, mapped to the brief

| Brief asks for | Where / how |
|---|---|
| 3 questions on a 1-5 scale as stars | `app/page.tsx` `QUESTIONS`, `components/Stars.tsx` |
| Collect name, email, phone | last survey step (phone optional; "I'm a professional painter" sets `kind`) |
| Under a minute, mobile first | one question per screen, large tap targets |
| Clear feedback while rating | stars preview on hover/focus, fill on click, text label (Poor, Fair, Good, Very good, Excellent) |
| Thank-you moment | a quietly animated check mark |
| Light and dark modes | CSS variables switch with `prefers-color-scheme` |
| Accessible | `radiogroup`/`radio` roles with labels, real `<label>`s, visible focus, keys **1-5**, reduced-motion support |
| Total respondents | dashboard "Total respondents" card |
| Donut of detractors, passives, promoters | `components/Charts.tsx` `Donut` |
| Day-by-day trend and projection | `TrendChart`: solid line = real data, dashed = 7-day projection from the backend |
| Drill-down | click (or Tab + Enter) a table row |
| Alerts with name and email | alerts card shows name, email, phone and delivery status |
| AI touch | "Draft reply" gives an editable draft; "Open in my email app" (`mailto:`). Nothing is sent automatically |
| Live dashboard | re-fetches every 5 seconds |
| CI/CD | `Dockerfile`, ESLint, Vitest, build; the pipeline is `../.github/workflows/ci.yml` |

Painters on feature phones are served by SMS through the backend (reply `4 5 4`).

---

## 4. Structure (each test sits next to its code)

```
frontend/
├── app/
│   ├── layout.tsx  globals.css
│   ├── page.tsx                survey                  page.test.tsx
│   └── dashboard/
│       └── page.tsx            dashboard               page.test.tsx
├── components/
│   ├── Stars.tsx               StarRating + StarsDisplay    Stars.test.tsx
│   └── Charts.tsx              Donut + TrendChart           Charts.test.tsx
├── lib/
│   ├── api.ts                  base URL, types, every call  api.test.ts
│   └── rating.ts               rating text labels           rating.test.ts
├── vitest.config.mts  vitest.setup.ts  eslint.config.mjs  Dockerfile  next.config.mjs
```

### Why Vitest (not Jest)?

The brief's pipeline names **Vitest** for the frontend (and `pytest` for Python). Vitest works like Jest (`describe`, `it`, `expect`, `vi.fn()` instead of `jest.fn()`) but starts faster and needs no extra setup with this toolchain. **React Testing Library** renders components in a fake browser (jsdom) and finds things the way a user would (by role and label).

### File walkthrough

**`lib/api.ts`**: `API_URL` (default port 8000); types that mirror the backend JSON; `request<T>()`, one helper that prefixes the URL, sends JSON, uses `cache: "no-store"`, throws on non-2xx; `api`, one function per backend route.

**`lib/rating.ts`**: `labelFor(rating)` returns the word under the stars, or "Select a rating".

**`components/Stars.tsx`**: `StarRating` is five `role="radio"` buttons inside a `radiogroup`; hover/focus previews the fill, click calls `onChange(n)`; each button is labelled "3 stars" for screen readers. `StarsDisplay` is the read-only version used on the dashboard.

**`app/page.tsx`** (survey): `"use client"` (uses state and keyboard events). `step` 0-2 questions, 3 contact form, 4 thank-you. `choose()` stores an answer; a `keydown` listener lets 1-5 pick a rating; `submit()` calls `api.submitFeedback`, shows a friendly error on failure and keeps what was typed. The Next button is disabled until a rating is chosen; Back keeps earlier answers.

**`components/Charts.tsx`**: `Donut` uses a circle of radius 15.9155 (circumference exactly 100) so each segment's percentage equals its dash length; `strokeDashoffset` chains the arcs from 12 o'clock. `TrendChart` maps dates to x and 1-5 to y, draws grid lines, the solid actual line, the dashed projection (starting at the last real point), dots with tooltips and end labels.

**`app/dashboard/page.tsx`**: `load()` fetches stats, trend, responses and alerts in parallel and shows "Can't reach the API" on failure. An effect fetches once immediately, then every 5 seconds, and cleans up when you leave. `draft()` stores the draft per alert in an editable textarea; the `mailto:` link opens the rep's own email app. Rows are keyboard-focusable and open the drill-down with each score as stars. There is no link back to the survey.

**`app/globals.css`**: colour variables with a dark override; classes for the survey (`.star-input`, `.progress`, `.thanks`) and dashboard (`.grid`, `.card`, `.alert`, `.pill`); animations switch off for `prefers-reduced-motion`.

**`Dockerfile`**: builds with `NEXT_PUBLIC_API_URL` as a build argument, then runs the small `standalone` output on port 3000.

---

## 5. Tests (32)

```bash
npm test                 # run once
npm run test:watch       # re-run on save
```

| File | What it proves |
|---|---|
| `lib/api.test.ts` | default port 8000; survey is POSTed as JSON to `/api/feedback`; every dashboard URL is right; server errors become clear exceptions |
| `lib/rating.test.ts` | rating labels and the placeholder |
| `components/Stars.test.tsx` | five labelled radios, click calls `onChange`, only the chosen star is checked, read-only stars are announced |
| `components/Charts.test.tsx` | donut counts/total/empty state; trend draws a real and a dashed line, handles no data, tooltips |
| `app/page.test.tsx` | Next disabled until rated; labels; keyboard 1-5; full 3-question flow submits the exact payload; Back keeps answers; failure shows an error and keeps the form; **no link to the dashboard** |
| `app/dashboard/page.test.tsx` | total and averages; split, trend and table; alerts show email and delivery status; drill-down shows stars; edit a draft and `mailto:` link; mark handled; API-down message; **no link to the survey** |

The API module is replaced by a mock in the page tests, so no backend is needed.

## 6. Troubleshooting

| Symptom | Fix |
|---|---|
| "couldn't send" / "Can't reach the API" | backend not running on port 8000, or wrong `NEXT_PUBLIC_API_URL` (restart `npm run dev`) |
| Browser CORS error | in `backend/.env` set `FRONTEND_ORIGIN` to the exact address in your browser and restart the API. If the backend log shows a 500, fix that first: a crashing API also looks like CORS |
| Dashboard empty | `python -m app.seed` in the backend, or submit a survey |
| Port 3000 busy | `npm run dev -- -p 3001` and add `http://localhost:3001` to `FRONTEND_ORIGIN` |

## 7. Limitations

- The dashboard has **no login**: anyone with the `/dashboard` address can see customer names and emails. Add authentication before real use.
- "Live" is polling every 5 seconds, not WebSockets.
- Charts are simple SVG: no zoom or export.
