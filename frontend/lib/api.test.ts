// Tests for lib/api.ts: the backend address and every route the frontend calls.
import { afterEach, describe, expect, it, vi } from "vitest";
import { API_URL, api } from "./api";

/** Replace the browser's fetch() with a fake that answers with `body`. */
function mockFetch(body: unknown, ok = true, status = 200) {
  const fn = vi.fn().mockResolvedValue({ ok, status, json: async () => body });
  vi.stubGlobal("fetch", fn);
  return fn;
}

afterEach(() => vi.unstubAllGlobals()); // put the real fetch back after each test

describe("api", () => {
  it("points at the backend on port 8000 by default", () => {
    expect(API_URL).toBe("http://localhost:8000");
  });

  it("POSTs the survey as JSON to /api/feedback", async () => {
    const fetchMock = mockFetch({ id: 1, mean: 4.67, category: "promoter", alert_created: false });
    const body = {
      name: "Amina",
      email: "a@x.com",
      kind: "buyer" as const,
      product_rating: 5,
      care_rating: 4,
      happy_rating: 5,
    };
    const result = await api.submitFeedback(body);

    expect(result.category).toBe("promoter");
    const [url, init] = fetchMock.mock.calls[0];
    expect(url).toBe("http://localhost:8000/api/feedback");
    expect(init.method).toBe("POST");
    expect(JSON.parse(init.body)).toEqual(body); // exactly what we passed in
    expect(init.headers["Content-Type"]).toBe("application/json");
  });

  it("calls every dashboard route with the right method and URL", async () => {
    const fetchMock = mockFetch({});
    await api.stats();
    await api.trend(14);
    await api.responses(10);
    await api.alerts();
    await api.markAlertRead(7);
    await api.markAllAlertsRead();
    await api.draftReply(7);
    const calls = fetchMock.mock.calls.map(([url, init]) => `${init?.method ?? "GET"} ${url}`);
    expect(calls).toEqual([
      "GET http://localhost:8000/api/stats",
      "GET http://localhost:8000/api/trend?days=14",
      "GET http://localhost:8000/api/responses?limit=10",
      "GET http://localhost:8000/api/alerts",
      "POST http://localhost:8000/api/alerts/7/read",
      "POST http://localhost:8000/api/alerts/read-all",
      "POST http://localhost:8000/api/alerts/7/draft-reply",
    ]);
  });

  it("throws a clear error when the server answers with an error", async () => {
    mockFetch({}, false, 500);
    await expect(api.stats()).rejects.toThrow("GET /api/stats failed (500)");
  });
});
