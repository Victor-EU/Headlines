export function StatusDot({ status }: { status: string }) {
  const color =
    status === "healthy" || status === "success"
      ? "bg-status-ok"
      : status === "warning" || status === "partial"
        ? "bg-status-warn"
        : status === "disabled" || status === "never_run"
          ? "bg-gray-400"
          : "bg-status-error";
  return <span className={`inline-block w-2 h-2 rounded-full ${color}`} />;
}
