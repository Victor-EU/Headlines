"use client";

import { useState } from "react";
import { adminFetch } from "@/lib/admin-api";
import { useAdminData } from "@/app/admin/_hooks/use-admin-data";
import { AdminPageSkeleton } from "@/components/Skeleton";

type Briefing = {
  id: string;
  type: string;
  date: string;
  brief: string | null;
  brief_model: string | null;
  generated_at: string | null;
  article_ids: string[];
};

export default function BriefingsPage() {
  const { data: briefings, loading, reload } = useAdminData(
    () => adminFetch<Briefing[]>("/api/admin/briefings"),
  );

  const [regenerating, setRegenerating] = useState<string | null>(null);
  const [expanded, setExpanded] = useState<string | null>(null);

  async function handleRegenerate(type: string) {
    setRegenerating(type);
    try {
      await adminFetch("/api/admin/briefings/regenerate", {
        method: "POST",
        body: JSON.stringify({ type }),
      });
      await reload();
    } catch (e: any) {
      alert(e.message);
    } finally {
      setRegenerating(null);
    }
  }

  if (loading) return <AdminPageSkeleton />;

  const briefingList = briefings ?? [];

  return (
    <div className="space-y-6 max-w-4xl">
      <div className="flex items-center justify-between">
        <h1 className="text-xl font-semibold text-primary">Briefings</h1>
        <div className="flex gap-2">
          <button
            onClick={() => handleRegenerate("daily_news")}
            disabled={regenerating !== null}
            className="px-3 py-1.5 rounded text-sm bg-accent text-white hover:bg-accent-hover disabled:opacity-50"
          >
            {regenerating === "daily_news" ? "Generating..." : "Regenerate Daily"}
          </button>
          <button
            onClick={() => handleRegenerate("weekly_learning")}
            disabled={regenerating !== null}
            className="px-3 py-1.5 rounded text-sm border border-rule text-secondary hover:text-primary disabled:opacity-50"
          >
            {regenerating === "weekly_learning" ? "Generating..." : "Regenerate Weekly"}
          </button>
        </div>
      </div>

      <div className="border border-rule rounded divide-y divide-rule">
        {briefingList.length === 0 ? (
          <div className="px-4 py-8 text-center text-muted">No briefings generated yet</div>
        ) : briefingList.map((b) => (
          <div key={b.id} className="px-4 py-3">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-3">
                <span className={`text-xs px-2 py-0.5 rounded ${b.type === "daily_news" ? "bg-blue-100 text-blue-700" : "bg-green-100 text-status-ok"}`}>
                  {b.type === "daily_news" ? "Daily News" : "Weekly Learning"}
                </span>
                <span className="text-sm text-primary font-medium">{b.date}</span>
                <span className="text-xs text-muted">{b.brief_model || "—"}</span>
                <span className="text-xs text-muted">{b.article_ids.length} articles</span>
              </div>
              <div className="flex items-center gap-2">
                <span className="text-xs text-muted">
                  {b.generated_at ? new Date(b.generated_at).toLocaleString() : "—"}
                </span>
                <button
                  onClick={() => setExpanded(expanded === b.id ? null : b.id)}
                  className="px-2 py-1 rounded text-xs border border-rule text-secondary hover:text-primary"
                >
                  {expanded === b.id ? "Collapse" : "Expand"}
                </button>
              </div>
            </div>
            {expanded === b.id && b.brief && (
              <div className="mt-3 p-3 rounded bg-surface-alt text-sm text-primary whitespace-pre-wrap leading-relaxed">
                {b.brief}
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  );
}
