// Tests for the dashboard page ("/dashboard"): the cards, the alerts bell and the panels.
import { render, screen, within } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { beforeEach, describe, expect, it, vi } from "vitest";
import { api, type Alert } from "@/lib/api";
import { makeAlert, makeResponse } from "@/lib/testData";
import DashboardPage from "./page";

// Fake backend: every call the dashboard makes is replaced.
vi.mock("@/lib/api", () => ({
  api: {
    stats: vi.fn(),
    trend: vi.fn(),
    responses: vi.fn(),
    alerts: vi.fn(),
    markAlertRead: vi.fn(),
    markAllAlertsRead: vi.fn(),
    draftReply: vi.fn(),
  },
}));

const person = (id: number, name: string, email: string | null) => ({
  id,
  name,
  email,
  phone: "+254700000000",
  kind: "buyer",
});
const amina = makeResponse({ id: 1, customer: person(1, "Amina Otieno", "amina@example.com") });
const brian = makeResponse({
  id: 2,
  customer: person(2, "Brian Kamau", null),
  product_rating: 5,
  care_rating: 5,
  happy_rating: 4,
  mean: 4.67,
  category: "promoter",
  source: "sms",
});

// The "server's" alerts. The fake mark-as-read functions below change this list, just like the
// real backend would, so the dashboard's refresh sees the new state.
let alertsOnServer: Alert[] = [];

beforeEach(() => {
  alertsOnServer = [
    makeAlert({ id: 10, response: amina }),
    makeAlert({ id: 11, response: makeResponse({ id: 3, customer: person(3, "Carol Wanjiku", "carol@example.com") }) }),
  ];
  vi.mocked(api.stats).mockResolvedValue({
    total: 42,
    detractors: 5,
    passives: 7,
    promoters: 30,
    avg_product: 3.9,
    avg_care: 4.1,
    avg_happy: 3.8,
    avg_mean: 3.93,
  });
  vi.mocked(api.trend).mockResolvedValue({
    points: [
      { date: "2026-11-11", mean: 3.5, count: 3 },
      { date: "2026-11-12", mean: 3.9, count: 4 },
    ],
    projection: [{ date: "2026-11-13", mean: 4.0 }],
  });
  vi.mocked(api.responses).mockResolvedValue([amina, brian]);
  vi.mocked(api.alerts).mockImplementation(async () => alertsOnServer);
  vi.mocked(api.markAlertRead).mockImplementation(async (id: number) => {
    alertsOnServer = alertsOnServer.map((a) => (a.id === id ? { ...a, is_read: true } : a));
    return alertsOnServer.find((a) => a.id === id) as Alert;
  });
  vi.mocked(api.markAllAlertsRead).mockImplementation(async () => {
    alertsOnServer = alertsOnServer.map((a) => ({ ...a, is_read: true }));
    return { updated: 2 };
  });
  vi.mocked(api.draftReply).mockResolvedValue({ draft: "Hi Amina, we are sorry.", ai_used: true });
});

describe("Dashboard summary", () => {
  it("shows the total number of respondents", async () => {
    render(<DashboardPage />);
    const card = await screen.findByRole("region", { name: "Total respondents" });
    expect(await within(card).findByText("42")).toBeInTheDocument();
  });

  it("shows the average ratings", async () => {
    render(<DashboardPage />);
    const card = await screen.findByRole("region", { name: "Average ratings" });
    expect(await within(card).findByText("3.93")).toBeInTheDocument();
    expect(within(card).getByText(/3\.9$/)).toBeInTheDocument();
  });

  it("calls the donut card 'How customers feel' (not 'split') and explains the groups", async () => {
    render(<DashboardPage />);
    expect(await screen.findByRole("heading", { name: "How customers feel" })).toBeInTheDocument();
    expect(screen.queryByText(/split/i)).not.toBeInTheDocument();
    expect(await screen.findByText("Unhappy (detractors): 5")).toBeInTheDocument();
  });

  it("shows the trend chart with a plain title", async () => {
    render(<DashboardPage />);
    expect(await screen.findByRole("heading", { name: "Satisfaction over time" })).toBeInTheDocument();
    expect(await screen.findByRole("img", { name: "Daily average score with projection" })).toBeInTheDocument();
  });

  it("explains the problem when the API is unreachable", async () => {
    vi.mocked(api.stats).mockRejectedValue(new Error("down"));
    render(<DashboardPage />);
    expect(await screen.findByRole("alert")).toHaveTextContent("Can't reach the API");
  });

  it("has no link back to the survey (different audiences)", async () => {
    render(<DashboardPage />);
    await screen.findByText("Brian Kamau"); // wait until the data has loaded
    expect(screen.queryByRole("link")).not.toBeInTheDocument();
  });
});

describe("Recent responses", () => {
  it("opens the full details of a response when its row is clicked", async () => {
    const user = userEvent.setup();
    render(<DashboardPage />);
    const table = await screen.findByRole("table");
    await user.click(await within(table).findByText("Brian Kamau"));

    const panel = screen.getByRole("dialog", { name: "Response details" });
    expect(within(panel).getByText("Email")).toBeInTheDocument();
    expect(within(panel).getByText("Not provided")).toBeInTheDocument(); // Brian has no email
    expect(within(panel).getByText("SMS reply")).toBeInTheDocument();
    expect(within(panel).getAllByRole("img", { name: "5 out of 5 stars" })).toHaveLength(2);

    await user.click(within(panel).getByRole("button", { name: "Close" }));
    expect(screen.queryByRole("dialog")).not.toBeInTheDocument();
  });
});

describe("Alerts bell", () => {
  it("shows the number of unread alerts on the bell", async () => {
    render(<DashboardPage />);
    expect(await screen.findByRole("button", { name: "Alerts, 2 unread" })).toBeInTheDocument();
  });

  it("opens a panel of labelled alert cards", async () => {
    const user = userEvent.setup();
    render(<DashboardPage />);
    await user.click(await screen.findByRole("button", { name: "Alerts, 2 unread" }));

    const panel = screen.getByRole("dialog", { name: "Alerts" });
    expect(within(panel).getByRole("tab", { name: "Unread (2)" })).toBeInTheDocument();
    expect(within(panel).getByText("Amina Otieno")).toBeInTheDocument();
    expect(within(panel).getByText("Carol Wanjiku")).toBeInTheDocument();
    expect(within(panel).getAllByText("Email")).toHaveLength(2); // one label per card
  });

  it("lowers the bell number when one alert is marked as read", async () => {
    const user = userEvent.setup();
    render(<DashboardPage />);
    await user.click(await screen.findByRole("button", { name: "Alerts, 2 unread" }));
    await user.click(within(screen.getByRole("dialog")).getAllByRole("button", { name: "Mark as read" })[0]);

    expect(api.markAlertRead).toHaveBeenCalledWith(10);
    expect(await screen.findByRole("button", { name: "Alerts, 1 unread" })).toBeInTheDocument();
  });

  it("removes the badge once everything is marked as read", async () => {
    const user = userEvent.setup();
    render(<DashboardPage />);
    await user.click(await screen.findByRole("button", { name: "Alerts, 2 unread" }));
    await user.click(screen.getByRole("button", { name: "Mark all as read" }));

    expect(api.markAllAlertsRead).toHaveBeenCalled();
    expect(await screen.findByRole("button", { name: "Alerts, none unread" })).toBeInTheDocument();
    expect(screen.getByText("You're all caught up. No unread alerts.")).toBeInTheDocument();
  });

  it("writes a reply draft for an alert", async () => {
    const user = userEvent.setup();
    render(<DashboardPage />);
    await user.click(await screen.findByRole("button", { name: "Alerts, 2 unread" }));
    await user.click(within(screen.getByRole("dialog")).getAllByRole("button", { name: "Write reply" })[0]);

    expect(await screen.findByRole("textbox")).toHaveValue("Hi Amina, we are sorry.");
    expect(api.draftReply).toHaveBeenCalledWith(10);
  });
});
