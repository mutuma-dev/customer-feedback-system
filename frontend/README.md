# Company X Feedback (frontend)

A small **Next.js 16 (React 19 + TypeScript)** app with two separate screens.

1. **`/` the survey**: three questions, one per screen, answered with a 1-5 **star rating**, then name/email/phone and a confirmation screen.
2. **`/dashboard` the dashboard**: total respondents, a donut of detractors/passives/promoters, a daily trend with a 7-day projection, detractor alerts with editable AI reply drafts, and a drill-down into each person's ratings. It refreshes itself every 5 seconds.


## 1. Quick start

Start the backend first then:

```bash
cd frontend 
npm install
npm run dev   # http://localhost:3000
```

Needs Node.js 20.9 or newer.


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


---


## 4. Structure

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
```
