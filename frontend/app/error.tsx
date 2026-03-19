"use client";

export default function RootError({
  reset,
}: {
  error: Error & { digest?: string };
  reset: () => void;
}) {
  return (
    <div className="min-h-screen flex items-center justify-center">
      <div className="text-center space-y-4">
        <h1 className="text-xl font-semibold text-primary">Something went wrong</h1>
        <button
          onClick={reset}
          className="px-4 py-2 rounded bg-accent text-white text-sm hover:bg-accent-hover"
        >
          Try again
        </button>
      </div>
    </div>
  );
}
