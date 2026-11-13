import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it, vi } from "vitest";
import { StarRating, StarsDisplay } from "./Stars";

describe("StarRating", () => {
  it("renders five selectable stars inside a labelled group", () => {
    render(<StarRating value={null} onChange={() => {}} label="Rate our care" />);
    expect(screen.getByRole("radiogroup", { name: "Rate our care" })).toBeInTheDocument();
    expect(screen.getAllByRole("radio")).toHaveLength(5);
    expect(screen.getByRole("radio", { name: "1 star" })).toBeInTheDocument();
    expect(screen.getByRole("radio", { name: "5 stars" })).toBeInTheDocument();
  });

  it("calls onChange with the clicked star number", async () => {
    const onChange = vi.fn();
    render(<StarRating value={null} onChange={onChange} label="q" />);
    await userEvent.click(screen.getByRole("radio", { name: "3 stars" }));
    expect(onChange).toHaveBeenCalledWith(3);
  });

  it("marks only the chosen star as checked", () => {
    render(<StarRating value={4} onChange={() => {}} label="q" />);
    expect(screen.getByRole("radio", { name: "4 stars" })).toHaveAttribute("aria-checked", "true");
    expect(screen.getByRole("radio", { name: "2 stars" })).toHaveAttribute("aria-checked", "false");
  });
});

describe("StarsDisplay", () => {
  it("describes the value for screen readers", () => {
    render(<StarsDisplay value={4} />);
    expect(screen.getByRole("img", { name: "4 out of 5 stars" })).toBeInTheDocument();
  });
});
