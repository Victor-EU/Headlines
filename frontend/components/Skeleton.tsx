export function SkeletonLine({
  width = "100%",
  height = "0.75rem",
}: {
  width?: string;
  height?: string;
}) {
  return (
    <div
      className="rounded bg-gradient-to-r from-surface-alt via-rule/30 to-surface-alt bg-[length:200%_100%] animate-shimmer"
      style={{ width, height }}
    />
  );
}

export function SkeletonBlock({
  width = "100%",
  height = "5rem",
}: {
  width?: string;
  height?: string;
}) {
  return (
    <div
      className="rounded bg-gradient-to-r from-surface-alt via-rule/30 to-surface-alt bg-[length:200%_100%] animate-shimmer"
      style={{ width, height }}
    />
  );
}

export function ReaderPageSkeleton() {
  return (
    <div>
      {/* SurfaceNav placeholder */}
      <nav className="flex gap-6 border-b border-rule pb-3 mb-6">
        <SkeletonLine width="3.5rem" height="1rem" />
        <SkeletonLine width="4.5rem" height="1rem" />
      </nav>

      {/* Category nav pill row */}
      <div className="flex gap-2 mb-6">
        <SkeletonLine width="2.5rem" height="1.75rem" />
        <SkeletonLine width="5rem" height="1.75rem" />
        <SkeletonLine width="4rem" height="1.75rem" />
        <SkeletonLine width="6rem" height="1.75rem" />
        <SkeletonLine width="4.5rem" height="1.75rem" />
      </div>

      {/* Headline blocks in 2-col grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-column">
        {Array.from({ length: 6 }).map((_, i) => (
          <div key={i} className="space-y-2 py-4 border-t border-rule">
            <SkeletonLine width="90%" height="1rem" />
            <SkeletonLine width="60%" height="0.75rem" />
            <SkeletonLine width="30%" height="0.625rem" />
          </div>
        ))}
      </div>
    </div>
  );
}

export function AdminPageSkeleton() {
  return (
    <div className="space-y-6 max-w-5xl">
      {/* Stat cards */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        {Array.from({ length: 4 }).map((_, i) => (
          <div key={i} className="border border-rule rounded p-4 space-y-2">
            <SkeletonLine width="60%" height="0.625rem" />
            <SkeletonLine width="40%" height="1.25rem" />
          </div>
        ))}
      </div>

      {/* Table block with row outlines */}
      <div className="border border-rule rounded overflow-hidden">
        <div className="bg-surface-alt px-3 py-2">
          <SkeletonLine width="30%" height="0.75rem" />
        </div>
        {Array.from({ length: 5 }).map((_, i) => (
          <div key={i} className="px-3 py-3 border-t border-rule flex gap-4">
            <SkeletonLine width="25%" height="0.75rem" />
            <SkeletonLine width="15%" height="0.75rem" />
            <SkeletonLine width="20%" height="0.75rem" />
            <SkeletonLine width="10%" height="0.75rem" />
          </div>
        ))}
      </div>
    </div>
  );
}
