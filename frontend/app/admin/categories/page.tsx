"use client";

import { useState, useRef } from "react";
import { adminFetch, getToken } from "@/lib/admin-api";
import { useAdminData } from "@/app/admin/_hooks/use-admin-data";
import { AdminPageSkeleton } from "@/components/Skeleton";
import { CategorySurfaceList } from "./category-surface-list";
import { CategoryPreviewPanel } from "./category-preview-panel";
import { CategoryMergeModal } from "./category-merge-modal";

export type Category = {
  id: string;
  name: string;
  slug: string;
  surface: string;
  description: string;
  display_order: number;
  active: boolean;
  article_count: number;
};

export type PreviewResult = {
  would_match: { article_id: string; title: string; confidence: number }[];
  currently_matched: { article_id: string; title: string; confidence: number }[];
};

export default function CategoriesPage() {
  const { data: categories, loading, reload } = useAdminData(
    () => adminFetch<Category[]>("/api/admin/categories"),
  );

  const [addSurface, setAddSurface] = useState<string | null>(null);
  const [form, setForm] = useState({ name: "", surface: "news", description: "" });
  const [editId, setEditId] = useState<string | null>(null);
  const [editForm, setEditForm] = useState({ name: "", slug: "", description: "", active: true });
  const [preview, setPreview] = useState<{ categoryId: string; result: PreviewResult } | null>(null);
  const [previewLoading, setPreviewLoading] = useState(false);
  const [mergeId, setMergeId] = useState<string | null>(null);
  const [mergeTarget, setMergeTarget] = useState("");
  const [reclassJob, setReclassJob] = useState<{ id: string; status: string; total: number; processed: number } | null>(null);
  const dragItem = useRef<string | null>(null);
  const dragOverItem = useRef<string | null>(null);

  const cats = categories ?? [];
  const newsCats = cats.filter((c) => c.surface === "news");
  const learningCats = cats.filter((c) => c.surface === "learning");

  async function handleAdd(e: React.FormEvent) {
    e.preventDefault();
    try {
      await adminFetch("/api/admin/categories", {
        method: "POST",
        body: JSON.stringify(form),
      });
      setAddSurface(null);
      setForm({ name: "", surface: "news", description: "" });
      await reload();
    } catch (e: any) {
      alert(e.message);
    }
  }

  function startEdit(cat: Category) {
    setEditId(cat.id);
    setEditForm({ name: cat.name, slug: cat.slug, description: cat.description, active: cat.active });
  }

  async function saveEdit() {
    if (!editId) return;
    try {
      await adminFetch(`/api/admin/categories/${editId}`, {
        method: "PUT",
        body: JSON.stringify(editForm),
      });
      setEditId(null);
      await reload();
    } catch (e: any) {
      alert(e.message);
    }
  }

  async function handleDelete(cat: Category) {
    if (!confirm(`Delete "${cat.name}"? This unlinks all article assignments.`)) return;
    await adminFetch(`/api/admin/categories/${cat.id}`, { method: "DELETE" });
    await reload();
  }

  async function handlePreview(cat: Category) {
    setPreviewLoading(true);
    setPreview(null);
    try {
      const result = await adminFetch<PreviewResult>(`/api/admin/categories/${cat.id}/preview`, {
        method: "POST",
        body: JSON.stringify({ description: null }),
      });
      setPreview({ categoryId: cat.id, result });
    } catch (e: any) {
      alert(e.message);
    } finally {
      setPreviewLoading(false);
    }
  }

  async function handleMerge() {
    if (!mergeId || !mergeTarget) return;
    if (!confirm("Merge categories? This cannot be undone.")) return;
    try {
      await adminFetch(`/api/admin/categories/${mergeId}/merge`, {
        method: "POST",
        body: JSON.stringify({ target_id: mergeTarget }),
      });
      setMergeId(null);
      setMergeTarget("");
      await reload();
    } catch (e: any) {
      alert(e.message);
    }
  }

  async function handleDrop(surface: string) {
    if (!dragItem.current || !dragOverItem.current || dragItem.current === dragOverItem.current) return;
    const surfaceCats = cats.filter((c) => c.surface === surface);
    const items = [...surfaceCats];
    const dragIdx = items.findIndex((c) => c.id === dragItem.current);
    const overIdx = items.findIndex((c) => c.id === dragOverItem.current);
    if (dragIdx < 0 || overIdx < 0) return;

    const [removed] = items.splice(dragIdx, 1);
    items.splice(overIdx, 0, removed);

    const reorder = items.map((c, i) => ({ id: c.id, display_order: i }));
    await adminFetch("/api/admin/categories/reorder", {
      method: "PUT",
      body: JSON.stringify(reorder),
    });
    await reload();
    dragItem.current = null;
    dragOverItem.current = null;
  }

  async function handleReclassify(since: string) {
    try {
      const result = await adminFetch<{ job_id: string; total: number }>("/api/admin/reclassify", {
        method: "POST",
        body: JSON.stringify({ since }),
      });
      setReclassJob({ id: result.job_id, status: "starting", total: result.total, processed: 0 });
      pollReclassify(result.job_id);
    } catch (e: any) {
      alert(e.message);
    }
  }

  async function pollReclassify(jobId: string) {
    const poll = async () => {
      const result = await adminFetch<{ status: string; total: number; processed: number }>(`/api/admin/reclassify/${jobId}`);
      setReclassJob({ id: jobId, ...result });
      if (result.status === "running" || result.status === "starting") {
        setTimeout(poll, 2000);
      } else {
        await reload();
      }
    };
    setTimeout(poll, 2000);
  }

  async function handleFlushCache() {
    try {
      const token = getToken();
      if (!token) return;
      const res = await fetch("/api/revalidate", {
        method: "POST",
        headers: { Authorization: `Bearer ${token}` },
      });
      if (!res.ok) throw new Error("Failed");
      alert("Cache flushed");
    } catch {
      alert("Failed to flush cache");
    }
  }

  if (loading) return <AdminPageSkeleton />;

  const dragHandlers = {
    onDragStart: (id: string) => { dragItem.current = id; },
    onDragOver: (id: string) => { dragOverItem.current = id; },
    onDrop: (surface: string) => handleDrop(surface),
  };

  return (
    <div className="space-y-6 max-w-4xl">
      <div className="flex items-center justify-between">
        <h1 className="text-xl font-semibold text-primary">Categories</h1>
        <div className="flex gap-2">
          <button onClick={() => handleReclassify("24h")} className="px-3 py-1.5 rounded text-sm border border-rule text-secondary hover:text-primary">
            Reclassify 24h
          </button>
          <button onClick={() => handleReclassify("7d")} className="px-3 py-1.5 rounded text-sm border border-rule text-secondary hover:text-primary">
            Reclassify 7d
          </button>
          <button onClick={handleFlushCache} className="px-3 py-1.5 rounded text-sm border border-rule text-secondary hover:text-primary">
            Flush Cache
          </button>
        </div>
      </div>

      {/* Reclassify progress */}
      {reclassJob && (
        <div className="border border-rule rounded p-3 text-sm">
          <span className="text-primary font-medium">Reclassification: </span>
          <span className="text-secondary">
            {reclassJob.status === "complete"
              ? `Done (${reclassJob.total} articles)`
              : reclassJob.status.startsWith("failed")
                ? reclassJob.status
                : `${reclassJob.status} — ${reclassJob.total} articles`}
          </span>
        </div>
      )}

      {preview && (
        <CategoryPreviewPanel preview={preview} onClose={() => setPreview(null)} />
      )}

      {mergeId && (
        <CategoryMergeModal
          mergeId={mergeId}
          categories={cats}
          mergeTarget={mergeTarget}
          setMergeTarget={setMergeTarget}
          onMerge={handleMerge}
          onClose={() => setMergeId(null)}
        />
      )}

      <CategorySurfaceList
        surfaceName="News"
        cats={newsCats}
        editId={editId}
        editForm={editForm}
        onEditFormChange={setEditForm}
        onStartEdit={startEdit}
        onSaveEdit={saveEdit}
        onCancelEdit={() => setEditId(null)}
        onPreview={handlePreview}
        onMerge={(id) => { setMergeId(id); setMergeTarget(""); }}
        onDelete={handleDelete}
        dragHandlers={dragHandlers}
        addSurface={addSurface}
        onSetAddSurface={setAddSurface}
        form={form}
        onFormChange={setForm}
        onAdd={handleAdd}
      />
      <CategorySurfaceList
        surfaceName="Learning"
        cats={learningCats}
        editId={editId}
        editForm={editForm}
        onEditFormChange={setEditForm}
        onStartEdit={startEdit}
        onSaveEdit={saveEdit}
        onCancelEdit={() => setEditId(null)}
        onPreview={handlePreview}
        onMerge={(id) => { setMergeId(id); setMergeTarget(""); }}
        onDelete={handleDelete}
        dragHandlers={dragHandlers}
        addSurface={addSurface}
        onSetAddSurface={setAddSurface}
        form={form}
        onFormChange={setForm}
        onAdd={handleAdd}
      />
    </div>
  );
}
