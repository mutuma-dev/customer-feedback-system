import type { TrendPoint } from "@/lib/api";

interface DonutProps {
  detractors: number;
  passives: number;
  promoters: number;
}

/** Donut chart drawn with SVG. Radius 15.9155 makes the circumference exactly 100. */
export function Donut({ detractors, passives, promoters }: DonutProps) {
  const total = detractors + passives + promoters;
  const segments = [
    { label: "Detractors", value: detractors, color: "var(--bad)" },
    { label: "Passives", value: passives, color: "var(--mid)" },
    { label: "Promoters", value: promoters, color: "var(--good)" },
  ];
  let offset = 25; // start at 12 o'clock
  return (
    <div>
      <svg
        viewBox="0 0 42 42"
        width="200"
        height="200"
        role="img"
        aria-label={`Detractors ${detractors}, passives ${passives}, promoters ${promoters}`}
      >
        <circle cx="21" cy="21" r="15.9155" fill="none" stroke="var(--line)" strokeWidth="6" />
        {total > 0 &&
          segments.map((s) => {
            const pct = (s.value / total) * 100;
            const circle = (
              <circle
                key={s.label}
                cx="21"
                cy="21"
                r="15.9155"
                fill="none"
                stroke={s.color}
                strokeWidth="6"
                strokeDasharray={`${pct} ${100 - pct}`}
                strokeDashoffset={offset}
              />
            );
            offset -= pct;
            return circle;
          })}
        <text x="21" y="22.5" textAnchor="middle" fontSize="6" fill="var(--text)" fontWeight="700">
          {total}
        </text>
      </svg>
      <div className="legend">
        {segments.map((s) => (
          <span key={s.label}>
            <i className="dot" style={{ background: s.color }} />
            {s.label}: {s.value}
          </span>
        ))}
      </div>
    </div>
  );
}

interface TrendProps {
  points: TrendPoint[];
  projection: TrendPoint[];
}

/** Line chart of daily mean score (solid) and the 7-day projection (dashed). Scale is 1-5. */
export function TrendChart({ points, projection }: TrendProps) {
  if (points.length === 0) return <p className="muted">No data yet.</p>;

  const W = 600;
  const H = 240;
  const P = 32;
  const total = points.length + projection.length;
  const x = (i: number) => P + (total === 1 ? 0 : (i * (W - 2 * P)) / (total - 1));
  const y = (v: number) => H - P - ((v - 1) / 4) * (H - 2 * P);

  const actual = points.map((p, i) => `${x(i)},${y(p.mean)}`).join(" ");
  const last = points[points.length - 1];
  const dashed = [last, ...projection].map((p, i) => `${x(points.length - 1 + i)},${y(p.mean)}`).join(" ");
  const first = points[0].date;
  const end = (projection[projection.length - 1] ?? last).date;

  return (
    <svg viewBox={`0 0 ${W} ${H}`} width="100%" role="img" aria-label="Daily average score with projection">
      {[1, 2, 3, 4, 5].map((v) => (
        <g key={v}>
          <line x1={P} x2={W - P} y1={y(v)} y2={y(v)} stroke="var(--line)" strokeDasharray={v === 3 ? "0" : "3 4"} />
          <text x={8} y={y(v) + 4} fontSize="11" fill="var(--muted)">{v}</text>
        </g>
      ))}
      <polyline points={actual} fill="none" stroke="var(--accent)" strokeWidth="3" strokeLinejoin="round" />
      {projection.length > 0 && (
        <polyline points={dashed} fill="none" stroke="var(--accent)" strokeWidth="3" strokeDasharray="6 6" opacity="0.7" />
      )}
      {points.map((p, i) => (
        <circle key={p.date} cx={x(i)} cy={y(p.mean)} r="3.5" fill="var(--accent)">
          <title>{`${p.date}: ${p.mean} (${p.count ?? 0} responses)`}</title>
        </circle>
      ))}
      <text x={P} y={H - 8} fontSize="11" fill="var(--muted)">{first}</text>
      <text x={W - P} y={H - 8} fontSize="11" fill="var(--muted)" textAnchor="end">{end} (projected)</text>
    </svg>
  );
}
