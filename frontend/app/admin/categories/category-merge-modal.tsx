import type { Category } from "./page";

type Props = {
  mergeId: string;
  categories: Category[];
  mergeTarget: string;
  setMergeTarget: (target: string) => void;
  onMerge: () => void;
  onClose: () => void;
};

export function CategoryMergeModal({
  mergeId,
  categories,
  mergeTarget,
  setMergeTarget,
  onMerge,
  onClose,
}: Props) {
  return (
    <div className="border border-rule rounded p-4 bg-surface-alt space-y-3">
      <h3 className="text-sm font-semibold text-primary">
        Merge &ldquo;{categories.find((c) => c.id === mergeId)?.name}&rdquo; into:
      </h3>
      <select value={mergeTarget} onChange={(e) => setMergeTarget(e.target.value)} className="px-3 py-2 rounded border border-rule bg-surface text-sm text-primary">
        <option value="">Select target...</option>
        {categories.filter((c) => c.id !== mergeId && c.surface === categories.find((x) => x.id === mergeId)?.surface).map((c) => (
          <option key={c.id} value={c.id}>{c.name}</option>
        ))}
      </select>
      <div className="flex gap-2">
        <button onClick={onMerge} disabled={!mergeTarget} className="px-3 py-1 rounded text-xs bg-status-error text-white disabled:opacity-50">Merge</button>
        <button onClick={onClose} className="px-3 py-1 rounded text-xs border border-rule text-secondary">Cancel</button>
      </div>
    </div>
  );
}
