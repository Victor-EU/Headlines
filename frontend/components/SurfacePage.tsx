import { notFound } from "next/navigation";
import type { SurfaceConfig } from "@/lib/surfaces";
import type { CategoryItem, PaginationMeta } from "@/lib/types";
import { fetchCategories, fetchHeadlines } from "@/lib/api";
import { CategoryNav } from "./CategoryNav";
import { EditorialSummary } from "./EditorialSummary";
import { InFocus } from "./InFocus";
import { LeadHeadline } from "./LeadHeadline";
import { CategorySections, type CategorySection } from "./CategorySections";

type Props = {
  config: SurfaceConfig;
};

export async function SurfacePage({ config }: Props) {
  // Round 1: categories + lead headline in parallel
  let categories: CategoryItem[];
  let leadHeadline = null;
  try {
    const [cats, leadResult] = await Promise.all([
      fetchCategories(config.categoryApiSurface),
      config.showLeadHeadline
        ? fetchHeadlines({ surface: config.slug, perPage: 1 }).catch(() => null)
        : Promise.resolve(null),
    ]);
    categories = cats;
    leadHeadline = leadResult?.headlines[0] ?? null;
  } catch {
    notFound();
  }

  // Round 2: per-category headline fetches (allSettled — one failed category doesn't crash the page)
  const categoryResults = await Promise.allSettled(
    categories.map((cat) =>
      fetchHeadlines({ surface: config.slug, category: cat.slug, perPage: config.perPage }),
    ),
  );

  const sections: CategorySection[] = categories.map((cat, i) => {
    const result = categoryResults[i];
    if (result.status === "fulfilled") {
      return {
        category: cat,
        headlines: result.value.headlines,
        pagination: result.value.pagination,
      };
    }
    return {
      category: cat,
      headlines: [],
      pagination: {
        page: 1,
        per_page: 0,
        total: 0,
        has_next: false,
      } as PaginationMeta,
    };
  });

  return (
    <div data-surface={config.slug}>
      <CategoryNav categories={categories} />
      <EditorialSummary config={config} />
      <InFocus config={config} />
      {leadHeadline && <LeadHeadline headline={leadHeadline} config={config} />}
      <CategorySections sections={sections} config={config} />
    </div>
  );
}
