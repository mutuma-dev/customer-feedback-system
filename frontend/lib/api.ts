/**
 * Everything the frontend knows about the backend lives in THIS file:
 *   1. the backend address (port 8000 by default)
 *   2. the shape (TypeScript "types") of the JSON the backend sends
 *   3. one function per backend endpoint
 * If a route changes, this is the only file that needs editing.
 */

// The backend address. Comes from .env.local (NEXT_PUBLIC_API_URL); "??" gives a default.
export const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

// ---------------------------------------------------------------------------
// Types: they describe the data. TypeScript warns us if we use a field that doesn't exist.
// ---------------------------------------------------------------------------

/** Verdict given by the backend: mean < 3, = 3, > 3. */
export type Category = "detractor" | "passive" | "promoter";

/** A person who gave feedback. `email`/`phone` are null when not provided. */
export interface Customer {
  id: number;
  name: string;
  email: string | null;
  phone: string | null;
  kind: string; // "buyer" or "painter"
}

/** One submitted survey (three star ratings) with its customer. */
export interface FeedbackResponse {
  id: number;
  customer: Customer;
  product_rating: number;
  care_rating: number;
  happy_rating: number;
  mean: number;
  category: Category;
  source: string; // "web" or "sms"
  created_at: string; // ISO date text, e.g. "2026-11-12T10:00:00Z"
}

/** An alert raised for an unhappy customer. */
export interface Alert {
  id: number;
  is_read: boolean; // false = shows in the bell's unread count
  email_sent: boolean; // did the care-team email really go out?
  sms_sent: boolean;
  draft_reply: string | null; // last reply draft, if any
  created_at: string;
  response: FeedbackResponse;
}

/** Headline numbers for the dashboard. */
export interface Stats {
  total: number;
  detractors: number;
  passives: number;
  promoters: number;
  avg_product: number;
  avg_care: number;
  avg_happy: number;
  avg_mean: number;
}

/** One day on the trend chart. */
export interface TrendPoint {
  date: string;
  mean: number;
  count?: number; // missing for projected days
}

export interface Trend {
  points: TrendPoint[]; // real data
  projection: TrendPoint[]; // forecast
}

/** What the survey sends to POST /api/feedback. */
export interface FeedbackInput {
  name: string;
  email: string;
  phone?: string;
  kind: "buyer" | "painter";
  product_rating: number;
  care_rating: number;
  happy_rating: number;
}

/** What the backend answers after a survey is submitted. */
export interface FeedbackResult {
  id: number;
  mean: number;
  category: Category;
  alert_created: boolean;
}

// ---------------------------------------------------------------------------
// One shared helper that every call below uses.
// ---------------------------------------------------------------------------

/** Calls the backend and returns its JSON as type T. Throws an Error if the answer is not OK. */
async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const res = await fetch(`${API_URL}${path}`, {
    ...init,
    headers: { "Content-Type": "application/json", ...init?.headers },
    cache: "no-store", // never reuse an old answer: the dashboard must show fresh data
  });
  if (!res.ok) throw new Error(`${init?.method ?? "GET"} ${path} failed (${res.status})`);
  return (await res.json()) as T;
}

// ---------------------------------------------------------------------------
// The backend's endpoints, one function each.
// ---------------------------------------------------------------------------
export const api = {
  /** POST /api/feedback: submit the survey. */
  submitFeedback: (body: FeedbackInput) =>
    request<FeedbackResult>("/api/feedback", { method: "POST", body: JSON.stringify(body) }),

  /** GET /api/stats: totals, the three groups and the averages. */
  stats: () => request<Stats>("/api/stats"),

  /** GET /api/trend: daily mean scores plus a 7-day projection. */
  trend: (days = 30) => request<Trend>(`/api/trend?days=${days}`),

  /** GET /api/responses: newest first, each with its customer. */
  responses: (limit = 25) => request<FeedbackResponse[]>(`/api/responses?limit=${limit}`),

  /** GET /api/alerts: the latest detractor alerts. */
  alerts: () => request<Alert[]>("/api/alerts"),

  /** POST /api/alerts/{id}/read: mark one alert as read. */
  markAlertRead: (id: number) => request<Alert>(`/api/alerts/${id}/read`, { method: "POST" }),

  /** POST /api/alerts/read-all: mark every alert as read. */
  markAllAlertsRead: () => request<{ updated: number }>("/api/alerts/read-all", { method: "POST" }),

  /** POST /api/alerts/{id}/draft-reply: AI (or template) reply draft. Sends nothing. */
  draftReply: (id: number) =>
    request<{ draft: string; ai_used: boolean }>(`/api/alerts/${id}/draft-reply`, {
      method: "POST",
    }),
};
