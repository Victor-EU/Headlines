"use client";

import { useState } from "react";
import { adminFetch } from "@/lib/admin-api";
import { useAdminData } from "@/app/admin/_hooks/use-admin-data";
import { AdminPageSkeleton } from "@/components/Skeleton";
import { SourceAddForm } from "./source-add-form";

type Source = {
  id: string;
  name: string;
  slug: string;
  surface: string;
  homepage_url: string;
  feed_url: string;
  adapter_type: string;
  fetch_interval: number;
  active: boolean;
  last_fetched_at: string | null;
  last_error: string | null;
  consecutive_failures: number;
};

type FetchLogEntry = {
  id: string;
  status: string;
  trigger: string;
  started_at: string;
  duration_ms: number | null;
  articles_new: number;
  articles_updated: number;
  error_message: string | null;
};

function StatusBadge({ source }: { source: Source }) {
  if (!source.active) return <span className="text-xs px-2 py-0.5 rounded bg-gray-200 text-gray-600">Disabled</span>;
  if (source.consecutive_failures >= 5) return <span className="text-xs px-2 py-0.5 rounded bg-red-100 text-status-error">Error</span>;
  if (source.consecutive_failures >= 2) return <span className="text-xs px-2 py-0.5 rounded bg-amber-100 text-status-warn">Warning</span>;
  return <span className="text-xs px-2 py-0.5 rounded bg-green-100 text-status-ok">Healthy</span>;
}

export default function SourcesPage() {
  const { data: sources, loading, reload } = useAdminData(
    () => adminFetch<Source[]>("/api/admin/sources"),
  );

  const [refreshing, setRefreshing] = useState(false);
  const [refreshStatus, setRefreshStatus] = useState<Record<string, { status: string; articles_new: number }> | null>(null);
  const [showAdd, setShowAdd] = useState(false);
  const [editId, setEditId] = useState<string | null>(null);
  const [logs, setLogs] = useState<{ sourceId: string; entries: FetchLogEntry[] } | null>(null);

  const [form, setForm] = useState({
    name: "", slug: "", surface: "news", homepage_url: "", feed_url: "",
    adapter_type: "rss", fetch_interval: 15,
  });

  if (loading) return <AdminPageSkeleton />;

  const sourceList = sources ?? [];

  async function handleRefreshAll() {
    setRefreshing(true);
    setRefreshStatus(null);
    try {
      const result = await adminFetch<{ batch_id: string }>("/api/admin/refresh-all", {
        method: "POST",
        signal: AbortSignal.timeout(60000),
      });
      const status = await adminFetch<{
        sources: { source_name: string; status: string; articles_new: number }[];
      }>(`/api/admin/refresh-status/${result.batch_id}`);
      const map: Record<string, { status: string; articles_new: number }> = {};
      status.sources.forEach((s) => { map[s.source_name] = { status: s.status, articles_new: s.articles_new }; });
      setRefreshStatus(map);
      await reload();
    } catch (e: any) {
      alert(e.message);
    } finally {
      setRefreshing(false);
    }
  }

  async function handleRefreshOne(id: string) {
    try {
      await adminFetch(`/api/admin/sources/${id}/refresh`, { method: "POST" });
      await reload();
    } catch (e: any) {
      alert(e.message);
    }
  }

  async function handleTestFetch(id: string) {
    try {
      const articles = await adminFetch<any[]>(`/api/admin/sources/${id}/test-fetch`, { method: "POST" });
      alert(`Test fetch returned ${articles.length} articles.\n\n${articles.slice(0, 3).map((a: any) => a.title).join("\n")}`);
    } catch (e: any) {
      alert(e.message);
    }
  }

  async function handleToggleActive(source: Source) {
    await adminFetch(`/api/admin/sources/${source.id}`, {
      method: "PUT",
      body: JSON.stringify({ active: !source.active }),
    });
    await reload();
  }

  async function handleDelete(source: Source) {
    if (!confirm(`Delete ${source.name}? This cascades to all articles and logs.`)) return;
    await adminFetch(`/api/admin/sources/${source.id}`, { method: "DELETE" });
    await reload();
  }

  async function handleAdd(e: React.FormEvent) {
    e.preventDefault();
    try {
      await adminFetch("/api/admin/sources", {
        method: "POST",
        body: JSON.stringify(form),
      });
      setShowAdd(false);
      setForm({ name: "", slug: "", surface: "news", homepage_url: "", feed_url: "", adapter_type: "rss", fetch_interval: 15 });
      await reload();
    } catch (e: any) {
      alert(e.message);
    }
  }

  async function handleUpdate(id: string, updates: Partial<Source>) {
    await adminFetch(`/api/admin/sources/${id}`, {
      method: "PUT",
      body: JSON.stringify(updates),
    });
    setEditId(null);
    await reload();
  }

  async function handleShowLogs(sourceId: string) {
    if (logs?.sourceId === sourceId) { setLogs(null); return; }
    const entries = await adminFetch<FetchLogEntry[]>(`/api/admin/sources/${sourceId}/fetch-logs`);
    setLogs({ sourceId, entries });
  }

  return (
    <div className="space-y-4 max-w-6xl">
      <div className="flex items-center justify-between">
        <h1 className="text-xl font-semibold text-primary">Sources</h1>
        <div className="flex gap-2">
          <button onClick={() => setShowAdd(!showAdd)} className="px-3 py-1.5 rounded text-sm bg-accent text-white hover:bg-accent-hover">
            Add Source
          </button>
          <button onClick={handleRefreshAll} disabled={refreshing} className="px-3 py-1.5 rounded text-sm border border-rule text-secondary hover:text-primary disabled:opacity-50">
            {refreshing ? "Refreshing..." : "Refresh All"}
          </button>
        </div>
      </div>

      {/* Refresh status banner */}
      {refreshStatus && (
        <div className="border border-rule rounded p-3 space-y-1">
          {Object.entries(refreshStatus).map(([name, s]) => (
            <div key={name} className="flex items-center gap-2 text-sm">
              <span className={`w-2 h-2 rounded-full ${s.status === "success" ? "bg-status-ok" : "bg-status-error"}`} />
              <span className="text-primary">{name}</span>
              <span className="text-muted">+{s.articles_new} new</span>
            </div>
          ))}
        </div>
      )}

      {showAdd && (
        <SourceAddForm
          form={form}
          setForm={setForm}
          onSubmit={handleAdd}
          onCancel={() => setShowAdd(false)}
        />
      )}

      {/* Sources table */}
      <div className="border border-rule rounded overflow-hidden">
        <div className="overflow-x-auto">
        <table className="w-full text-sm">
          <thead className="bg-surface-alt text-left">
            <tr>
              <th className="px-3 py-2 text-secondary font-medium">Name</th>
              <th className="px-3 py-2 text-secondary font-medium">Surface</th>
              <th className="px-3 py-2 text-secondary font-medium">Status</th>
              <th className="px-3 py-2 text-secondary font-medium">Last Fetch</th>
              <th className="px-3 py-2 text-secondary font-medium">Interval</th>
              <th className="px-3 py-2 text-secondary font-medium text-right">Actions</th>
            </tr>
          </thead>
          <tbody>
            {sourceList.map((source) => (
              <>
                <tr key={source.id} className={`border-t border-rule ${source.consecutive_failures >= 5 ? "bg-red-50" : ""}`}>
                  <td className="px-3 py-2 text-primary font-medium">{source.name}</td>
                  <td className="px-3 py-2 text-secondary">{source.surface}</td>
                  <td className="px-3 py-2"><StatusBadge source={source} /></td>
                  <td className="px-3 py-2 text-secondary">
                    {source.last_fetched_at
                      ? new Date(source.last_fetched_at).toLocaleString()
                      : "Never"}
                  </td>
                  <td className="px-3 py-2 text-secondary">{source.fetch_interval}m</td>
                  <td className="px-3 py-2 text-right">
                    <div className="flex gap-1 justify-end">
                      <button onClick={() => handleRefreshOne(source.id)} className="px-2 py-1 rounded text-xs border border-rule text-secondary hover:text-primary">Refresh</button>
                      <button onClick={() => handleTestFetch(source.id)} className="px-2 py-1 rounded text-xs border border-rule text-secondary hover:text-primary">Test</button>
                      <button onClick={() => handleToggleActive(source)} className="px-2 py-1 rounded text-xs border border-rule text-secondary hover:text-primary">
                        {source.active ? "Disable" : "Enable"}
                      </button>
                      <button onClick={() => handleShowLogs(source.id)} className="px-2 py-1 rounded text-xs border border-rule text-secondary hover:text-primary">Logs</button>
                      <button onClick={() => handleDelete(source)} className="px-2 py-1 rounded text-xs border border-rule text-status-error hover:bg-red-50">Delete</button>
                    </div>
                  </td>
                </tr>
                {logs?.sourceId === source.id && (
                  <tr key={`${source.id}-logs`} className="border-t border-rule">
                    <td colSpan={6} className="px-3 py-2 bg-surface-alt">
                      <p className="text-xs text-secondary font-semibold mb-2">Recent Fetch Logs</p>
                      {logs.entries.length === 0 ? (
                        <p className="text-xs text-muted">No logs</p>
                      ) : (
                        <div className="space-y-1 max-h-48 overflow-y-auto">
                          {logs.entries.map((log) => (
                            <div key={log.id} className="flex items-center gap-3 text-xs">
                              <span className={`w-2 h-2 rounded-full ${log.status === "success" ? "bg-status-ok" : log.status === "partial" ? "bg-status-warn" : "bg-status-error"}`} />
                              <span className="text-muted w-36">{new Date(log.started_at).toLocaleString()}</span>
                              <span className="text-secondary">{log.trigger}</span>
                              <span className="text-secondary">+{log.articles_new} new</span>
                              {log.duration_ms != null && <span className="text-muted">{log.duration_ms}ms</span>}
                              {log.error_message && <span className="text-status-error truncate max-w-xs">{log.error_message}</span>}
                            </div>
                          ))}
                        </div>
                      )}
                    </td>
                  </tr>
                )}
              </>
            ))}
          </tbody>
        </table>
        </div>
      </div>
    </div>
  );
}
