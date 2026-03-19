"use client";

import { useEffect, useRef, useState, useCallback } from "react";
import type { CategoryItem } from "@/lib/types";

type Props = {
  categories: CategoryItem[];
};

export function CategoryNav({ categories }: Props) {
  const [activeSlug, setActiveSlug] = useState<string | null>(null);
  const isScrollingRef = useRef(false);
  const timeoutRef = useRef<ReturnType<typeof setTimeout> | null>(null);

  // Scroll-spy: IntersectionObserver tracks which sections are visible
  useEffect(() => {
    const visibleSections = new Set<string>();

    const observer = new IntersectionObserver(
      (entries) => {
        if (isScrollingRef.current) return;

        for (const entry of entries) {
          if (entry.isIntersecting) {
            visibleSections.add(entry.target.id);
          } else {
            visibleSections.delete(entry.target.id);
          }
        }

        // Pick first visible section in category order
        const firstVisible = categories.find((c) =>
          visibleSections.has(c.slug),
        );
        setActiveSlug(firstVisible?.slug ?? null);
      },
      { rootMargin: "0px 0px -70% 0px", threshold: 0 },
    );

    for (const cat of categories) {
      const el = document.getElementById(cat.slug);
      if (el) observer.observe(el);
    }

    return () => observer.disconnect();
  }, [categories]);

  const scrollToSection = useCallback((slug: string | null) => {
    // Suppress scroll-spy while programmatic scrolling
    isScrollingRef.current = true;
    if (timeoutRef.current) clearTimeout(timeoutRef.current);
    timeoutRef.current = setTimeout(() => {
      isScrollingRef.current = false;
    }, 1000);

    // Update URL hash (replaceState — no history pollution)
    window.history.replaceState(
      null,
      "",
      `${window.location.pathname}${slug ? `#${slug}` : ""}`,
    );

    if (!slug) {
      setActiveSlug(null);
      window.scrollTo({ top: 0, behavior: "smooth" });
      return;
    }

    setActiveSlug(slug);
    document
      .getElementById(slug)
      ?.scrollIntoView({ behavior: "smooth", block: "start" });
  }, []);

  // Initial hash handling: scroll to section if URL has hash
  useEffect(() => {
    const hash = window.location.hash.slice(1);
    if (hash) {
      requestAnimationFrame(() => scrollToSection(hash));
    }
  }, [scrollToSection]);

  return (
    <nav className="sticky top-0 z-10 bg-surface border-b border-rule flex gap-4 overflow-x-auto scrollbar-hide pb-4 pt-4 mb-6 relative">
      <button
        onClick={() => scrollToSection(null)}
        className={`text-nav uppercase whitespace-nowrap font-sans transition-colors duration-150 ${
          !activeSlug
            ? "text-nav-active border-b-2 border-current"
            : "text-nav hover:text-nav-active"
        }`}
      >
        All
      </button>
      {categories.map((cat) => {
        const isActive = cat.slug === activeSlug;
        return (
          <button
            key={cat.slug}
            onClick={() => scrollToSection(cat.slug)}
            className={`text-nav uppercase whitespace-nowrap font-sans transition-colors duration-150 ${
              isActive
                ? "text-nav-active border-b-2 border-current"
                : "text-nav hover:text-nav-active"
            }`}
          >
            {cat.name}
          </button>
        );
      })}
      {/* Fade gradient hint for overflow */}
      <div className="absolute right-0 top-0 bottom-0 w-8 bg-gradient-to-l from-surface to-transparent pointer-events-none" />
    </nav>
  );
}
