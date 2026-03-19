export type SurfaceConfig = {
  slug: string;
  label: string;
  basePath: string;
  groupBy: "time" | "topic";
  showSummary: boolean;
  showLeadHeadline: boolean;
  showAlsoReportedBy: boolean;
  timeFormat: "relative" | "date";
  briefingType: string;
  briefingLabel: string;
  briefingCadence: string;
  categoryApiSurface: string;
};

export const SURFACES: Record<string, SurfaceConfig> = {
  news: {
    slug: "news",
    label: "News",
    basePath: "/",
    groupBy: "time",
    showSummary: false,
    showLeadHeadline: true,
    showAlsoReportedBy: true,
    timeFormat: "relative",
    briefingType: "daily_news",
    briefingLabel: "THE BRIEF",
    briefingCadence: "today",
    categoryApiSurface: "news",
  },
  learning: {
    slug: "learning",
    label: "Learning",
    basePath: "/learning",
    groupBy: "topic",
    showSummary: true,
    showLeadHeadline: false,
    showAlsoReportedBy: true,
    timeFormat: "date",
    briefingType: "weekly_learning",
    briefingLabel: "THE LEARNING DIGEST",
    briefingCadence: "this week",
    categoryApiSurface: "learning",
  },
};

export function getSurfaceFromPath(path: string): SurfaceConfig {
  if (path.startsWith("/learning")) return SURFACES.learning;
  return SURFACES.news;
}
