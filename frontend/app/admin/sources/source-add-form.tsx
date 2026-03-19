type FormState = {
  name: string;
  slug: string;
  surface: string;
  homepage_url: string;
  feed_url: string;
  adapter_type: string;
  fetch_interval: number;
};

type Props = {
  form: FormState;
  setForm: (form: FormState) => void;
  onSubmit: (e: React.FormEvent) => void;
  onCancel: () => void;
};

export function SourceAddForm({ form, setForm, onSubmit, onCancel }: Props) {
  return (
    <form onSubmit={onSubmit} className="border border-rule rounded p-4 space-y-3 bg-surface-alt">
      <div className="grid grid-cols-3 gap-3">
        <input placeholder="Name" value={form.name} onChange={(e) => setForm({ ...form, name: e.target.value })} className="px-3 py-2 rounded border border-rule bg-surface text-sm text-primary" required />
        <input placeholder="Slug" value={form.slug} onChange={(e) => setForm({ ...form, slug: e.target.value })} className="px-3 py-2 rounded border border-rule bg-surface text-sm text-primary" required />
        <select value={form.surface} onChange={(e) => setForm({ ...form, surface: e.target.value })} className="px-3 py-2 rounded border border-rule bg-surface text-sm text-primary">
          <option value="news">News</option>
          <option value="learning">Learning</option>
        </select>
      </div>
      <div className="grid grid-cols-2 gap-3">
        <input placeholder="Feed URL" value={form.feed_url} onChange={(e) => setForm({ ...form, feed_url: e.target.value })} className="px-3 py-2 rounded border border-rule bg-surface text-sm text-primary" required />
        <input placeholder="Homepage URL" value={form.homepage_url} onChange={(e) => setForm({ ...form, homepage_url: e.target.value })} className="px-3 py-2 rounded border border-rule bg-surface text-sm text-primary" required />
      </div>
      <div className="flex gap-3 items-center">
        <input type="number" placeholder="Interval (min)" value={form.fetch_interval} onChange={(e) => setForm({ ...form, fetch_interval: Number(e.target.value) })} className="w-32 px-3 py-2 rounded border border-rule bg-surface text-sm text-primary" />
        <button type="submit" className="px-4 py-2 rounded bg-accent text-white text-sm hover:bg-accent-hover">Create</button>
        <button type="button" onClick={onCancel} className="px-4 py-2 rounded border border-rule text-sm text-secondary">Cancel</button>
      </div>
    </form>
  );
}
