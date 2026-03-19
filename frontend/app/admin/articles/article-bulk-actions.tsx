type Category = {
  id: string;
  name: string;
  slug: string;
  surface: string;
};

type Props = {
  selectedCount: number;
  categories: Category[];
  onAction: (action: string, categoryId?: string) => void;
};

export function ArticleBulkActions({ selectedCount, categories, onAction }: Props) {
  return (
    <div className="flex items-center gap-3 p-2 bg-surface-alt rounded border border-rule">
      <span className="text-sm text-secondary">{selectedCount} selected</span>
      <button onClick={() => onAction("hide")} className="px-3 py-1 rounded text-xs bg-accent text-white">Hide</button>
      <button onClick={() => onAction("unhide")} className="px-3 py-1 rounded text-xs border border-rule text-secondary">Unhide</button>
      <select
        onChange={(e) => { if (e.target.value) { onAction("assign_category", e.target.value); e.target.value = ""; } }}
        className="px-2 py-1 rounded text-xs border border-rule bg-surface text-primary"
      >
        <option value="">Assign category...</option>
        {categories.map((c) => <option key={c.id} value={c.id}>{c.name}</option>)}
      </select>
    </div>
  );
}
