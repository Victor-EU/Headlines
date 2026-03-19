"use client";

import { useState } from "react";
import { adminFetch } from "@/lib/admin-api";
import { useAdminData } from "@/app/admin/_hooks/use-admin-data";
import { AdminPageSkeleton } from "@/components/Skeleton";
import { ModelAddForm } from "./model-add-form";
import { PipelineTasksSection } from "./pipeline-tasks-section";

type LLMModel = {
  id: string;
  provider: string;
  model_id: string;
  display_name: string;
  active: boolean;
  input_price_per_mtok: number | null;
  output_price_per_mtok: number | null;
  context_window: number | null;
  max_output_tokens: number | null;
  config: Record<string, any>;
};

type PipelineTask = {
  task: string;
  model_id: string;
  active: boolean;
  config: Record<string, any>;
};

type ProviderStatus = {
  provider: string;
  key_configured: boolean;
  key_masked: string;
};

type CostEstimate = Record<string, {
  weekly_cost_usd: number;
  daily_cost_usd: number;
  monthly_cost_usd: number;
}>;

type ModelsData = {
  models: LLMModel[];
  tasks: PipelineTask[];
  providers: ProviderStatus[];
  costs: CostEstimate;
};

export default function ModelsPage() {
  const { data, loading, reload } = useAdminData(async () => {
    const [models, tasks, providers, costs] = await Promise.all([
      adminFetch<LLMModel[]>("/api/admin/models"),
      adminFetch<PipelineTask[]>("/api/admin/tasks"),
      adminFetch<ProviderStatus[]>("/api/admin/models/providers"),
      adminFetch<CostEstimate>("/api/admin/tasks/cost-estimate"),
    ]);
    return { models, tasks, providers, costs } as ModelsData;
  });

  const [showAdd, setShowAdd] = useState(false);
  const [form, setForm] = useState({
    provider: "anthropic", model_id: "", display_name: "",
    input_price_per_mtok: "", output_price_per_mtok: "",
  });
  const [testResult, setTestResult] = useState<{ model_id: string; data: any } | null>(null);

  if (loading) return <AdminPageSkeleton />;
  if (!data) return null;

  const { models, tasks, providers, costs } = data;
  const activeModels = models.filter((m) => m.active);

  async function handleAddModel(e: React.FormEvent) {
    e.preventDefault();
    try {
      await adminFetch("/api/admin/models", {
        method: "POST",
        body: JSON.stringify({
          ...form,
          input_price_per_mtok: form.input_price_per_mtok ? Number(form.input_price_per_mtok) : null,
          output_price_per_mtok: form.output_price_per_mtok ? Number(form.output_price_per_mtok) : null,
        }),
      });
      setShowAdd(false);
      setForm({ provider: "anthropic", model_id: "", display_name: "", input_price_per_mtok: "", output_price_per_mtok: "" });
      await reload();
    } catch (e: any) {
      alert(e.message);
    }
  }

  async function handleToggleModel(model: LLMModel) {
    await adminFetch(`/api/admin/models/${model.model_id}`, {
      method: "PUT",
      body: JSON.stringify({ active: !model.active }),
    });
    await reload();
  }

  async function handleDeleteModel(model: LLMModel) {
    if (!confirm(`Delete model ${model.display_name}?`)) return;
    try {
      await adminFetch(`/api/admin/models/${model.model_id}`, { method: "DELETE" });
      await reload();
    } catch (e: any) {
      alert(e.message);
    }
  }

  async function handleTestModel(model: LLMModel) {
    setTestResult({ model_id: model.model_id, data: { loading: true } });
    try {
      const result = await adminFetch(`/api/admin/models/${model.model_id}/test`, { method: "POST" });
      setTestResult({ model_id: model.model_id, data: result });
    } catch (e: any) {
      setTestResult({ model_id: model.model_id, data: { success: false, error: e.message } });
    }
  }

  async function handleUpdateTask(taskName: string, updates: Partial<PipelineTask>) {
    try {
      await adminFetch(`/api/admin/tasks/${taskName}`, {
        method: "PUT",
        body: JSON.stringify(updates),
      });
      await reload();
    } catch (e: any) {
      alert(e.message);
    }
  }

  return (
    <div className="space-y-6 max-w-5xl">
      <h1 className="text-xl font-semibold text-primary">Models & Pipeline</h1>

      {/* API Key Status */}
      <section>
        <h2 className="text-sm font-semibold text-secondary uppercase tracking-wider mb-3">API Keys</h2>
        <div className="flex gap-4">
          {providers.map((p) => (
            <div key={p.provider} className="flex items-center gap-2 text-sm">
              <span className={`w-2 h-2 rounded-full ${p.key_configured ? "bg-status-ok" : "bg-status-error"}`} />
              <span className="text-primary capitalize">{p.provider}</span>
              <span className="text-muted">{p.key_masked || "Not set"}</span>
            </div>
          ))}
        </div>
      </section>

      {/* Model Registry */}
      <section>
        <div className="flex items-center justify-between mb-3">
          <h2 className="text-sm font-semibold text-secondary uppercase tracking-wider">Model Registry</h2>
          <button onClick={() => setShowAdd(!showAdd)} className="text-xs px-2 py-1 rounded border border-rule text-secondary hover:text-primary">
            + Add Model
          </button>
        </div>

        {showAdd && (
          <ModelAddForm
            form={form}
            setForm={setForm}
            onSubmit={handleAddModel}
            onCancel={() => setShowAdd(false)}
          />
        )}

        <div className="border border-rule rounded overflow-hidden">
          <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead className="bg-surface-alt text-left">
              <tr>
                <th className="px-3 py-2 text-secondary font-medium">Provider</th>
                <th className="px-3 py-2 text-secondary font-medium">Model</th>
                <th className="px-3 py-2 text-secondary font-medium">Pricing ($/Mtok)</th>
                <th className="px-3 py-2 text-secondary font-medium">Status</th>
                <th className="px-3 py-2 text-secondary font-medium text-right">Actions</th>
              </tr>
            </thead>
            <tbody>
              {models.map((model) => (
                <tr key={model.model_id} className={`border-t border-rule ${!model.active ? "opacity-50" : ""}`}>
                  <td className="px-3 py-2 text-secondary capitalize">{model.provider}</td>
                  <td className="px-3 py-2">
                    <span className="text-primary">{model.display_name}</span>
                    <span className="text-muted text-xs ml-2">{model.model_id}</span>
                  </td>
                  <td className="px-3 py-2 text-secondary">
                    {model.input_price_per_mtok != null ? `$${model.input_price_per_mtok}` : "—"} / {model.output_price_per_mtok != null ? `$${model.output_price_per_mtok}` : "—"}
                  </td>
                  <td className="px-3 py-2">
                    <span className={`text-xs px-2 py-0.5 rounded ${model.active ? "bg-green-100 text-status-ok" : "bg-gray-200 text-gray-600"}`}>
                      {model.active ? "Active" : "Inactive"}
                    </span>
                  </td>
                  <td className="px-3 py-2 text-right">
                    <div className="flex gap-1 justify-end">
                      <button onClick={() => handleTestModel(model)} className="px-2 py-1 rounded text-xs border border-rule text-secondary hover:text-primary">Test</button>
                      <button onClick={() => handleToggleModel(model)} className="px-2 py-1 rounded text-xs border border-rule text-secondary hover:text-primary">
                        {model.active ? "Disable" : "Enable"}
                      </button>
                      <button onClick={() => handleDeleteModel(model)} className="px-2 py-1 rounded text-xs border border-rule text-status-error">Delete</button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
          </div>
        </div>

        {/* Test result */}
        {testResult && (
          <div className="mt-2 border border-rule rounded p-3 text-sm bg-surface-alt">
            <div className="flex items-center justify-between mb-2">
              <span className="font-medium text-primary">Test: {testResult.model_id}</span>
              <button onClick={() => setTestResult(null)} className="text-xs text-secondary hover:text-primary">Close</button>
            </div>
            {testResult.data.loading ? (
              <p className="text-secondary">Testing...</p>
            ) : testResult.data.success ? (
              <div className="space-y-1">
                <p className="text-status-ok">Success — {testResult.data.latency_ms}ms</p>
                <p className="text-muted">Tokens: {testResult.data.input_tokens} in / {testResult.data.output_tokens} out</p>
              </div>
            ) : (
              <p className="text-status-error">{testResult.data.error}</p>
            )}
          </div>
        )}
      </section>

      <PipelineTasksSection
        tasks={tasks}
        activeModels={activeModels}
        costs={costs}
        onUpdateTask={handleUpdateTask}
      />
    </div>
  );
}
