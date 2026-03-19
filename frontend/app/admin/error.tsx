"use client";

export default function AdminError({
  error,
  reset,
}: {
  error: Error & { digest?: string };
  reset: () => void;
}) {
  return (
    <div className="py-16 text-center space-y-4 max-w-lg mx-auto">
      <h1 className="text-xl font-semibold text-primary">Something went wrong</h1>
      <p className="text-sm text-secondary break-words">{error.message}</p>
      <button
        onClick={reset}
        className="px-4 py-2 rounded bg-accent text-white text-sm hover:bg-accent-hover"
      >
        Try again
      </button>
    </div>
  );
}
