"use client";

import { useState } from "react";
import type { Alert } from "@/lib/api";
import { categoryLabel, sourceLabel, timeAgo } from "@/lib/format";
import { StarsDisplay } from "./Stars";

interface AlertCardProps {
  alert: Alert;
  onMarkRead: (id: number) => void; // the parent updates the data and the bell count
  // Asks the backend for a reply draft. The parent supplies the real function (tests supply a fake).
  onDraft: (id: number) => Promise<{ draft: string; ai_used: boolean }>;
}

/** The text of the draft: where it came from, and what the rep can edit. */
interface Reply {
  text: string;
  ai: boolean | null; // true = AI wrote it, false = built-in template, null = saved earlier
}

/**
 * One alert, laid out with labels: who the customer is, how to reach them, their ratings,
 * whether the email/SMS reached the care team, and the actions (write reply, mark as read).
 */
export function AlertCard({ alert, onMarkRead, onDraft }: AlertCardProps) {
  const { response } = alert;
  const customer = response.customer;

  // null = the reply box is closed.
  const [reply, setReply] = useState<Reply | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  /** Ask the backend (AI or template) to write a draft. */
  async function generate() {
    setLoading(true);
    setError(null);
    try {
      const result = await onDraft(alert.id);
      setReply({ text: result.draft, ai: result.ai_used });
    } catch {
      setError("Couldn't write a draft. Please try again.");
    } finally {
      setLoading(false); // runs whether it worked or failed
    }
  }

  /** "Write reply": reuse a draft saved earlier, otherwise generate a new one. */
  function openReply() {
    if (alert.draft_reply) setReply({ text: alert.draft_reply, ai: null });
    else void generate();
  }

  // A link that opens the rep's own email app with the (edited) draft already filled in.
  const mailto = customer.email
    ? `mailto:${customer.email}?subject=${encodeURIComponent("About your feedback")}` +
      `&body=${encodeURIComponent(reply?.text ?? "")}`
    : null;

  return (
    <article className={`alert-card ${alert.is_read ? "is-read" : "is-unread"}`}>
      {/* ---- Top row: name (with an unread dot) and how long ago ---- */}
      <header className="alert-card-head">
        <div className="alert-title">
          {!alert.is_read && <span className="unread-dot" role="img" aria-label="Unread" />}
          <h3>{customer.name}</h3>
        </div>
        <span className="alert-time">{timeAgo(alert.created_at)}</span>
      </header>

      {/* ---- Overall score and verdict ---- */}
      <p className="alert-score">
        <strong>{response.mean.toFixed(2)}</strong> / 5 average
        <span className="chip chip-bad">{categoryLabel(response.category)}</span>
      </p>

      {/* ---- Labelled contact details ---- */}
      <dl className="fields">
        <div>
          <dt>Email</dt>
          <dd>{customer.email ?? <span className="muted">Not provided</span>}</dd>
        </div>
        <div>
          <dt>Phone</dt>
          <dd>{customer.phone ?? <span className="muted">Not provided</span>}</dd>
        </div>
        <div>
          <dt>Answered via</dt>
          <dd>{sourceLabel(response.source)}</dd>
        </div>
      </dl>

      {/* ---- Labelled ratings ---- */}
      <dl className="fields">
        <div>
          <dt>Product</dt>
          <dd>
            <StarsDisplay value={response.product_rating} />
          </dd>
        </div>
        <div>
          <dt>Customer care</dt>
          <dd>
            <StarsDisplay value={response.care_rating} />
          </dd>
        </div>
        <div>
          <dt>Happiness</dt>
          <dd>
            <StarsDisplay value={response.happy_rating} />
          </dd>
        </div>
      </dl>

      {/* ---- Did the alert reach the care team? ---- */}
      <ul className="chips" aria-label="Delivery status">
        <li className={`chip ${alert.email_sent ? "chip-ok" : "chip-muted"}`}>
          {alert.email_sent ? "Email sent" : "Email not sent"}
        </li>
        <li className={`chip ${alert.sms_sent ? "chip-ok" : "chip-muted"}`}>
          {alert.sms_sent ? "SMS sent" : "SMS not sent"}
        </li>
      </ul>

      {/* ---- Actions ---- */}
      <div className="card-actions">
        <button className="btn small" onClick={openReply} disabled={loading}>
          {loading ? "Writing…" : "Write reply"}
        </button>
        {alert.is_read ? (
          <span className="read-label">✓ Read</span>
        ) : (
          <button className="btn small outline" onClick={() => onMarkRead(alert.id)}>
            Mark as read
          </button>
        )}
      </div>
      {error && (
        <p className="error" role="alert">
          {error}
        </p>
      )}

      {/* ---- The reply box (only after "Write reply") ---- */}
      {reply && (
        <section className="reply" aria-label="Reply draft">
          <label htmlFor={`reply-${alert.id}`}>
            {reply.ai === true ? "AI draft" : reply.ai === false ? "Template draft" : "Saved draft"}
            {" · edit before sending"}
          </label>
          <textarea
            id={`reply-${alert.id}`}
            value={reply.text}
            onChange={(e) => setReply({ ...reply, text: e.target.value })}
          />
          <div className="card-actions">
            {/* Nothing is sent automatically: the care rep sends it from their own email app. */}
            {mailto ? (
              <a className="btn small" href={mailto}>
                Open in email app
              </a>
            ) : customer.phone ? (
              <a className="btn small" href={`tel:${customer.phone}`}>
                Call customer
              </a>
            ) : null}
            <button className="btn small outline" onClick={generate} disabled={loading}>
              Rewrite
            </button>
            <button className="btn small ghost" onClick={() => setReply(null)}>
              Close
            </button>
          </div>
        </section>
      )}
    </article>
  );
}
