// Tests for the alerts panel opened from the bell.
import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it, vi } from "vitest";
import { makeAlert, makeResponse } from "@/lib/testData";
import { AlertsPanel } from "./AlertsPanel";

const person = (id: number, name: string) => ({
  id,
  name,
  email: `${name.toLowerCase()}@example.com`,
  phone: null,
  kind: "buyer",
});

// Two unread alerts and one already read.
const alerts = [
  makeAlert({ id: 1, response: makeResponse({ id: 1, customer: person(1, "Amina") }) }),
  makeAlert({ id: 2, response: makeResponse({ id: 2, customer: person(2, "Brian") }) }),
  makeAlert({ id: 3, is_read: true, response: makeResponse({ id: 3, customer: person(3, "Carol") }) }),
];

function setup(list = alerts, open = true) {
  const handlers = {
    onClose: vi.fn(),
    onMarkRead: vi.fn(),
    onMarkAllRead: vi.fn(),
    onDraft: vi.fn(),
  };
  render(<AlertsPanel open={open} alerts={list} {...handlers} />);
  return handlers;
}

describe("AlertsPanel", () => {
  it("renders nothing while closed", () => {
    setup(alerts, false);
    expect(screen.queryByRole("dialog")).not.toBeInTheDocument();
  });

  it("starts on the Unread tab, showing only unread alerts, with counts on the tabs", () => {
    setup();
    expect(screen.getByRole("tab", { name: "Unread (2)" })).toHaveAttribute("aria-selected", "true");
    expect(screen.getByRole("tab", { name: "All (3)" })).toBeInTheDocument();
    expect(screen.getByText("Amina")).toBeInTheDocument();
    expect(screen.getByText("Brian")).toBeInTheDocument();
    expect(screen.queryByText("Carol")).not.toBeInTheDocument();
  });

  it("shows read alerts as well on the All tab", async () => {
    setup();
    await userEvent.click(screen.getByRole("tab", { name: "All (3)" }));
    expect(screen.getByText("Carol")).toBeInTheDocument();
    expect(screen.getByText("✓ Read")).toBeInTheDocument();
  });

  it("marks all as read with one click", async () => {
    const { onMarkAllRead } = setup();
    await userEvent.click(screen.getByRole("button", { name: "Mark all as read" }));
    expect(onMarkAllRead).toHaveBeenCalledTimes(1);
  });

  it("passes a single 'Mark as read' click up with the alert's id", async () => {
    const { onMarkRead } = setup();
    await userEvent.click(screen.getAllByRole("button", { name: "Mark as read" })[0]);
    expect(onMarkRead).toHaveBeenCalledWith(1);
  });

  it("shows a friendly message and disables 'Mark all' when nothing is unread", () => {
    setup([makeAlert({ is_read: true })]);
    expect(screen.getByText("You're all caught up. No unread alerts.")).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "Mark all as read" })).toBeDisabled();
  });

  it("says so when there are no alerts at all", async () => {
    setup([]);
    await userEvent.click(screen.getByRole("tab", { name: "All (0)" }));
    expect(screen.getByText("No alerts yet.")).toBeInTheDocument();
  });
});
