// Tests for the response details panel (opened from the table).
import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it, vi } from "vitest";
import { makeResponse } from "@/lib/testData";
import { ResponseDetail } from "./ResponseDetail";

describe("ResponseDetail", () => {
  it("is closed when no response is selected", () => {
    render(<ResponseDetail response={null} onClose={() => {}} />);
    expect(screen.queryByRole("dialog")).not.toBeInTheDocument();
  });

  it("shows every detail under a label, with the ratings as stars", () => {
    render(<ResponseDetail response={makeResponse({ source: "sms" })} onClose={() => {}} />);
    expect(screen.getByRole("dialog", { name: "Response details" })).toBeInTheDocument();
    expect(screen.getByText("Amina Otieno")).toBeInTheDocument();
    expect(screen.getByText("Unhappy")).toBeInTheDocument();
    for (const label of ["Email", "Phone", "Customer type", "Answered via", "Submitted"]) {
      expect(screen.getByText(label)).toBeInTheDocument();
    }
    expect(screen.getByText("SMS reply")).toBeInTheDocument();
    expect(screen.getByText("Paint buyer")).toBeInTheDocument();
    expect(screen.getByText("2.33 / 5")).toBeInTheDocument();
    expect(screen.getAllByRole("img", { name: /out of 5 stars/ })).toHaveLength(3);
  });

  it("calls onClose from the Close button", async () => {
    const onClose = vi.fn();
    render(<ResponseDetail response={makeResponse()} onClose={onClose} />);
    await userEvent.click(screen.getByRole("button", { name: "Close" }));
    expect(onClose).toHaveBeenCalled();
  });
});
