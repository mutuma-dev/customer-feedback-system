/**
 * Two hand-drawn SVG charts (no chart library needed):
 *   Donut      - how many customers are unhappy / neutral / happy
 *   TrendChart - the daily average score and a 7-day forecast
 */
import type { TrendPoint } from "@/lib/api";

interface DonutProps {
  detractors: number;
  passives: number;
  promoters: number;
}

/**
 * Donut chart. The circle's radius is 15.9155, which makes its circumference exactly 100.
 * That way a segment worth 40% is simply a dash of length 40.
 */
export function Donut({ detractors, passives, promoters }: DonutProps) {
  const total = detractors + passives + promoters;
  // Plain-language names first; the brief's technical word in brackets.
  const segments = [
    { label: "Unhappy", note: "detractors", value: detractors, color: "var(--bad)" },
    { label: "Neutral", note: "passives", value: passives, color: "var(--mid)" },
    { label: "Happy", note: "promoters", value: promoters, color: "var(--good)" },
  ];
  let offset = 25; // 25 moves the start of the first segment to 12 o'clock

  return (
    <div className="donut-wrap">
      <svg
        className="donut"
        viewBox="0 0 42 42"
        role="img"
        aria-label={`Unhappy ${detractors}, neutral ${passives}, happy ${promoters}`}
      >
        {/* The grey ring behind the coloured segments. */}
        <circle cx="21" cy="21" r="15.9155" fill="none" stroke="var(--line)" strokeWidth="6" />
        {total > 0 &&
          segments.map((s) => {
            const pct = (s.value / total) * 100; // this segment's share of the ring
            const circle = (
              <circle
                key={s.label}
                cx="21"
                cy="21"
                r="15.9155"
                fill="none"
                stroke={s.color}
                strokeWidth="6"
                // "dash gap": draw `pct`, then leave the rest of the ring empty
                strokeDasharray={`${pct} ${100 - pct}`}
                strokeDashoffset={offset}
              />
            );
            offset -= pct; // the next segment starts where this one ended
            return circle;
          })}
        {/* The total in the middle. */}
        <text x="21" y="23" textAnchor="middle" fontSize="7" fill="var(--text)" fontWeight="700">
          {total}
        </text>
      </svg>
      <ul className="legend">
        {segments.map((s) => (
          <li key={s.label}>
            <i className="dot" style={{ background: s.color }} />
            {s.label} ({s.note}): {s.value}
          </li>
        ))}
      </ul>
    </div>
  );
}

interface TrendProps {
  points: TrendPoint[]; // real daily averages
  projection: TrendPoint[]; // forecast days
}

/** Line chart on a 1-5 scale. Solid line = real data, dashed line = forecast. */
export function TrendChart({ points, projection }: TrendProps) {
  if (points.length === 0) return <p className="muted">No data yet.</p>;

  // The drawing area is 600 x 260 units; it scales down to fit any screen width.
  const W = 600;
  const H = 260;
  const P = 36; // padding around the plot
  const total = points.length + projection.length;
  // x position of the i-th day, spread evenly across the width.
  const x = (i: number) => P + (total === 1 ? 0 : (i * (W - 2 * P)) / (total - 1));
  // y position of a score: 1 is at the bottom, 5 at the top.
  const y = (v: number) => H - P - ((v - 1) / 4) * (H - 2 * P);

  // A polyline is written as "x1,y1 x2,y2 x3,y3 ...".
  const actual = points.map((p, i) => `${x(i)},${y(p.mean)}`).join(" ");
  const last = points[points.length - 1];
  // The dashed forecast line starts from the last real point so the two lines connect.
  const dashed = [last, ...projection]
    .map((p, i) => `${x(points.length - 1 + i)},${y(p.mean)}`)
    .join(" ");
  const first = points[0].date;
  const end = (projection[projection.length - 1] ?? last).date;

  return (
    <svg
      viewBox={`0 0 ${W} ${H}`}
      width="100%"
      role="img"
      aria-label="Daily average score with projection"
    >
      {/* Horizontal grid lines and the 1-5 labels on the left. */}
      {[1, 2, 3, 4, 5].map((v) => (
        <g key={v}>
          <line
            x1={P}
            x2={W - P}
            y1={y(v)}
            y2={y(v)}
            stroke="var(--line)"
            strokeDasharray={v === 3 ? "0" : "3 4"}
          />
          <text x={8} y={y(v) + 5} fontSize="16" fill="var(--muted)">
            {v}
          </text>
        </g>
      ))}
      <polyline
        points={actual}
        fill="none"
        stroke="var(--accent)"
        strokeWidth="3"
        strokeLinejoin="round"
      />
      {projection.length > 0 && (
        <polyline
          points={dashed}
          fill="none"
          stroke="var(--accent)"
          strokeWidth="3"
          strokeDasharray="6 6"
          opacity="0.7"
        />
      )}
      {/* One dot per real day; the <title> is the hover/long-press tooltip. */}
      {points.map((p, i) => (
        <circle key={p.date} cx={x(i)} cy={y(p.mean)} r="4" fill="var(--accent)">
          <title>{`${p.date}: ${p.mean} (${p.count ?? 0} responses)`}</title>
        </circle>
      ))}
      <text x={P} y={H - 8} fontSize="16" fill="var(--muted)">
        {first}
      </text>
      <text x={W - P} y={H - 8} fontSize="16" fill="var(--muted)" textAnchor="end">
        {end} (forecast)
      </text>
    </svg>
  );
}
