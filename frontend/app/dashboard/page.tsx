"use client";

import { useCallback, useEffect, useState } from "react";
import { Donut, TrendChart } from "@/components/Charts";
import { api, Alert, FeedbackResponse, Stats, Trend } from "@/lib/api";
import { StarsDisplay } from "@/components/Stars";

const REFRESH_MS = 5000; // the dashboard re-fetches every 5 seconds ("live")

export default function DashboardPage() {
  const [stats, setStats] = useState<Stats | null>(null);
  const [trend, setTrend] = useState<Trend | null>(null);
  const [responses, setResponses] = useState<FeedbackResponse[]>([]);
  const [alerts, setAlerts] = useState<Alert[]>([]);
  const [selected, setSelected] = useState<FeedbackResponse | null>(null);
  const [drafts, setDrafts] = useState<Record<number, { text: string; ai: boolean }>>({});
  const [error, setError] = useState<string | null>(null);

  const load = useCallback(async () => {
    try {
      const [s, t, r, a] = await Promise.all([api.stats(), api.trend(), api.responses(), api.alerts()]);
      setStats(s);
      setTrend(t);
      setResponses(r);
      setAlerts(a);
      setError(null);
    } catch {
      setError("Can't reach the API. Is the backend running on port 8000?");
    }
  }, []);

  useEffect(() => {
    const first = setTimeout(load, 0); // first fetch right away, but not synchronously in the effect
    const id = setInterval(load, REFRESH_MS);
    return () => {
      clearTimeout(first);
      clearInterval(id);
    };
  }, [load]);

  async function draft(alert: Alert) {
    const res = await api.draftReply(alert.id);
    setDrafts((d) => ({ ...d, [alert.id]: { text: res.draft, ai: res.ai_used } }));
  }

  async function markRead(alert: Alert) {
    await api.markAlertRead(alert.id);
    load();
  }

  return (
    <main className="wrap wide">
      <div className="top">
        <p className="brand">Company X</p>
        <h1>Feedback dashboard</h1>
      </div>
      {error && <p className="error" role="alert">{error}</p>}

      <div className="grid">
        <section className="card" aria-label="Total respondents">
          <div className="muted">Total respondents</div>
          <div className="total">{stats?.total ?? "–"}</div>
          {stats && (
            <p className="muted">
              Averages · product {stats.avg_product} · care {stats.avg_care} · happy {stats.avg_happy}
            </p>
          )}
        </section>
        <section className="card" aria-label="Detractors, passives and promoters">
          <h2>Customer split</h2>
          {stats && <Donut detractors={stats.detractors} passives={stats.passives} promoters={stats.promoters} />}
        </section>
      </div>

      <section className="card" style={{ marginTop: 16 }} aria-label="Trend">
        <h2>Daily trend and 7-day projection</h2>
        {trend && <TrendChart points={trend.points} projection={trend.projection} />}
      </section>

      <div className="grid">
        <section className="card" aria-label="Alerts">
          <h2>Detractor alerts ({alerts.filter((a) => !a.is_read).length} new)</h2>
          {alerts.length === 0 && <p className="muted">No alerts. 🎉</p>}
          {alerts.map((a) => {
            const c = a.response.customer;
            const d = drafts[a.id] ?? (a.draft_reply ? { text: a.draft_reply, ai: false } : null);
            const mailto = c.email
              ? `mailto:${c.email}?subject=${encodeURIComponent("About your feedback")}&body=${encodeURIComponent(d?.text ?? "")}`
              : null;
            return (
              <div key={a.id} className={`alert ${a.is_read ? "read" : ""}`}>
                <strong>{c.name}</strong> · mean {a.response.mean.toFixed(2)}{" "}
                <span className="muted">
                  ({a.response.product_rating}/{a.response.care_rating}/{a.response.happy_rating})
                </span>
                <div className="muted">
                  {c.email ?? "no email"} · {c.phone ?? "no phone"} · via {a.response.source}
                  {" · "}email {a.email_sent ? "sent" : "not sent"} · sms {a.sms_sent ? "sent" : "not sent"}
                </div>
                <div className="row-actions">
                  <button className="btn small" onClick={() => draft(a)}>Draft reply</button>
                  {!a.is_read && (
                    <button className="btn small outline" onClick={() => markRead(a)}>Mark handled</button>
                  )}
                </div>
                {d && (
                  <>
                    <label htmlFor={`draft-${a.id}`} className="muted">
                      {d.ai ? "AI draft" : "Template draft"} - edit before sending
                    </label>
                    <textarea
                      id={`draft-${a.id}`}
                      value={d.text}
                      onChange={(e) => setDrafts((all) => ({ ...all, [a.id]: { ...d, text: e.target.value } }))}
                    />
                    <div className="row-actions">
                      {mailto ? <a href={mailto}>Open in my email app</a> : c.phone && <a href={`tel:${c.phone}`}>Call {c.phone}</a>}
                    </div>
                  </>
                )}
              </div>
            );
          })}
        </section>

        <section className="card" aria-label="Individual ratings">
          <h2>Individual ratings</h2>
          {selected && (
            <div className="detail" role="region" aria-label="Selected customer">
              <strong>{selected.customer.name}</strong>{" "}
              <span className={`pill ${selected.category}`}>{selected.category}</span>
              <div className="detail-row"><span>Product experience</span><StarsDisplay value={selected.product_rating} /></div>
              <div className="detail-row"><span>Customer care</span><StarsDisplay value={selected.care_rating} /></div>
              <div className="detail-row"><span>Happy with product</span><StarsDisplay value={selected.happy_rating} /></div>
              <button className="btn small outline" onClick={() => setSelected(null)}>Close</button>
            </div>
          )}
          <table>
            <thead>
              <tr><th>Customer</th><th>Mean</th><th>Verdict</th></tr>
            </thead>
            <tbody>
              {responses.map((r) => (
                <tr
                  key={r.id}
                  className="row"
                  tabIndex={0}
                  onClick={() => setSelected(r)}
                  onKeyDown={(e) => e.key === "Enter" && setSelected(r)}
                >
                  <td>{r.customer.name}</td>
                  <td>{r.mean.toFixed(2)}</td>
                  <td><span className={`pill ${r.category}`}>{r.category}</span></td>
                </tr>
              ))}
            </tbody>
          </table>
        </section>
      </div>
    </main>
  );
}
