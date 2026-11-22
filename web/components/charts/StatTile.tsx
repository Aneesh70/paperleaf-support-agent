export default function StatTile({ label, value, note }: { label: string; value: number | string; note?: string }) {
  return (
    <div className="rounded-lg border border-stone-200 bg-white p-4">
      <div className="text-sm text-stone-600">{label}</div>
      <div className="mt-1 text-3xl font-semibold tabular-nums text-stone-900">{value}</div>
      {note && <div className="mt-1 text-xs text-stone-600">{note}</div>}
    </div>
  );
}
