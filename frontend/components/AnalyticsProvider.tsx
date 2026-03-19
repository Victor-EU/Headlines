"use client";

import { useEffect } from "react";
import { usePathname } from "next/navigation";
import { trackEvent } from "@/lib/analytics";

export function AnalyticsProvider({ children }: { children: React.ReactNode }) {
  const pathname = usePathname();

  // page_view on every route change
  useEffect(() => {
    const surface = pathname.startsWith("/learning") ? "learning" : "news";
    trackEvent("page_view", { surface });
  }, [pathname]);

  // Event delegation for headline_click
  useEffect(() => {
    function handleClick(e: MouseEvent) {
      const anchor = (e.target as HTMLElement).closest<HTMLAnchorElement>("a[data-article-id]");
      if (!anchor) return;
      const surfaceEl = anchor.closest<HTMLElement>("[data-surface]");
      const surface = surfaceEl?.dataset.surface || "news";
      const sectionEl = anchor.closest<HTMLElement>("section[id]");
      const categorySlug = sectionEl?.id || undefined;

      trackEvent("headline_click", {
        article_id: anchor.dataset.articleId,
        source_slug: anchor.dataset.sourceSlug,
        surface,
        category_slug: categorySlug,
      });
    }
    document.addEventListener("click", handleClick);
    return () => document.removeEventListener("click", handleClick);
  }, []);

  return <>{children}</>;
}
