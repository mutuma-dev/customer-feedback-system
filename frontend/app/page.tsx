"use client"; // this page uses state and keyboard events, so it runs in the browser

// THE SURVEY (route "/"). What a paint buyer sees on their phone:
//   questions 1-3 (one per screen) -> contact details -> thank-you screen.

import { FormEvent, useEffect, useState } from "react";
import { StarRating } from "@/components/Stars";
import { api } from "@/lib/api";
import { labelFor } from "@/lib/rating";

// The three questions from the brief. `key` is the field name sent to the backend.
const QUESTIONS = [
  { key: "product_rating", text: "Rate your experience with our product." },
  { key: "care_rating", text: "Rate our customer care." },
  { key: "happy_rating", text: "Are you happy with the product?" },
] as const;

type Key = (typeof QUESTIONS)[number]["key"];
type Ratings = Record<Key, number | null>; // null = not answered yet

export default function SurveyPage() {
  // Which screen is showing: 0, 1, 2 = questions, 3 = contact details, 4 = thank you.
  const [step, setStep] = useState(0);
  // The three answers so far.
  const [ratings, setRatings] = useState<Ratings>({
    product_rating: null,
    care_rating: null,
    happy_rating: null,
  });
  // The contact form fields.
  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [phone, setPhone] = useState("");
  const [isPainter, setIsPainter] = useState(false);
  // Sending state and error message.
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // The question being shown (null on the contact and thank-you screens).
  const question = step < 3 ? QUESTIONS[step] : null;
  // The answer chosen for it so far.
  const current = question ? ratings[question.key] : null;

  /** Save the star the person chose for the current question. */
  function choose(value: number) {
    if (!question) return;
    setRatings((r) => ({ ...r, [question.key]: value }));
  }

  // Keyboard shortcut: pressing 1-5 on a question screen picks that rating.
  useEffect(() => {
    if (!question) return;
    const onKey = (e: KeyboardEvent) => {
      if (/^[1-5]$/.test(e.key)) choose(Number(e.key));
    };
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey); // cleanup when the screen changes
  });

  /** Send everything to the backend. */
  async function submit(e: FormEvent) {
    e.preventDefault(); // stop the browser from reloading the page
    setBusy(true);
    setError(null);
    try {
      await api.submitFeedback({
        name: name.trim(),
        email: email.trim(),
        phone: phone.trim() || undefined, // empty phone is simply left out
        kind: isPainter ? "painter" : "buyer",
        product_rating: ratings.product_rating ?? 3,
        care_rating: ratings.care_rating ?? 3,
        happy_rating: ratings.happy_rating ?? 3,
      });
      setStep(4); // show the thank-you screen
    } catch {
      // Keep what the person typed; just explain what happened.
      setError("We couldn't send your feedback. Please check your connection and try again.");
    } finally {
      setBusy(false);
    }
  }

  // Progress bar: 0%, 33%, 66%, 100%.
  const percent = Math.round((Math.min(step, 3) / 3) * 100);

  return (
    <main className="wrap">
      <p className="brand">Company X</p>

      {/* aria-live: screen readers announce the new content when the screen changes */}
      <section className="card" aria-live="polite">
        {/* ---------- Screens 1-3: one question each ---------- */}
        {question && (
          <>
            <div className="step-row">
              <span>Question {step + 1} of 3</span>
              <span>{percent}%</span>
            </div>
            <div
              className="progress"
              role="progressbar"
              aria-valuenow={percent}
              aria-valuemin={0}
              aria-valuemax={100}
            >
              <div style={{ width: `${percent}%` }} />
            </div>
            <h1>{question.text}</h1>
            <StarRating value={current} onChange={choose} label={question.text} />
            <p className="rating-label">{labelFor(current)}</p>
            {/* The button stays disabled until a star is chosen. */}
            <button className="btn" disabled={current === null} onClick={() => setStep(step + 1)}>
              {step === 2 ? "Continue" : "Next question"}
            </button>
            {step > 0 && (
              <button className="btn ghost" onClick={() => setStep(step - 1)}>
                Back
              </button>
            )}
          </>
        )}

        {/* ---------- Screen 4: contact details ---------- */}
        {step === 3 && (
          <form onSubmit={submit}>
            <h1>Your details</h1>
            <p className="muted">So our team can follow up if needed.</p>
            <label htmlFor="name">Full name</label>
            <input
              id="name"
              required
              value={name}
              onChange={(e) => setName(e.target.value)}
              autoComplete="name"
            />
            <label htmlFor="email">Email</label>
            <input
              id="email"
              type="email"
              required
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              autoComplete="email"
            />
            <label htmlFor="phone">Phone (optional)</label>
            <input
              id="phone"
              type="tel"
              placeholder="+254712345678"
              value={phone}
              onChange={(e) => setPhone(e.target.value)}
              autoComplete="tel"
            />
            <label className="check">
              <input
                type="checkbox"
                checked={isPainter}
                onChange={(e) => setIsPainter(e.target.checked)}
              />
              I&apos;m a professional painter
            </label>
            {error && (
              <p className="error" role="alert">
                {error}
              </p>
            )}
            <button className="btn" type="submit" disabled={busy}>
              {busy ? "Submitting…" : "Submit feedback"}
            </button>
            <button className="btn ghost" type="button" onClick={() => setStep(2)}>
              Back
            </button>
          </form>
        )}

        {/* ---------- Screen 5: thank you ---------- */}
        {step === 4 && (
          <div className="thanks">
            {/* An animated check mark (drawn by the CSS). */}
            <svg className="tick" viewBox="0 0 52 52" width="64" height="64" aria-hidden="true">
              <circle cx="26" cy="26" r="24" fill="none" stroke="var(--accent)" strokeWidth="2.5" />
              <path
                d="M15 27l8 8 14-16"
                fill="none"
                stroke="var(--accent)"
                strokeWidth="3"
                strokeLinecap="round"
                strokeLinejoin="round"
              />
            </svg>
            <h1>Thank you, {name.trim().split(" ")[0]}</h1>
            <p className="muted">Your feedback has been received.</p>
          </div>
        )}
      </section>
    </main>
  );
}
