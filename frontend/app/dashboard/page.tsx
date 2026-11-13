"use client"; // uses state, timers and clicks, so it runs in the browser

// THE DASHBOARD (route "/dashboard"). What Company X staff see:
//   header with the alerts bell -> summary cards -> trend chart -> recent responses table.
// There is deliberately NO link back to the survey: customers and staff are different people.

import { useCallback, useEffect, useState } from "react";
import { AlertsPanel } from "@/components/AlertsPanel";
import { Donut, TrendChart } from "@/components/Charts";
import { NotificationBell } from "@/components/NotificationBell";
import { ResponseDetail } from "@/components/ResponseDetail";
import { StarsDisplay } from "@/components/Stars";
import { api, type Alert, type FeedbackResponse, type Stats, type Trend } from "@/lib/api";
import { categoryLabel, timeAgo } from "@/lib/format";

const REFRESH_MS = 5000; // the dashboard asks the backend for fresh data every 5 seconds

export default function DashboardPage() {
  // ---- Data from the backend (null / empty until the first answer arrives) ----
  const [stats, setStats] = useState<Stats | null>(null);
  const [trend, setTrend] = useState<Trend | null>(null);
  const [responses, setResponses] = useState<FeedbackResponse[]>([]);
  const [alerts, setAlerts] = useState<Alert[]>([]);
  // ---- What the user has opened ----
  const [panelOpen, setPanelOpen] = useState(false); // the alerts panel
  const [selected, setSelected] = useState<FeedbackResponse | null>(null); // response details
  // ---- Error banner ----
  const [error, setError] = useState<string | null>(null);

  // The number on the bell: alerts that have not been marked as read.
  const unreadCount = alerts.filter((a) => !a.is_read).length;

  /** Fetch everything from the backend (4 requests at the same time). */
  const load = useCallback(async () => {
    try {
      const [s, t, r, a] = await Promise.all([
        api.stats(),
        api.trend(),
        api.responses(),
        api.alerts(),
      ]);
      setStats(s);
      setTrend(t);
      setResponses(r);
      setAlerts(a);
      setError(null);
    } catch {
      setError("Can't reach the API. Is the backend running on port 8000?");
    }
  }, []);

  // Load once straight away, then again every 5 seconds ("live" dashboard).
  useEffect(() => {
    const first = setTimeout(load, 0); // first load (a timer keeps the effect itself simple)
    const id = setInterval(load, REFRESH_MS);
    return () => {
      // cleanup when leaving the page, so timers do not keep running
      clearTimeout(first);
      clearInterval(id);
    };
  }, [load]);

  /** Mark ONE alert as read. The bell number drops immediately, then we sync with the server. */
  async function markRead(id: number) {
    setAlerts((all) => all.map((a) => (a.id === id ? { ...a, is_read: true } : a)));
    try {
      await api.markAlertRead(id);
    } finally {
      await load(); // either way, show what the server really has
    }
  }

  /** Mark EVERY alert as read. */
  async function markAllRead() {
    setAlerts((all) => all.map((a) => ({ ...a, is_read: true })));
    try {
      await api.markAllAlertsRead();
    } finally {
      await load();
    }
  }

  return (
    <main className="wrap dash">
      {/* ================= Header: title + alerts bell ================= */}
      <header className="dash-header">
        <div>
          <p className="brand">Company X</p>
          <h1>Feedback dashboard</h1>
        </div>
        <NotificationBell unread={unreadCount} onClick={() => setPanelOpen(true)} />
      </header>

      {error && (
        <p className="error" role="alert">
          {error}
        </p>
      )}

      {/* ================= Summary cards ================= */}
      <div className="dash-grid">
        <section className="card" aria-label="Total respondents">
          <h2>Total respondents</h2>
          <div className="big-number">{stats?.total ?? "–"}</div>
          <p className="muted">people have given feedback</p>
        </section>

        <section className="card" aria-label="Average ratings">
          <h2>Average ratings</h2>
          {stats ? (
            <>
              <p className="avg-overall">
                <strong>{stats.avg_mean.toFixed(2)}</strong> / 5 overall
              </p>
              <dl className="fields">
                <div>
                  <dt>Product</dt>
                  <dd>
                    <StarsDisplay value={Math.round(stats.avg_product)} /> {stats.avg_product}
                  </dd>
                </div>
                <div>
                  <dt>Customer care</dt>
                  <dd>
                    <StarsDisplay value={Math.round(stats.avg_care)} /> {stats.avg_care}
                  </dd>
                </div>
                <div>
                  <dt>Happiness</dt>
                  <dd>
                    <StarsDisplay value={Math.round(stats.avg_happy)} /> {stats.avg_happy}
                  </dd>
                </div>
              </dl>
            </>
          ) : (
            <p className="muted">Loading…</p>
          )}
        </section>

        <section className="card" aria-label="How customers feel">
          <h2>How customers feel</h2>
          <p className="muted">Share of unhappy, neutral and happy customers</p>
          {stats && (
            <Donut
              detractors={stats.detractors}
              passives={stats.passives}
              promoters={stats.promoters}
            />
          )}
        </section>
      </div>

      {/* ================= Trend ================= */}
      <section className="card spaced" aria-label="Satisfaction over time">
        <h2>Satisfaction over time</h2>
        <p className="muted">Daily average score (1-5). The dashed line is a 7-day forecast.</p>
        {trend && <TrendChart points={trend.points} projection={trend.projection} />}
      </section>

      {/* ================= Recent responses ================= */}
      <section className="card spaced" aria-label="Recent responses">
        <h2>Recent responses</h2>
        <p className="muted">Tap a row to see the full ratings.</p>
        {/* table-wrap lets the table scroll sideways on very small screens */}
        <div className="table-wrap">
          <table>
            <thead>
              <tr>
                <th>Customer</th>
                <th>Average</th>
                <th>Feeling</th>
                <th className="hide-xs">When</th>
              </tr>
            </thead>
            <tbody>
              {responses.map((r) => (
                <tr
                  key={r.id}
                  className="row"
                  tabIndex={0} // reachable with the Tab key
                  onClick={() => setSelected(r)}
                  onKeyDown={(e) => e.key === "Enter" && setSelected(r)}
                >
                  <td>{r.customer.name}</td>
                  <td>{r.mean.toFixed(2)}</td>
                  <td>
                    <span className={`pill ${r.category}`}>{categoryLabel(r.category)}</span>
                  </td>
                  <td className="hide-xs">{timeAgo(r.created_at)}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </section>

      {/* ================= Panels (hidden until opened) ================= */}
      <AlertsPanel
        open={panelOpen}
        alerts={alerts}
        onClose={() => setPanelOpen(false)}
        onMarkRead={markRead}
        onMarkAllRead={markAllRead}
        onDraft={api.draftReply}
      />
      <ResponseDetail response={selected} onClose={() => setSelected(null)} />
    </main>
  );
}
