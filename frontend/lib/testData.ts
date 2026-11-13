/**
 * Sample data builders used ONLY by tests (so every test does not repeat a long object).
 * `overrides` lets a test change just the fields it cares about.
 */
import type { Alert, FeedbackResponse } from "./api";

/** A response from an unhappy web customer, created "just now". */
export function makeResponse(overrides: Partial<FeedbackResponse> = {}): FeedbackResponse {
  return {
    id: 1,
    customer: {
      id: 1,
      name: "Amina Otieno",
      email: "amina@example.com",
      phone: "+254712345678",
      kind: "buyer",
    },
    product_rating: 2,
    care_rating: 3,
    happy_rating: 2,
    mean: 2.33,
    category: "detractor",
    source: "web",
    created_at: new Date().toISOString(),
    ...overrides,
  };
}

/** An unread alert for the response above. */
export function makeAlert(overrides: Partial<Alert> = {}): Alert {
  return {
    id: 10,
    is_read: false,
    email_sent: true,
    sms_sent: false,
    draft_reply: null,
    created_at: new Date().toISOString(),
    response: makeResponse(),
    ...overrides,
  };
}
