"use client";

import { useEffect, useState } from "react";
import { adminFetch } from "@/lib/admin-api";
import { SkeletonLine } from "@/components/Skeleton";
import { ArticleFilters } from "./article-filters";
import { ArticleBulkActions } from "./article-bulk-actions";

type ArticleCategory = {
  slug: string;
  confidence: number;
  manual: boolean;
};

type Article = {
  id: string;
  title: string;
  url: string;
  source_name: string;
  published_at: string;
  classified: boolean;
  hidden: boolean;
  is_representative: boolean;
  categories: ArticleCategory[];
};

type Source = {
  id: string;
  name: string;
  surface: string;
};

type Category = {
  id: string;
  name: string;
  slug: string;
  surface: string;
};

export default function ArticlesPage() {
  const [articles, setArticles] = useState<Article[]>([]);
  const [pagination, setPagination] = useState({ page: 1, per_page: 30, total: 0, has_next: false });
  const [loading, setLoading] = useState(true);
  const [sources, setSources] = useState<Source[]>([]);
  const [categories, setCategories] = useState<Category[]>([]);
  const [selected, setSelected] = useState<Set<string>>(new Set());

  // Filters
  const [search, setSearch] = useState("");
  const [filterSource, setFilterSource] = useState("");
  const [filterSurface, setFilterSurface] = useState("");
  const [filterCategory, setFilterCategory] = useState("");
  const [filterClassified, setFilterClassified] = useState<string>("");
  const [filterHidden, setFilterHidden] = useState<string>("");
  const [page, setPage] = useState(1);

  async function loadArticles() {
    setLoading(true);
    const params = new URLSearchParams({ page: String(page), per_page: "30" });
    if (search) params.set("q", search);
    if (filterSource) params.set("source_id", filterSource);
    if (filterSurface) params.set("surface", filterSurface);
    if (filterCategory) params.set("category_slug", filterCategory);
    if (filterClassified) params.set("classified", filterClassified);
    if (filterHidden) params.set("hidden", filterHidden);

    const data = await adminFetch<{ articles: Article[]; pagination: typeof pagination }>(
      `/api/admin/articles?${params}`
    );
    setArticles(data.articles);
    setPagination(data.pagination);
    setSelected(new Set());
    setLoading(false);
  }

  async function loadFilters() {
    const [s, c] = await Promise.all([
      adminFetch<Source[]>("/api/admin/sources"),
      adminFetch<Category[]>("/api/admin/categories"),
    ]);
    setSources(s);
    setCategories(c);
  }

  useEffect(() => { loadFilters(); }, []);
  useEffect(() => { loadArticles(); }, [page, filterSource, filterSurface, filterCategory, filterClassified, filterHidden]);

  function handleSearch(e: React.FormEvent) {
    e.preventDefault();
    setPage(1);
    loadArticles();
  }

  function toggleSelect(id: string) {
    const next = new Set(selected);
    if (next.has(id)) next.delete(id); else next.add(id);
    setSelected(next);
  }

  function toggleSelectAll() {
    if (selected.size === articles.length) {
      setSelected(new Set());
    } else {
      setSelected(new Set(articles.map((a) => a.id)));
    }
  }

  async function handleBulkAction(action: string, categoryId?: string) {
    try {
      await adminFetch("/api/admin/articles/bulk", {
        method: "POST",
        body: JSON.stringify({
          action,
          article_ids: Array.from(selected),
          category_id: categoryId || null,
        }),
      });
      await loadArticles();
    } catch (e: any) {
      alert(e.message);
    }
  }

  async function handleToggleHidden(article: Article) {
    await adminFetch(`/api/admin/articles/${article.id}`, {
      method: "PUT",
      body: JSON.stringify({ hidden: !article.hidden }),
    });
    await loadArticles();
  }

  return (
    <div className="space-y-4 max-w-7xl">
      <h1 className="text-xl font-semibold text-primary">Articles</h1>

      <ArticleFilters
        search={search}
        setSearch={setSearch}
        filterSurface={filterSurface}
        setFilterSurface={setFilterSurface}
        filterSource={filterSource}
        setFilterSource={setFilterSource}
        filterCategory={filterCategory}
        setFilterCategory={setFilterCategory}
        filterClassified={filterClassified}
        setFilterClassified={setFilterClassified}
        filterHidden={filterHidden}
        setFilterHidden={setFilterHidden}
        sources={sources}
        categories={categories}
        onSearch={handleSearch}
        onResetPage={() => setPage(1)}
      />

      {selected.size > 0 && (
        <ArticleBulkActions
          selectedCount={selected.size}
          categories={categories}
          onAction={handleBulkAction}
        />
      )}

      {/* Table */}
      <div className="border border-rule rounded overflow-hidden">
        <div className="overflow-x-auto">
        <table className="w-full text-sm">
          <thead className="bg-surface-alt text-left">
            <tr>
              <th className="px-3 py-2 w-8">
                <input type="checkbox" checked={selected.size === articles.length && articles.length > 0} onChange={toggleSelectAll} />
              </th>
              <th className="px-3 py-2 text-secondary font-medium">Title</th>
              <th className="px-3 py-2 text-secondary font-medium">Source</th>
              <th className="px-3 py-2 text-secondary font-medium">Categories</th>
              <th className="px-3 py-2 text-secondary font-medium">Published</th>
              <th className="px-3 py-2 text-secondary font-medium text-right">Actions</th>
            </tr>
          </thead>
          <tbody>
            {loading ? (
              <>
                {Array.from({ length: 5 }).map((_, i) => (
                  <tr key={i} className="border-t border-rule">
                    <td className="px-3 py-3" colSpan={6}>
                      <SkeletonLine width={`${70 + Math.random() * 20}%`} height="0.75rem" />
                    </td>
                  </tr>
                ))}
              </>
            ) : articles.length === 0 ? (
              <tr><td colSpan={6} className="px-3 py-4 text-center text-muted">No articles found</td></tr>
            ) : articles.map((article) => (
              <tr key={article.id} className={`border-t border-rule ${article.hidden ? "opacity-50" : ""}`}>
                <td className="px-3 py-2">
                  <input type="checkbox" checked={selected.has(article.id)} onChange={() => toggleSelect(article.id)} />
                </td>
                <td className="px-3 py-2 max-w-md">
                  <a href={article.url} target="_blank" rel="noreferrer" className="text-primary hover:underline line-clamp-1">
                    {article.title}
                  </a>
                  <div className="flex gap-1 mt-0.5">
                    {!article.classified && <span className="text-xs px-1 py-0.5 rounded bg-amber-100 text-status-warn">Unclassified</span>}
                    {article.hidden && <span className="text-xs px-1 py-0.5 rounded bg-gray-200 text-gray-600">Hidden</span>}
                    {!article.is_representative && <span className="text-xs px-1 py-0.5 rounded bg-blue-100 text-blue-700">Duplicate</span>}
                  </div>
                </td>
                <td className="px-3 py-2 text-secondary">{article.source_name}</td>
                <td className="px-3 py-2">
                  <div className="flex gap-1 flex-wrap">
                    {article.categories.map((c) => (
                      <span key={c.slug} className={`text-xs px-1.5 py-0.5 rounded ${c.manual ? "bg-blue-100 text-blue-700" : "bg-surface-alt text-secondary"}`}>
                        {c.slug} <span className="text-muted">({(c.confidence * 100).toFixed(0)}%)</span>
                      </span>
                    ))}
                  </div>
                </td>
                <td className="px-3 py-2 text-secondary whitespace-nowrap">
                  {new Date(article.published_at).toLocaleDateString()}
                </td>
                <td className="px-3 py-2 text-right">
                  <button
                    onClick={() => handleToggleHidden(article)}
                    className="px-2 py-1 rounded text-xs border border-rule text-secondary hover:text-primary"
                  >
                    {article.hidden ? "Unhide" : "Hide"}
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
        </div>
      </div>

      {/* Pagination */}
      <div className="flex items-center justify-between">
        <span className="text-sm text-muted">
          {pagination.total} articles — page {pagination.page}
        </span>
        <div className="flex gap-2">
          <button
            onClick={() => setPage(Math.max(1, page - 1))}
            disabled={page <= 1}
            className="px-3 py-1.5 rounded text-sm border border-rule text-secondary disabled:opacity-50"
          >
            Previous
          </button>
          <button
            onClick={() => setPage(page + 1)}
            disabled={!pagination.has_next}
            className="px-3 py-1.5 rounded text-sm border border-rule text-secondary disabled:opacity-50"
          >
            Next
          </button>
        </div>
      </div>
    </div>
  );
}
