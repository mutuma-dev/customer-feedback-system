// Tests for the slide-in panel.
import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it, vi } from "vitest";
import { SidePanel } from "./SidePanel";

describe("SidePanel", () => {
  it("renders nothing while closed", () => {
    render(
      <SidePanel title="Alerts" open={false} onClose={() => {}}>
        content
      </SidePanel>,
    );
    expect(screen.queryByRole("dialog")).not.toBeInTheDocument();
  });

  it("shows a labelled dialog with its content when open", () => {
    render(
      <SidePanel title="Alerts" open onClose={() => {}}>
        <p>inside</p>
      </SidePanel>,
    );
    expect(screen.getByRole("dialog", { name: "Alerts" })).toBeInTheDocument();
    expect(screen.getByText("inside")).toBeInTheDocument();
  });

  it("closes with the X button and with the Escape key", async () => {
    const onClose = vi.fn();
    render(
      <SidePanel title="Alerts" open onClose={onClose}>
        x
      </SidePanel>,
    );
    await userEvent.click(screen.getByRole("button", { name: "Close" }));
    expect(onClose).toHaveBeenCalledTimes(1);
    await userEvent.keyboard("{Escape}");
    expect(onClose).toHaveBeenCalledTimes(2);
  });

  it("closes when the dark background is clicked, but not when the panel itself is", async () => {
    const onClose = vi.fn();
    const { container } = render(
      <SidePanel title="Alerts" open onClose={onClose}>
        <p>inside</p>
      </SidePanel>,
    );
    await userEvent.click(screen.getByText("inside")); // inside the panel: stays open
    expect(onClose).not.toHaveBeenCalled();
    await userEvent.click(container.querySelector(".panel-overlay") as HTMLElement);
    expect(onClose).toHaveBeenCalledTimes(1);
  });

  it("locks page scrolling while open and restores it afterwards", () => {
    const { unmount } = render(
      <SidePanel title="Alerts" open onClose={() => {}}>
        x
      </SidePanel>,
    );
    expect(document.body.style.overflow).toBe("hidden");
    unmount();
    expect(document.body.style.overflow).not.toBe("hidden");
  });
});
