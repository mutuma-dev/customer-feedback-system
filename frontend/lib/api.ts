/**
 * Everything the frontend knows about the backend lives in this file:
 * the base URL (port 8000 by default), every route, and the response types.
 */
export const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

export type Category = "detractor" | "passive" | "promoter";

export interface Customer {
  id: number;
  name: string;
  email: string | null;
  phone: string | null;
  kind: string;
}

export interface FeedbackResponse {
  id: number;
  customer: Customer;
  product_rating: number;
  care_rating: number;
  happy_rating: number;
  mean: number;
  category: Category;
  source: string;
  created_at: string;
}

export interface Alert {
  id: number;
  is_read: boolean;
  email_sent: boolean;
  sms_sent: boolean;
  draft_reply: string | null;
  created_at: string;
  response: FeedbackResponse;
}

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

export interface TrendPoint {
  date: string;
  mean: number;
  count?: number;
}

export interface Trend {
  points: TrendPoint[];
  projection: TrendPoint[];
}

export interface FeedbackInput {
  name: string;
  email: string;
  phone?: string;
  kind: "buyer" | "painter";
  product_rating: number;
  care_rating: number;
  happy_rating: number;
}

export interface FeedbackResult {
  id: number;
  mean: number;
  category: Category;
  alert_created: boolean;
}

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const res = await fetch(`${API_URL}${path}`, {
    ...init,
    headers: { "Content-Type": "application/json", ...init?.headers },
    cache: "no-store",
  });
  if (!res.ok) throw new Error(`${init?.method ?? "GET"} ${path} failed (${res.status})`);
  return (await res.json()) as T;
}

export const api = {
  /** POST /api/feedback - submit the survey. */
  submitFeedback: (body: FeedbackInput) =>
    request<FeedbackResult>("/api/feedback", { method: "POST", body: JSON.stringify(body) }),
  /** GET /api/stats - totals, split and averages. */
  stats: () => request<Stats>("/api/stats"),
  /** GET /api/trend - daily mean and 7-day projection. */
  trend: (days = 30) => request<Trend>(`/api/trend?days=${days}`),
  /** GET /api/responses - newest first, with customer details. */
  responses: (limit = 25) => request<FeedbackResponse[]>(`/api/responses?limit=${limit}`),
  /** GET /api/alerts - detractor alerts. */
  alerts: () => request<Alert[]>("/api/alerts"),
  /** POST /api/alerts/:id/read - mark an alert handled. */
  markAlertRead: (id: number) => request<Alert>(`/api/alerts/${id}/read`, { method: "POST" }),
  /** POST /api/alerts/:id/draft-reply - AI (or template) follow-up draft. */
  draftReply: (id: number) =>
    request<{ draft: string; ai_used: boolean }>(`/api/alerts/${id}/draft-reply`, {
      method: "POST",
    }),
};
