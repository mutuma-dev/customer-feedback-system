// Tests for one alert card: labelled details, delivery chips and the actions.
import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it, vi } from "vitest";
import { makeAlert, makeResponse } from "@/lib/testData";
import { AlertCard } from "./AlertCard";

/** Render a card with fake handlers, and return them so tests can check how they were used. */
function setup(alertOverrides = {}, draft = { draft: "Hi Amina, we are sorry.", ai_used: true }) {
  const onMarkRead = vi.fn();
  const onDraft = vi.fn().mockResolvedValue(draft);
  render(<AlertCard alert={makeAlert(alertOverrides)} onMarkRead={onMarkRead} onDraft={onDraft} />);
  return { onMarkRead, onDraft };
}

describe("AlertCard details", () => {
  it("shows the customer's details under clear labels", () => {
    setup();
    expect(screen.getByRole("heading", { name: "Amina Otieno" })).toBeInTheDocument();
    expect(screen.getByText("Email")).toBeInTheDocument();
    expect(screen.getByText("amina@example.com")).toBeInTheDocument();
    expect(screen.getByText("Phone")).toBeInTheDocument();
    expect(screen.getByText("+254712345678")).toBeInTheDocument();
    expect(screen.getByText("Answered via")).toBeInTheDocument();
    expect(screen.getByText("Web form")).toBeInTheDocument();
  });

  it("shows the overall score, the verdict and the three ratings as stars", () => {
    setup();
    expect(screen.getByText("2.33")).toBeInTheDocument();
    expect(screen.getByText("Unhappy")).toBeInTheDocument();
    expect(screen.getByText("Product")).toBeInTheDocument();
    expect(screen.getByText("Customer care")).toBeInTheDocument();
    expect(screen.getByText("Happiness")).toBeInTheDocument();
    expect(screen.getAllByRole("img", { name: /out of 5 stars/ })).toHaveLength(3);
  });

  it("says plainly whether the email and the SMS reached the care team", () => {
    setup({ email_sent: true, sms_sent: false });
    expect(screen.getByText("Email sent")).toBeInTheDocument();
    expect(screen.getByText("SMS not sent")).toBeInTheDocument();
  });

  it("shows 'Not provided' for a missing email or phone (painters who used SMS)", () => {
    setup({
      response: makeResponse({
        source: "sms",
        customer: { id: 2, name: "Painter +254700000000", email: null, phone: "+254700000000", kind: "painter" },
      }),
    });
    expect(screen.getByText("Not provided")).toBeInTheDocument();
    expect(screen.getByText("SMS reply")).toBeInTheDocument();
  });
});

describe("AlertCard read state", () => {
  it("an unread alert has an unread dot and a Mark as read button", async () => {
    const { onMarkRead } = setup();
    expect(screen.getByRole("img", { name: "Unread" })).toBeInTheDocument();
    await userEvent.click(screen.getByRole("button", { name: "Mark as read" }));
    expect(onMarkRead).toHaveBeenCalledWith(10);
  });

  it("a read alert shows a Read label instead, with no dot and no button", () => {
    setup({ is_read: true });
    expect(screen.getByText("✓ Read")).toBeInTheDocument();
    expect(screen.queryByRole("button", { name: "Mark as read" })).not.toBeInTheDocument();
    expect(screen.queryByRole("img", { name: "Unread" })).not.toBeInTheDocument();
  });
});

describe("AlertCard reply", () => {
  it("writes an editable AI draft and offers to open it in the email app", async () => {
    const { onDraft } = setup();
    await userEvent.click(screen.getByRole("button", { name: "Write reply" }));

    const box = await screen.findByRole("textbox");
    expect(onDraft).toHaveBeenCalledWith(10);
    expect(box).toHaveValue("Hi Amina, we are sorry.");
    expect(screen.getByText(/AI draft/)).toBeInTheDocument();

    await userEvent.type(box, " Edited.");
    expect(box).toHaveValue("Hi Amina, we are sorry. Edited.");
    expect(screen.getByRole("link", { name: "Open in email app" })).toHaveAttribute(
      "href",
      expect.stringContaining("mailto:amina@example.com"),
    );
  });

  it("labels a template draft honestly", async () => {
    setup({}, { draft: "Template text", ai_used: false });
    await userEvent.click(screen.getByRole("button", { name: "Write reply" }));
    expect(await screen.findByText(/Template draft/)).toBeInTheDocument();
  });

  it("re-uses a draft saved earlier instead of calling the AI again", async () => {
    const { onDraft } = setup({ draft_reply: "Saved text" });
    await userEvent.click(screen.getByRole("button", { name: "Write reply" }));
    expect(await screen.findByRole("textbox")).toHaveValue("Saved text");
    expect(screen.getByText(/Saved draft/)).toBeInTheDocument();
    expect(onDraft).not.toHaveBeenCalled();
  });

  it("offers a call link when the customer has no email", async () => {
    setup({
      response: makeResponse({
        customer: { id: 2, name: "Joseph", email: null, phone: "+254700000000", kind: "painter" },
      }),
    });
    await userEvent.click(screen.getByRole("button", { name: "Write reply" }));
    expect(await screen.findByRole("link", { name: "Call customer" })).toHaveAttribute(
      "href",
      "tel:+254700000000",
    );
  });

  it("shows an error if the draft cannot be written", async () => {
    const onDraft = vi.fn().mockRejectedValue(new Error("down"));
    render(<AlertCard alert={makeAlert()} onMarkRead={() => {}} onDraft={onDraft} />);
    await userEvent.click(screen.getByRole("button", { name: "Write reply" }));
    expect(await screen.findByRole("alert")).toHaveTextContent("Couldn't write a draft");
  });

  it("closes the reply box without marking the alert as read", async () => {
    const { onMarkRead } = setup();
    await userEvent.click(screen.getByRole("button", { name: "Write reply" }));
    await screen.findByRole("textbox");
    await userEvent.click(screen.getByRole("button", { name: "Close" }));
    expect(screen.queryByRole("textbox")).not.toBeInTheDocument();
    expect(onMarkRead).not.toHaveBeenCalled();
  });
});
