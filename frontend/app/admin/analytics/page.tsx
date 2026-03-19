"use client";

import { useState } from "react";
import { adminFetch } from "@/lib/admin-api";
import { useAdminData } from "@/app/admin/_hooks/use-admin-data";
import { AdminPageSkeleton } from "@/components/Skeleton";
import { StatCard } from "@/app/admin/_components/stat-card";
import { HorizontalBarChart } from "./horizontal-bar-chart";
import { HourChart } from "./hour-chart";

type Period = "7d" | "30d" | "90d";

type Overview = {
  period_days: number;
  sessions: number;
  page_views: number;
  headline_clicks: number;
  ctr: number;
  new_sessions: number;
  returning_sessions: number;
};

type TopHeadline = {
  article_id: string;
  title: string;
  source_name: string;
  clicks: number;
};

type SourceMetric = {
  source_slug: string;
  source_name: string | null;
  clicks: number;
  share: number;
};

type CategoryMetric = {
  category_slug: string;
  clicks: number;
  page_views: number;
  ctr: number;
};

type HourMetric = {
  hour: number;
  page_views: number;
  clicks: number;
};

type AnalyticsData = {
  overview: Overview;
  topHeadlines: TopHeadline[];
  sources: { total_clicks: number; sources: SourceMetric[] };
  categories: CategoryMetric[];
  hours: HourMetric[];
};

export default function AnalyticsPage() {
  const [period, setPeriod] = useState<Period>("7d");

  const { data, loading } = useAdminData(async () => {
    const q = `period=${period}`;
    const [overview, th, sources, cat, hr] = await Promise.all([
      adminFetch<Overview>(`/api/admin/analytics/overview?${q}`),
      adminFetch<{ headlines: TopHeadline[] }>(`/api/admin/analytics/top-headlines?${q}&limit=20`),
      adminFetch<{ total_clicks: number; sources: SourceMetric[] }>(`/api/admin/analytics/by-source?${q}`),
      adminFetch<{ categories: CategoryMetric[] }>(`/api/admin/analytics/by-category?${q}`),
      adminFetch<{ hours: HourMetric[] }>(`/api/admin/analytics/by-hour?${q}`),
    ]);
    return {
      overview,
      topHeadlines: th.headlines,
      sources,
      categories: cat.categories,
      hours: hr.hours,
    } as AnalyticsData;
  }, [period]);

  if (loading) return <AdminPageSkeleton />;
  if (!data) return null;

  const { overview, topHeadlines, sources, categories, hours } = data;
  const maxSourceClicks = Math.max(...sources.sources.map((s) => s.clicks), 1);
  const maxCategoryPV = Math.max(...categories.map((c) => c.page_views), 1);
  const maxHourPV = Math.max(...hours.map((h) => h.page_views), 1);

  return (
    <div className="space-y-6 max-w-5xl">
      {/* Header */}
      <div className="flex items-center justify-between">
        <h1 className="text-xl font-semibold text-primary">Analytics</h1>
        <div className="flex gap-1">
          {(["7d", "30d", "90d"] as Period[]).map((p) => (
            <button
              key={p}
              onClick={() => setPeriod(p)}
              className={`px-3 py-1.5 rounded text-sm ${
                period === p
                  ? "bg-accent text-white font-medium"
                  : "border border-rule text-secondary hover:text-primary"
              }`}
            >
              {p}
            </button>
          ))}
        </div>
      </div>

      {/* Overview cards */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <StatCard label="Sessions" value={overview.sessions.toLocaleString()} />
        <StatCard label="Page Views" value={overview.page_views.toLocaleString()} />
        <StatCard label="Headline Clicks" value={overview.headline_clicks.toLocaleString()} />
        <StatCard label="CTR" value={`${(overview.ctr * 100).toFixed(1)}%`} />
      </div>

      {/* New vs Returning */}
      <div className="grid grid-cols-2 gap-4">
        <StatCard label="New Sessions" value={overview.new_sessions.toLocaleString()} />
        <StatCard label="Returning Sessions" value={overview.returning_sessions.toLocaleString()} />
      </div>

      {/* Top Headlines */}
      <section>
        <h2 className="text-sm font-semibold text-secondary uppercase tracking-wider mb-3">
          Top Headlines
        </h2>
        <div className="border border-rule rounded overflow-hidden">
          <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead className="bg-surface-alt text-left">
              <tr>
                <th className="px-3 py-2 text-secondary font-medium w-8">#</th>
                <th className="px-3 py-2 text-secondary font-medium">Title</th>
                <th className="px-3 py-2 text-secondary font-medium">Source</th>
                <th className="px-3 py-2 text-secondary font-medium text-right">Clicks</th>
              </tr>
            </thead>
            <tbody>
              {topHeadlines.length === 0 ? (
                <tr>
                  <td colSpan={4} className="px-3 py-4 text-center text-muted">No click data yet</td>
                </tr>
              ) : (
                topHeadlines.map((h, i) => (
                  <tr key={h.article_id} className="border-t border-rule">
                    <td className="px-3 py-2 text-muted">{i + 1}</td>
                    <td className="px-3 py-2 text-primary max-w-md truncate">{h.title}</td>
                    <td className="px-3 py-2 text-secondary">{h.source_name}</td>
                    <td className="px-3 py-2 text-secondary text-right">{h.clicks}</td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
          </div>
        </div>
      </section>

      {/* By Source */}
      <section>
        <h2 className="text-sm font-semibold text-secondary uppercase tracking-wider mb-3">
          Clicks by Source
        </h2>
        {sources.sources.length === 0 ? (
          <p className="text-muted text-sm">No click data yet</p>
        ) : (
          <HorizontalBarChart
            items={sources.sources.map((s) => ({
              key: s.source_slug,
              label: s.source_name || s.source_slug,
              value: s.clicks,
              extras: [
                { label: "clicks", value: String(s.clicks) },
                { label: "share", value: `${(s.share * 100).toFixed(1)}%`, className: "text-xs text-muted w-14 text-right" },
              ],
            }))}
            maxValue={maxSourceClicks}
          />
        )}
      </section>

      {/* By Category */}
      <section>
        <h2 className="text-sm font-semibold text-secondary uppercase tracking-wider mb-3">
          By Category
        </h2>
        {categories.length === 0 ? (
          <p className="text-muted text-sm">No category data yet</p>
        ) : (
          <HorizontalBarChart
            items={categories.map((c) => ({
              key: c.category_slug,
              label: c.category_slug,
              value: c.page_views,
              extras: [
                { label: "pv", value: `${c.page_views} pv` },
                { label: "cl", value: `${c.clicks} cl` },
                { label: "ctr", value: `${(c.ctr * 100).toFixed(1)}% CTR`, className: "text-xs text-muted w-16 text-right" },
              ],
            }))}
            maxValue={maxCategoryPV}
          />
        )}
      </section>

      {/* By Hour */}
      <section>
        <h2 className="text-sm font-semibold text-secondary uppercase tracking-wider mb-3">
          Activity by Hour
        </h2>
        <HourChart hours={hours} maxPageViews={maxHourPV} />
      </section>
    </div>
  );
}
