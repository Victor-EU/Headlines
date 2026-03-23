import type { BriefingResponse, CategoryItem, HeadlinesResponse } from "./types";

function getBaseUrl(): string {
  if (typeof window === "undefined") {
    return process.env.INTERNAL_API_URL || "http://api:8000";
  }
  return process.env.NEXT_PUBLIC_API_URL || "";
}

async function apiFetch<T>(
  path: string,
  options?: RequestInit & { revalidate?: number },
): Promise<T> {
  const { revalidate = 120, ...fetchOptions } = options ?? {};
  const url = `${getBaseUrl()}${path}`;
  const res = await fetch(url, {
    ...fetchOptions,
    next: { revalidate },
  });

  if (res.status === 301 || res.status === 308) {
    const location = res.headers.get("Location");
    return { redirect: location } as T;
  }

  if (!res.ok) {
    throw new Error(`API error: ${res.status} ${res.statusText}`);
  }

  return res.json();
}

export async function fetchHeadlines(params: {
  surface: string;
  category?: string;
  page?: number;
  perPage?: number;
}): Promise<HeadlinesResponse> {
  const searchParams = new URLSearchParams({ surface: params.surface });
  if (params.category) searchParams.set("category", params.category);
  if (params.page) searchParams.set("page", String(params.page));
  if (params.perPage) searchParams.set("per_page", String(params.perPage));

  return apiFetch<HeadlinesResponse>(`/api/headlines?${searchParams}`, {
    revalidate: params.surface === "learning" ? 1800 : 120,
  });
}

export async function fetchCategories(surface: string): Promise<CategoryItem[]> {
  return apiFetch<CategoryItem[]>(`/api/categories?surface=${surface}`, {
    revalidate: 600,
  });
}

export async function fetchBriefing(type: string): Promise<BriefingResponse> {
  return apiFetch<BriefingResponse>(`/api/briefing?type=${type}`, {
    revalidate: type === "weekly_learning" ? 1800 : 300,
  });
}
