"use client";

import { useState } from "react";
import type { Alert } from "@/lib/api";
import { AlertCard } from "./AlertCard";
import { SidePanel } from "./SidePanel";

interface AlertsPanelProps {
  open: boolean;
  alerts: Alert[];
  onClose: () => void;
  onMarkRead: (id: number) => void;
  onMarkAllRead: () => void;
  onDraft: (id: number) => Promise<{ draft: string; ai_used: boolean }>;
}

/** The panel that opens from the bell: Unread / All tabs, "Mark all as read" and the cards. */
export function AlertsPanel({
  open,
  alerts,
  onClose,
  onMarkRead,
  onMarkAllRead,
  onDraft,
}: AlertsPanelProps) {
  const [tab, setTab] = useState<"unread" | "all">("unread");

  const unread = alerts.filter((a) => !a.is_read);
  // The Unread tab hides alerts as soon as they are read, like a notification inbox.
  const shown = tab === "unread" ? unread : alerts;

  return (
    <SidePanel title="Alerts" open={open} onClose={onClose}>
      <div className="panel-toolbar">
        <div className="tabs" role="tablist" aria-label="Which alerts to show">
          <button role="tab" aria-selected={tab === "unread"} onClick={() => setTab("unread")}>
            Unread ({unread.length})
          </button>
          <button role="tab" aria-selected={tab === "all"} onClick={() => setTab("all")}>
            All ({alerts.length})
          </button>
        </div>
        <button className="link-btn" onClick={onMarkAllRead} disabled={unread.length === 0}>
          Mark all as read
        </button>
      </div>

      {shown.length === 0 ? (
        <p className="empty">
          {tab === "unread" ? "You're all caught up. No unread alerts." : "No alerts yet."}
        </p>
      ) : (
        <ul className="alert-list">
          {shown.map((alert) => (
            <li key={alert.id}>
              <AlertCard alert={alert} onMarkRead={onMarkRead} onDraft={onDraft} />
            </li>
          ))}
        </ul>
      )}
    </SidePanel>
  );
}
