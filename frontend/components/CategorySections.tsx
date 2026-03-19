"use client";

import { useState, useCallback, useRef } from "react";
import type { SurfaceConfig } from "@/lib/surfaces";
import type { CategoryItem, HeadlineData, PaginationMeta } from "@/lib/types";
import { HeadlineItem } from "./HeadlineItem";
import { SectionLabel } from "./SectionLabel";

export type CategorySection = {
  category: CategoryItem;
  headlines: HeadlineData[];
  pagination: PaginationMeta;
};

type Props = {
  sections: CategorySection[];
  config: SurfaceConfig;
};

export function CategorySections({ sections: initialSections, config }: Props) {
  const [sections, setSections] = useState(initialSections);
  const [loadingSection, setLoadingSection] = useState<string | null>(null);
  const loadingRef = useRef(false);
  const abortRef = useRef<AbortController | null>(null);

  const loadMore = useCallback(
    async (slug: string, nextPage: number) => {
      if (loadingRef.current) return;
      loadingRef.current = true;
      setLoadingSection(slug);

      abortRef.current?.abort();
      const controller = new AbortController();
      abortRef.current = controller;

      try {
        const params = new URLSearchParams({
          surface: config.slug,
          category: slug,
          page: String(nextPage),
        });
        const url = `${process.env.NEXT_PUBLIC_API_URL || ""}/api/headlines?${params}`;
        const res = await fetch(url, { signal: controller.signal });
        if (!res.ok) throw new Error(`${res.status}`);
        const data = await res.json();

        setSections((prev) =>
          prev.map((s) =>
            s.category.slug === slug
              ? {
                  ...s,
                  headlines: [...s.headlines, ...data.headlines],
                  pagination: data.pagination,
                }
              : s,
          ),
        );
      } catch {
        // silently fail — user can retry
      } finally {
        loadingRef.current = false;
        setLoadingSection(null);
      }
    },
    [config.slug],
  );

  return (
    <div>
      {sections.map((section) => (
        <section
          key={section.category.slug}
          id={section.category.slug}
          className="scroll-mt-16"
        >
          <SectionLabel label={section.category.name.toUpperCase()} />
          {section.headlines.length === 0 ? (
            <p className="text-meta text-muted py-12 text-center">
              No headlines in this section.
            </p>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 gap-column">
              {section.headlines.map((h) => (
                <HeadlineItem key={h.id} headline={h} config={config} />
              ))}
            </div>
          )}
          {section.pagination.has_next && (
            <div className="border-t border-rule py-8 text-center">
              <button
                onClick={() =>
                  loadMore(
                    section.category.slug,
                    section.pagination.page + 1,
                  )
                }
                disabled={loadingSection === section.category.slug}
                className="text-meta text-muted hover:text-accent transition-colors font-sans"
              >
                {loadingSection === section.category.slug
                  ? "Loading..."
                  : "More headlines"}
              </button>
            </div>
          )}
        </section>
      ))}
    </div>
  );
}
