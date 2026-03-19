export function StatCard({ label, value }: { label: string; value: string }) {
  return (
    <div className="border border-rule rounded p-4">
      <p className="text-xs text-secondary uppercase tracking-wider">{label}</p>
      <p className="text-xl font-semibold text-primary mt-1">{value}</p>
    </div>
  );
}
