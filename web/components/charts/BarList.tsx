// Ranked horizontal bars: one series, one hue, bars share one baseline, value printed at the end.
const SERIES = "#2a78d6"; // categorical slot 1 (validated reference palette)

export default function BarList({ rows, emptyText }: { rows: { label: string; value: number }[]; emptyText: string }) {
  const max = Math.max(1, ...rows.map((r) => r.value));
  if (rows.length === 0) return <p className="text-sm text-stone-500">{emptyText}</p>;
  return (
    <ul className="space-y-2">
      {rows.map((r) => (
        <li key={r.label} className="grid grid-cols-[minmax(0,11rem)_1fr_2rem] items-center gap-3 text-sm" title={`${r.label}: ${r.value}`}>
          <span className="truncate text-stone-700">{r.label}</span>
          <span className="h-3 rounded-r bg-stone-100">
            <span
              className="block h-3 rounded-r"
              style={{ width: `${(r.value / max) * 100}%`, background: SERIES, borderTopRightRadius: 4, borderBottomRightRadius: 4 }}
            />
          </span>
          <span className="text-right tabular-nums text-stone-900">{r.value}</span>
        </li>
      ))}
    </ul>
  );
}
