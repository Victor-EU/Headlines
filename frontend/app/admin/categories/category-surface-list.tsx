import type { Category } from "./page";

type DragHandlers = {
  onDragStart: (id: string) => void;
  onDragOver: (id: string) => void;
  onDrop: (surface: string) => void;
};

type Props = {
  surfaceName: string;
  cats: Category[];
  editId: string | null;
  editForm: { name: string; slug: string; description: string; active: boolean };
  onEditFormChange: (form: { name: string; slug: string; description: string; active: boolean }) => void;
  onStartEdit: (cat: Category) => void;
  onSaveEdit: () => void;
  onCancelEdit: () => void;
  onPreview: (cat: Category) => void;
  onMerge: (catId: string) => void;
  onDelete: (cat: Category) => void;
  dragHandlers: DragHandlers;
  addSurface: string | null;
  onSetAddSurface: (surface: string | null) => void;
  form: { name: string; surface: string; description: string };
  onFormChange: (form: { name: string; surface: string; description: string }) => void;
  onAdd: (e: React.FormEvent) => void;
};

export function CategorySurfaceList({
  surfaceName,
  cats,
  editId,
  editForm,
  onEditFormChange,
  onStartEdit,
  onSaveEdit,
  onCancelEdit,
  onPreview,
  onMerge,
  onDelete,
  dragHandlers,
  addSurface,
  onSetAddSurface,
  form,
  onFormChange,
  onAdd,
}: Props) {
  const surfaceKey = surfaceName.toLowerCase();

  return (
    <section className="space-y-3">
      <div className="flex items-center justify-between">
        <h2 className="text-sm font-semibold text-secondary uppercase tracking-wider">{surfaceName}</h2>
        <button onClick={() => { onSetAddSurface(surfaceKey); onFormChange({ ...form, surface: surfaceKey }); }} className="text-xs px-2 py-1 rounded border border-rule text-secondary hover:text-primary">
          + Add Category
        </button>
      </div>
      <div className="border border-rule rounded divide-y divide-rule">
        {cats.map((cat) => (
          <div
            key={cat.id}
            draggable
            onDragStart={() => dragHandlers.onDragStart(cat.id)}
            onDragOver={(e) => { e.preventDefault(); dragHandlers.onDragOver(cat.id); }}
            onDrop={() => dragHandlers.onDrop(surfaceKey)}
            className={`px-3 py-2 flex items-center gap-3 cursor-move ${!cat.active ? "opacity-50" : ""}`}
          >
            <span className="text-muted cursor-grab select-none">::</span>
            {editId === cat.id ? (
              <div className="flex-1 space-y-2">
                <div className="flex gap-2">
                  <input value={editForm.name} onChange={(e) => onEditFormChange({ ...editForm, name: e.target.value })} className="flex-1 px-2 py-1 rounded border border-rule bg-surface text-sm text-primary" />
                  <input value={editForm.slug} onChange={(e) => onEditFormChange({ ...editForm, slug: e.target.value })} className="w-40 px-2 py-1 rounded border border-rule bg-surface text-sm text-muted" />
                </div>
                <textarea value={editForm.description} onChange={(e) => onEditFormChange({ ...editForm, description: e.target.value })} rows={2} className="w-full px-2 py-1 rounded border border-rule bg-surface text-sm text-primary" />
                <div className="flex gap-2">
                  <button onClick={onSaveEdit} className="px-3 py-1 rounded text-xs bg-accent text-white">Save</button>
                  <button onClick={onCancelEdit} className="px-3 py-1 rounded text-xs border border-rule text-secondary">Cancel</button>
                  <label className="flex items-center gap-1 text-xs text-secondary">
                    <input type="checkbox" checked={editForm.active} onChange={(e) => onEditFormChange({ ...editForm, active: e.target.checked })} />
                    Active
                  </label>
                </div>
              </div>
            ) : (
              <>
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-2">
                    <span className="text-primary font-medium text-sm cursor-pointer hover:underline" onClick={() => onStartEdit(cat)}>{cat.name}</span>
                    <span className="text-xs text-muted">{cat.slug}</span>
                    <span className="text-xs px-1.5 py-0.5 rounded bg-surface-alt text-secondary">{cat.article_count}</span>
                  </div>
                  <p className="text-xs text-secondary truncate mt-0.5">{cat.description}</p>
                </div>
                <div className="flex gap-1 shrink-0">
                  <button onClick={() => onPreview(cat)} className="px-2 py-1 rounded text-xs border border-rule text-secondary hover:text-primary">Preview</button>
                  <button onClick={() => onMerge(cat.id)} className="px-2 py-1 rounded text-xs border border-rule text-secondary hover:text-primary">Merge</button>
                  <button onClick={() => onDelete(cat)} className="px-2 py-1 rounded text-xs border border-rule text-status-error">Delete</button>
                </div>
              </>
            )}
          </div>
        ))}
      </div>

      {addSurface === surfaceKey && (
        <form onSubmit={onAdd} className="border border-rule rounded p-3 space-y-2 bg-surface-alt">
          <input placeholder="Category name" value={form.name} onChange={(e) => onFormChange({ ...form, name: e.target.value })} className="w-full px-2 py-1 rounded border border-rule bg-surface text-sm text-primary" required />
          <textarea placeholder="Description (used for classification)" value={form.description} onChange={(e) => onFormChange({ ...form, description: e.target.value })} rows={2} className="w-full px-2 py-1 rounded border border-rule bg-surface text-sm text-primary" required />
          <div className="flex gap-2">
            <button type="submit" className="px-3 py-1 rounded text-xs bg-accent text-white">Create</button>
            <button type="button" onClick={() => onSetAddSurface(null)} className="px-3 py-1 rounded text-xs border border-rule text-secondary">Cancel</button>
          </div>
        </form>
      )}
    </section>
  );
}
