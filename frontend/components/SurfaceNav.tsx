import Link from "next/link";
import { SURFACES } from "@/lib/surfaces";

export function SurfaceNav({ activeSurface }: { activeSurface: string }) {
  return (
    <nav className="flex gap-6 border-b border-rule pb-3 mb-6">
      {Object.values(SURFACES).map((surface) => {
        const isActive = surface.slug === activeSurface;
        return (
          <Link
            key={surface.slug}
            href={surface.basePath}
            className={`font-serif text-nav uppercase transition-colors duration-150 ${
              isActive
                ? "text-nav-active border-b-2 border-current pb-[calc(0.75rem-2px)]"
                : "text-nav hover:text-nav-active pb-3"
            }`}
          >
            {surface.label}
          </Link>
        );
      })}
    </nav>
  );
}
