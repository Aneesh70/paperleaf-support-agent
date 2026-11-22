"use client";

import { useState } from "react";

// One series of daily counts: thin columns on one baseline, hover tooltip, value shown on the hovered/non-zero column.
const SERIES = "#2a78d6";

export default function DailyColumns({ data }: { data: { date: string; count: number }[] }) {
  const [hover, setHover] = useState<number | null>(null);
  const max = Math.max(1, ...data.map((d) => d.count));
  const H = 120;
  return (
    <div className="relative" role="img" aria-label={`Tickets per day, last ${data.length} days`}>
      <div className="flex items-end gap-3 border-b border-stone-300" style={{ height: H + 20 }}>
        {data.map((d, i) => {
          const h = d.count === 0 ? 0 : Math.max(4, (d.count / max) * H);
          return (
            <div
              key={d.date}
              className="relative flex flex-1 flex-col items-center justify-end"
              style={{ height: "100%" }}
              onMouseEnter={() => setHover(i)}
              onMouseLeave={() => setHover(null)}
            >
              {(d.count > 0 || hover === i) && (
                <span className="mb-1 text-xs tabular-nums text-stone-700">{d.count}</span>
              )}
              <div
                style={{ height: h, width: "55%", maxWidth: 28, background: SERIES, borderTopLeftRadius: 4, borderTopRightRadius: 4, opacity: hover === null || hover === i ? 1 : 0.55 }}
              />
              {hover === i && (
                <div className="pointer-events-none absolute -top-8 z-10 whitespace-nowrap rounded bg-stone-900 px-2 py-1 text-xs text-white">
                  {d.date}: {d.count} {d.count === 1 ? "ticket" : "tickets"}
                </div>
              )}
            </div>
          );
        })}
      </div>
      <div className="mt-1 flex gap-3">
        {data.map((d) => (
          <span key={d.date} className="flex-1 text-center text-xs text-stone-600">
            {new Date(d.date + "T00:00:00").toLocaleDateString("en-IN", { weekday: "short" })}
          </span>
        ))}
      </div>
    </div>
  );
}
