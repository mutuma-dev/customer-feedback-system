import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { Donut, TrendChart } from "./Charts";

describe("Donut", () => {
  it("shows each group's count and the total", () => {
    render(<Donut detractors={2} passives={3} promoters={5} />);
    expect(screen.getByRole("img")).toHaveAttribute(
      "aria-label",
      "Detractors 2, passives 3, promoters 5",
    );
    expect(screen.getByText("Detractors: 2")).toBeInTheDocument();
    expect(screen.getByText("Passives: 3")).toBeInTheDocument();
    expect(screen.getByText("Promoters: 5")).toBeInTheDocument();
    expect(screen.getByText("10")).toBeInTheDocument(); // total in the middle
  });

  it("draws one arc per group plus the grey track", () => {
    const { container } = render(<Donut detractors={1} passives={1} promoters={1} />);
    expect(container.querySelectorAll("circle")).toHaveLength(4);
  });

  it("draws only the track when there is no data", () => {
    const { container } = render(<Donut detractors={0} passives={0} promoters={0} />);
    expect(container.querySelectorAll("circle")).toHaveLength(1);
    expect(screen.getByText("0")).toBeInTheDocument();
  });
});

describe("TrendChart", () => {
  const points = [
    { date: "2026-11-01", mean: 3.0, count: 4 },
    { date: "2026-11-02", mean: 3.5, count: 6 },
  ];
  const projection = [{ date: "2026-11-03", mean: 3.8 }];

  it("says so when there is no data", () => {
    render(<TrendChart points={[]} projection={[]} />);
    expect(screen.getByText("No data yet.")).toBeInTheDocument();
  });

  it("draws the real line and the dashed projection", () => {
    const { container } = render(<TrendChart points={points} projection={projection} />);
    expect(container.querySelectorAll("polyline")).toHaveLength(2);
    expect(container.querySelectorAll("polyline")[1]).toHaveAttribute("stroke-dasharray");
  });

  it("omits the projection line when there is none", () => {
    const { container } = render(<TrendChart points={points} projection={[]} />);
    expect(container.querySelectorAll("polyline")).toHaveLength(1);
  });

  it("gives every day a tooltip with its response count", () => {
    render(<TrendChart points={points} projection={projection} />);
    expect(screen.getByText("2026-11-02: 3.5 (6 responses)")).toBeInTheDocument();
  });
});
