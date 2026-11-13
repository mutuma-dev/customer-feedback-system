// Tests for the bell with the unread badge.
import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it, vi } from "vitest";
import { NotificationBell } from "./NotificationBell";

describe("NotificationBell", () => {
  it("shows the unread number on a badge and announces it", () => {
    render(<NotificationBell unread={3} onClick={() => {}} />);
    expect(screen.getByRole("button", { name: "Alerts, 3 unread" })).toBeInTheDocument();
    expect(screen.getByText("3")).toBeInTheDocument();
  });

  it("hides the badge completely when everything is read", () => {
    render(<NotificationBell unread={0} onClick={() => {}} />);
    expect(screen.getByRole("button", { name: "Alerts, none unread" })).toBeInTheDocument();
    expect(screen.queryByText("0")).not.toBeInTheDocument();
  });

  it("caps large numbers at 9+", () => {
    render(<NotificationBell unread={25} onClick={() => {}} />);
    expect(screen.getByText("9+")).toBeInTheDocument();
  });

  it("calls onClick when pressed", async () => {
    const onClick = vi.fn();
    render(<NotificationBell unread={1} onClick={onClick} />);
    await userEvent.click(screen.getByRole("button"));
    expect(onClick).toHaveBeenCalledTimes(1);
  });
});
