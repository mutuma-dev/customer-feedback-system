import { render, screen, within } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { beforeEach, describe, expect, it, vi } from "vitest";
import { api, type Alert, type FeedbackResponse } from "@/lib/api";
import DashboardPage from "./page";

vi.mock("@/lib/api", () => ({
  api: {
    stats: vi.fn(),
    trend: vi.fn(),
    responses: vi.fn(),
    alerts: vi.fn(),
    markAlertRead: vi.fn(),
    draftReply: vi.fn(),
  },
}));

const amina: FeedbackResponse = {
  id: 1,
  customer: { id: 1, name: "Amina Otieno", email: "amina@example.com", phone: "+254712345678", kind: "buyer" },
  product_rating: 2,
  care_rating: 3,
  happy_rating: 2,
  mean: 2.33,
  category: "detractor",
  source: "web",
  created_at: "2026-11-12T10:00:00Z",
};
const brian: FeedbackResponse = {
  ...amina,
  id: 2,
  customer: { id: 2, name: "Brian Kamau", email: null, phone: "+254700000000", kind: "painter" },
  product_rating: 5,
  care_rating: 5,
  happy_rating: 4,
  mean: 4.67,
  category: "promoter",
  source: "sms",
};
const alert: Alert = {
  id: 10,
  is_read: false,
  email_sent: true,
  sms_sent: false,
  draft_reply: null,
  created_at: "2026-11-12T10:00:00Z",
  response: amina,
};

beforeEach(() => {
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
  vi.mocked(api.alerts).mockResolvedValue([alert]);
  vi.mocked(api.markAlertRead).mockResolvedValue({ ...alert, is_read: true });
  vi.mocked(api.draftReply).mockResolvedValue({ draft: "Hi Amina, we are sorry.", ai_used: true });
});

describe("Dashboard page", () => {
  it("shows the total number of respondents and the averages", async () => {
    render(<DashboardPage />);
    const card = await screen.findByRole("region", { name: "Total respondents" });
    expect(await within(card).findByText("42")).toBeInTheDocument();
    expect(within(card).getByText(/product 3.9 · care 4.1 · happy 3.8/)).toBeInTheDocument();
  });

  it("shows the customer split, trend and the responses table", async () => {
    render(<DashboardPage />);
    expect(await screen.findByText("Detractors: 5")).toBeInTheDocument();
    expect(screen.getByRole("img", { name: "Daily average score with projection" })).toBeInTheDocument();
    const table = screen.getByRole("table");
    expect(within(table).getByText("Brian Kamau")).toBeInTheDocument();
    expect(within(table).getByText("4.67")).toBeInTheDocument();
  });

  it("lists detractor alerts with name, email and delivery status", async () => {
    render(<DashboardPage />);
    expect(await screen.findByText("Detractor alerts (1 new)")).toBeInTheDocument();
    expect(screen.getByText(/amina@example.com/)).toBeInTheDocument();
    expect(screen.getByText(/email sent · sms not sent/)).toBeInTheDocument();
  });

  it("drills down into one person's ratings as stars", async () => {
    const user = userEvent.setup();
    render(<DashboardPage />);
    await user.click(await screen.findByText("Brian Kamau"));
    const detail = screen.getByRole("region", { name: "Selected customer" });
    expect(within(detail).getAllByRole("img", { name: "5 out of 5 stars" })).toHaveLength(2);
    expect(within(detail).getAllByRole("img", { name: "4 out of 5 stars" })).toHaveLength(1);
    await user.click(within(detail).getByRole("button", { name: "Close" }));
    expect(screen.queryByRole("region", { name: "Selected customer" })).not.toBeInTheDocument();
  });

  it("drafts a reply the care rep can edit before sending", async () => {
    const user = userEvent.setup();
    render(<DashboardPage />);
    await user.click(await screen.findByRole("button", { name: "Draft reply" }));
    const box = await screen.findByRole("textbox");
    expect(box).toHaveValue("Hi Amina, we are sorry.");
    expect(screen.getByText(/AI draft/)).toBeInTheDocument();
    await user.type(box, " Edited.");
    expect(box).toHaveValue("Hi Amina, we are sorry. Edited.");
    expect(screen.getByRole("link", { name: "Open in my email app" })).toHaveAttribute(
      "href",
      expect.stringContaining("mailto:amina@example.com"),
    );
  });

  it("marks an alert handled", async () => {
    const user = userEvent.setup();
    render(<DashboardPage />);
    await user.click(await screen.findByRole("button", { name: "Mark handled" }));
    expect(api.markAlertRead).toHaveBeenCalledWith(10);
  });

  it("explains the problem when the API is unreachable", async () => {
    vi.mocked(api.stats).mockRejectedValue(new Error("down"));
    render(<DashboardPage />);
    expect(await screen.findByRole("alert")).toHaveTextContent("Can't reach the API");
  });

  it("has no link back to the survey (different audiences)", async () => {
    render(<DashboardPage />);
    await screen.findByText("Brian Kamau"); // wait until the data has loaded
    expect(screen.queryByRole("link", { name: /survey/i })).not.toBeInTheDocument();
  });
});
