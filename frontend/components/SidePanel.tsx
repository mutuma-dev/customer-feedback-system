"use client";

import { useEffect, useRef, type ReactNode } from "react";

interface SidePanelProps {
  title: string; // shown in the header and read by screen readers
  open: boolean; // the panel renders nothing while this is false
  onClose: () => void;
  children: ReactNode; // whatever goes inside the panel
}

/**
 * A panel that slides in over the page: full width on phones, a 440px column on bigger screens.
 * Closes with the X button, the Escape key, or a click on the dark background.
 */
export function SidePanel({ title, open, onClose, children }: SidePanelProps) {
  const closeButton = useRef<HTMLButtonElement>(null);

  // Keep the latest onClose in a "ref", so the effect below does not restart (and steal the
  // keyboard focus) every time the parent page re-renders, e.g. during the 5-second refresh.
  const latestOnClose = useRef(onClose);
  useEffect(() => {
    latestOnClose.current = onClose;
  }, [onClose]);

  useEffect(() => {
    if (!open) return;
    // Escape closes the panel.
    const onKey = (e: KeyboardEvent) => {
      if (e.key === "Escape") latestOnClose.current();
    };
    window.addEventListener("keydown", onKey);
    // Stop the page behind from scrolling while the panel is open.
    const previousOverflow = document.body.style.overflow;
    document.body.style.overflow = "hidden";
    // Move keyboard focus into the panel.
    closeButton.current?.focus();
    // Cleanup: undo everything when the panel closes.
    return () => {
      window.removeEventListener("keydown", onKey);
      document.body.style.overflow = previousOverflow;
    };
  }, [open]);

  if (!open) return null;

  return (
    // The dark background. Clicking it closes the panel.
    <div className="panel-overlay" onClick={onClose}>
      <aside
        className="panel"
        role="dialog"
        aria-modal="true"
        aria-label={title}
        // Clicks inside the panel must NOT reach the background (which would close it).
        onClick={(e) => e.stopPropagation()}
      >
        <header className="panel-head">
          <h2>{title}</h2>
          <button ref={closeButton} className="icon-btn" aria-label="Close" onClick={onClose}>
            ×
          </button>
        </header>
        <div className="panel-body">{children}</div>
      </aside>
    </div>
  );
}
