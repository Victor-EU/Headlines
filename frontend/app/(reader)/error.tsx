"use client";

export default function ReaderError({
  reset,
}: {
  error: Error & { digest?: string };
  reset: () => void;
}) {
  return (
    <div className="py-16 text-center space-y-4">
      <h1 className="text-xl font-semibold text-primary">
        We had trouble loading this page
      </h1>
      <p className="text-secondary text-sm">
        Please try again in a moment.
      </p>
      <button
        onClick={reset}
        className="px-4 py-2 rounded bg-accent text-white text-sm hover:bg-accent-hover"
      >
        Try again
      </button>
    </div>
  );
}
