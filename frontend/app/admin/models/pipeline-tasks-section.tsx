type LLMModel = {
  model_id: string;
  display_name: string;
  active: boolean;
};

type PipelineTask = {
  task: string;
  model_id: string;
  active: boolean;
  config: Record<string, any>;
};

type CostEstimate = Record<string, {
  weekly_cost_usd: number;
  daily_cost_usd: number;
  monthly_cost_usd: number;
}>;

type Props = {
  tasks: PipelineTask[];
  activeModels: LLMModel[];
  costs: CostEstimate;
  onUpdateTask: (taskName: string, updates: Partial<PipelineTask>) => void;
};

export function PipelineTasksSection({ tasks, activeModels, costs, onUpdateTask }: Props) {
  return (
    <section>
      <h2 className="text-sm font-semibold text-secondary uppercase tracking-wider mb-3">Pipeline Tasks</h2>
      <div className="border border-rule rounded divide-y divide-rule">
        {tasks.map((task) => (
          <div key={task.task} className="px-3 py-3 flex items-center gap-4">
            <div className="flex-1">
              <span className="text-primary font-medium text-sm">{task.task}</span>
              <span className={`ml-2 text-xs px-2 py-0.5 rounded ${task.active ? "bg-green-100 text-status-ok" : "bg-gray-200 text-gray-600"}`}>
                {task.active ? "Active" : "Inactive"}
              </span>
            </div>
            <select
              value={task.model_id}
              onChange={(e) => onUpdateTask(task.task, { model_id: e.target.value })}
              className="px-2 py-1 rounded border border-rule bg-surface text-sm text-primary"
            >
              {activeModels.map((m) => (
                <option key={m.model_id} value={m.model_id}>{m.display_name}</option>
              ))}
              {!activeModels.find((m) => m.model_id === task.model_id) && (
                <option value={task.model_id}>{task.model_id} (inactive)</option>
              )}
            </select>
            <button
              onClick={() => onUpdateTask(task.task, { active: !task.active })}
              className="px-2 py-1 rounded text-xs border border-rule text-secondary hover:text-primary"
            >
              {task.active ? "Disable" : "Enable"}
            </button>
            {costs[task.task] && (
              <span className="text-xs text-muted w-28 text-right">
                ~${costs[task.task].monthly_cost_usd.toFixed(2)}/mo
              </span>
            )}
          </div>
        ))}
      </div>
    </section>
  );
}
