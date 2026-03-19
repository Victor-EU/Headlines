"use client";

import { adminFetch } from "@/lib/admin-api";
import { timeAgo } from "@/lib/time";
import { useAdminData } from "@/app/admin/_hooks/use-admin-data";
import { AdminPageSkeleton } from "@/components/Skeleton";
import { StatCard } from "@/app/admin/_components/stat-card";
import { StatusDot } from "@/app/admin/_components/status-dot";

type SystemStatus = {
  sources: {
    name: string;
    last_fetch: string | null;
    status: string;
    consecutive_failures: number;
    articles_last_24h: number;
  }[];
  tasks: {
    task: string;
    last_run: string | null;
    status: string;
    model_used: string | null;
  }[];
  costs: {
    today_usd: number;
    this_month_usd: number;
    by_task: Record<string, number>;
  };
  briefings: {
    daily_news: { date: string | null; generated_at: string | null; model: string | null };
    weekly_learning: { date: string | null; generated_at: string | null; model: string | null };
  };
  queue_depth: number;
};

type ErrorItem = {
  type: string;
  source_name?: string;
  task?: string;
  status: string;
  error: string | null;
  at: string;
};

type DashboardData = {
  status: SystemStatus;
  errors: ErrorItem[];
};

export default function AdminDashboard() {
  const { data, loading } = useAdminData(async () => {
    const [status, { errors }] = await Promise.all([
      adminFetch<SystemStatus>("/api/admin/system/status"),
      adminFetch<{ errors: ErrorItem[] }>("/api/admin/system/errors"),
    ]);
    return { status, errors } as DashboardData;
  });

  if (loading) return <AdminPageSkeleton />;
  if (!data) return null;

  const { status, errors } = data;

  return (
    <div className="space-y-6 max-w-5xl">
      <h1 className="text-xl font-semibold text-primary">Dashboard</h1>

      {/* Top stats */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <StatCard label="Queue Depth" value={String(status.queue_depth)} />
        <StatCard label="Cost Today" value={`$${status.costs.today_usd.toFixed(4)}`} />
        <StatCard label="Cost This Month" value={`$${status.costs.this_month_usd.toFixed(4)}`} />
        <StatCard
          label="Sources Active"
          value={`${status.sources.filter((s) => s.status !== "disabled").length}/${status.sources.length}`}
        />
      </div>

      {/* Source health */}
      <section>
        <h2 className="text-sm font-semibold text-secondary uppercase tracking-wider mb-3">
          Source Health
        </h2>
        <div className="border border-rule rounded overflow-hidden">
          <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead className="bg-surface-alt text-left">
              <tr>
                <th className="px-3 py-2 text-secondary font-medium">Source</th>
                <th className="px-3 py-2 text-secondary font-medium">Status</th>
                <th className="px-3 py-2 text-secondary font-medium">Last Fetch</th>
                <th className="px-3 py-2 text-secondary font-medium text-right">24h Articles</th>
              </tr>
            </thead>
            <tbody>
              {status.sources.map((s) => (
                <tr key={s.name} className="border-t border-rule">
                  <td className="px-3 py-2 text-primary">{s.name}</td>
                  <td className="px-3 py-2">
                    <StatusDot status={s.status} />
                    <span className="ml-2 text-secondary">{s.status}</span>
                  </td>
                  <td className="px-3 py-2 text-secondary">{timeAgo(s.last_fetch)}</td>
                  <td className="px-3 py-2 text-secondary text-right">{s.articles_last_24h}</td>
                </tr>
              ))}
            </tbody>
          </table>
          </div>
        </div>
      </section>

      {/* Pipeline tasks */}
      <section>
        <h2 className="text-sm font-semibold text-secondary uppercase tracking-wider mb-3">
          Pipeline Tasks
        </h2>
        <div className="border border-rule rounded overflow-hidden">
          <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead className="bg-surface-alt text-left">
              <tr>
                <th className="px-3 py-2 text-secondary font-medium">Task</th>
                <th className="px-3 py-2 text-secondary font-medium">Status</th>
                <th className="px-3 py-2 text-secondary font-medium">Last Run</th>
                <th className="px-3 py-2 text-secondary font-medium">Model</th>
                <th className="px-3 py-2 text-secondary font-medium text-right">Monthly Cost</th>
              </tr>
            </thead>
            <tbody>
              {status.tasks.map((t) => (
                <tr key={t.task} className="border-t border-rule">
                  <td className="px-3 py-2 text-primary">{t.task}</td>
                  <td className="px-3 py-2">
                    <StatusDot status={t.status} />
                    <span className="ml-2 text-secondary">{t.status}</span>
                  </td>
                  <td className="px-3 py-2 text-secondary">{timeAgo(t.last_run)}</td>
                  <td className="px-3 py-2 text-secondary">{t.model_used || "—"}</td>
                  <td className="px-3 py-2 text-secondary text-right">
                    ${(status.costs.by_task[t.task] || 0).toFixed(4)}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
          </div>
        </div>
      </section>

      {/* Briefing status */}
      <section>
        <h2 className="text-sm font-semibold text-secondary uppercase tracking-wider mb-3">
          Briefings
        </h2>
        <div className="grid grid-cols-2 gap-4">
          <div className="border border-rule rounded p-4">
            <p className="text-xs text-secondary uppercase tracking-wider mb-1">Daily News</p>
            <p className="text-primary text-sm">
              {status.briefings.daily_news.date || "Not generated"}
            </p>
            <p className="text-xs text-muted mt-1">
              {timeAgo(status.briefings.daily_news.generated_at)} &middot;{" "}
              {status.briefings.daily_news.model || "—"}
            </p>
          </div>
          <div className="border border-rule rounded p-4">
            <p className="text-xs text-secondary uppercase tracking-wider mb-1">Weekly Learning</p>
            <p className="text-primary text-sm">
              {status.briefings.weekly_learning.date || "Not generated"}
            </p>
            <p className="text-xs text-muted mt-1">
              {timeAgo(status.briefings.weekly_learning.generated_at)} &middot;{" "}
              {status.briefings.weekly_learning.model || "—"}
            </p>
          </div>
        </div>
      </section>

      {/* Error feed */}
      {errors.length > 0 && (
        <section>
          <h2 className="text-sm font-semibold text-secondary uppercase tracking-wider mb-3">
            Recent Errors
          </h2>
          <div className="border border-rule rounded divide-y divide-rule max-h-64 overflow-y-auto">
            {errors.slice(0, 20).map((err, i) => (
              <div key={i} className="px-3 py-2 text-sm">
                <div className="flex items-center gap-2">
                  <StatusDot status={err.status} />
                  <span className="text-primary font-medium">
                    {err.type === "fetch" ? err.source_name : err.task}
                  </span>
                  <span className="text-muted">{timeAgo(err.at)}</span>
                </div>
                {err.error && (
                  <p className="text-secondary text-xs mt-1 truncate">{err.error}</p>
                )}
              </div>
            ))}
          </div>
        </section>
      )}
    </div>
  );
}
