import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { beforeEach, describe, expect, it, vi } from "vitest";
import { api } from "@/lib/api";
import SurveyPage from "./page";

vi.mock("@/lib/api", () => ({ api: { submitFeedback: vi.fn() } }));

async function answer(user: ReturnType<typeof userEvent.setup>, stars: number, next: string) {
  await user.click(screen.getByRole("radio", { name: `${stars} ${stars === 1 ? "star" : "stars"}` }));
  await user.click(screen.getByRole("button", { name: next }));
}

beforeEach(() => {
  vi.mocked(api.submitFeedback).mockReset();
  vi.mocked(api.submitFeedback).mockResolvedValue({
    id: 1,
    mean: 4.33,
    category: "promoter",
    alert_created: false,
  });
});

describe("Survey page", () => {
  it("starts on question 1 with the Next button disabled", () => {
    render(<SurveyPage />);
    expect(screen.getByText("Question 1 of 3")).toBeInTheDocument();
    expect(screen.getByRole("heading", { name: "Rate your experience with our product." })).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "Next question" })).toBeDisabled();
  });

  it("shows a text label for the chosen rating and enables Next", async () => {
    const user = userEvent.setup();
    render(<SurveyPage />);
    await user.click(screen.getByRole("radio", { name: "4 stars" }));
    expect(screen.getByText("Very good")).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "Next question" })).toBeEnabled();
  });

  it("accepts the 1-5 keyboard shortcut", async () => {
    const user = userEvent.setup();
    render(<SurveyPage />);
    await user.keyboard("5");
    expect(screen.getByText("Excellent")).toBeInTheDocument();
  });

  it("goes through three questions, collects details and submits everything", async () => {
    const user = userEvent.setup();
    render(<SurveyPage />);

    await answer(user, 5, "Next question");
    expect(screen.getByText("Question 2 of 3")).toBeInTheDocument();
    await answer(user, 4, "Next question");
    expect(screen.getByText("Question 3 of 3")).toBeInTheDocument();
    await answer(user, 5, "Continue");

    await user.type(screen.getByLabelText("Full name"), "Amina Otieno");
    await user.type(screen.getByLabelText("Email"), "amina@example.com");
    await user.type(screen.getByLabelText("Phone (optional)"), "+254712345678");
    await user.click(screen.getByLabelText("I'm a professional painter"));
    await user.click(screen.getByRole("button", { name: "Submit feedback" }));

    expect(api.submitFeedback).toHaveBeenCalledWith({
      name: "Amina Otieno",
      email: "amina@example.com",
      phone: "+254712345678",
      kind: "painter",
      product_rating: 5,
      care_rating: 4,
      happy_rating: 5,
    });
    expect(await screen.findByRole("heading", { name: "Thank you, Amina" })).toBeInTheDocument();
  });

  it("lets the person go back and change an answer", async () => {
    const user = userEvent.setup();
    render(<SurveyPage />);
    await answer(user, 3, "Next question");
    await user.click(screen.getByRole("button", { name: "Back" }));
    expect(screen.getByText("Question 1 of 3")).toBeInTheDocument();
    expect(screen.getByRole("radio", { name: "3 stars" })).toHaveAttribute("aria-checked", "true");
  });

  it("shows a friendly error and keeps the form when sending fails", async () => {
    vi.mocked(api.submitFeedback).mockRejectedValue(new Error("network"));
    const user = userEvent.setup();
    render(<SurveyPage />);
    await answer(user, 2, "Next question");
    await answer(user, 2, "Next question");
    await answer(user, 2, "Continue");
    await user.type(screen.getByLabelText("Full name"), "Amina");
    await user.type(screen.getByLabelText("Email"), "a@x.com");
    await user.click(screen.getByRole("button", { name: "Submit feedback" }));

    expect(await screen.findByRole("alert")).toHaveTextContent("We couldn't send your feedback");
    expect(screen.getByLabelText("Full name")).toHaveValue("Amina");
  });

  it("has no link to the dashboard (different audiences)", () => {
    render(<SurveyPage />);
    expect(screen.queryByRole("link")).not.toBeInTheDocument();
  });
});
