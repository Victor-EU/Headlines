export type AlsoReportedBy = {
  source_name: string;
  source_slug: string;
  url: string;
};

export type HeadlineData = {
  id: string;
  title: string;
  url: string;
  summary: string | null;
  source_name: string;
  source_slug: string;
  source_homepage: string;
  published_at: string;
  categories: string[];
  also_reported_by: AlsoReportedBy[];
  interest_score: number | null;
};

export type PaginationMeta = {
  page: number;
  per_page: number;
  total: number;
  has_next: boolean;
};

export type HeadlinesResponse = {
  surface: string;
  headlines: HeadlineData[];
  pagination: PaginationMeta;
  redirect?: string;
};

export type CategoryItem = {
  name: string;
  slug: string;
  article_count: number;
};

export type BriefingResponse = {
  type: string;
  date: string;
  brief: string | null;
  generated_at: string | null;
  focus_topic: string | null;
  focus_body: string | null;
};
