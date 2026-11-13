"use client"; // this file uses React state, so it runs in the browser

import { useState } from "react";

// The outline of a 5-point star (an SVG "path"). Drawn inside a 24x24 box.
const STAR_PATH = "M12 2.5l2.95 6.2 6.8.9-5 4.7 1.25 6.7L12 17.6 6 21l1.25-6.7-5-4.7 6.8-.9L12 2.5z";

/** One star: filled amber when `filled`, just an outline otherwise. */
function StarIcon({ filled, size }: { filled: boolean; size: number }) {
  return (
    // aria-hidden: screen readers skip the picture; the parent element has a text label.
    <svg viewBox="0 0 24 24" width={size} height={size} aria-hidden="true">
      <path
        d={STAR_PATH}
        fill={filled ? "var(--star)" : "none"}
        stroke={filled ? "var(--star)" : "var(--star-empty)"}
        strokeWidth="1.6"
        strokeLinejoin="round"
      />
    </svg>
  );
}

/** Read-only row of 5 stars (used on the dashboard to show a rating). */
export function StarsDisplay({ value, size = 16 }: { value: number; size?: number }) {
  return (
    // role="img" + aria-label: a screen reader announces "4 out of 5 stars".
    <span className="stars-display" role="img" aria-label={`${value} out of 5 stars`}>
      {[1, 2, 3, 4, 5].map((n) => (
        <StarIcon key={n} filled={n <= value} size={size} />
      ))}
    </span>
  );
}

interface StarRatingProps {
  value: number | null; // the chosen rating, or null when nothing is chosen yet
  onChange: (value: number) => void; // called with 1-5 when a star is clicked
  label: string; // the question, read aloud by screen readers
}

/** Interactive 5-star input. Hover/focus previews, click selects. */
export function StarRating({ value, onChange, label }: StarRatingProps) {
  // The star the mouse (or keyboard focus) is currently on, for the preview effect.
  const [hover, setHover] = useState<number | null>(null);
  // Fill stars up to the hovered star, otherwise up to the chosen value.
  const shown = hover ?? value ?? 0;

  return (
    <div
      className="star-input"
      role="radiogroup" // "a group where exactly one option can be chosen"
      aria-label={label}
      onMouseLeave={() => setHover(null)}
    >
      {[1, 2, 3, 4, 5].map((n) => (
        <button
          key={n}
          type="button"
          role="radio"
          aria-checked={value === n}
          aria-label={`${n} ${n === 1 ? "star" : "stars"}`}
          onMouseEnter={() => setHover(n)}
          onFocus={() => setHover(n)}
          onBlur={() => setHover(null)}
          onClick={() => onChange(n)}
        >
          <StarIcon filled={n <= shown} size={44} />
        </button>
      ))}
    </div>
  );
}
