"use client";

import { useState } from "react";

const STAR_PATH = "M12 2.5l2.95 6.2 6.8.9-5 4.7 1.25 6.7L12 17.6 6 21l1.25-6.7-5-4.7 6.8-.9L12 2.5z";

function StarIcon({ filled, size }: { filled: boolean; size: number }) {
  return (
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

/** Read-only stars, used on the dashboard. */
export function StarsDisplay({ value, size = 16 }: { value: number; size?: number }) {
  return (
    <span className="stars-display" role="img" aria-label={`${value} out of 5 stars`}>
      {[1, 2, 3, 4, 5].map((n) => (
        <StarIcon key={n} filled={n <= value} size={size} />
      ))}
    </span>
  );
}

interface StarRatingProps {
  value: number | null;
  onChange: (value: number) => void;
  label: string;
}

/** Interactive 5-star input. Hover previews, click selects, arrow keys and 1-5 work too. */
export function StarRating({ value, onChange, label }: StarRatingProps) {
  const [hover, setHover] = useState<number | null>(null);
  const shown = hover ?? value ?? 0;

  return (
    <div
      className="star-input"
      role="radiogroup"
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
