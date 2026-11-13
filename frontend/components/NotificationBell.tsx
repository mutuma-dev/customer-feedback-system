interface NotificationBellProps {
  unread: number; // number of unread alerts
  onClick: () => void; // opens the alerts panel
}

/**
 * The bell icon in the dashboard header. A red badge shows how many alerts are unread.
 * When everything is read the badge disappears, like a normal notification bell.
 */
export function NotificationBell({ unread, onClick }: NotificationBellProps) {
  // Very large numbers are shortened so the badge stays small.
  const badge = unread > 9 ? "9+" : String(unread);
  return (
    <button
      type="button"
      className="bell"
      onClick={onClick}
      // Screen readers cannot see the red badge, so the number is part of the label.
      aria-label={unread > 0 ? `Alerts, ${unread} unread` : "Alerts, none unread"}
    >
      {/* The bell picture (decorative). */}
      <svg viewBox="0 0 24 24" width="24" height="24" aria-hidden="true">
        <path
          d="M6 9a6 6 0 1 1 12 0c0 3.5 1 5 2 6H4c1-1 2-2.5 2-6z M10 19a2 2 0 0 0 4 0"
          fill="none"
          stroke="currentColor"
          strokeWidth="1.8"
          strokeLinecap="round"
          strokeLinejoin="round"
        />
      </svg>
      {/* Only drawn when there is something unread. */}
      {unread > 0 && (
        <span className="bell-badge" aria-hidden="true">
          {badge}
        </span>
      )}
    </button>
  );
}
