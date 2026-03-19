type FormState = {
  provider: string;
  model_id: string;
  display_name: string;
  input_price_per_mtok: string;
  output_price_per_mtok: string;
};

type Props = {
  form: FormState;
  setForm: (form: FormState) => void;
  onSubmit: (e: React.FormEvent) => void;
  onCancel: () => void;
};

export function ModelAddForm({ form, setForm, onSubmit, onCancel }: Props) {
  return (
    <form onSubmit={onSubmit} className="border border-rule rounded p-3 space-y-2 bg-surface-alt mb-3">
      <div className="grid grid-cols-3 gap-2">
        <select value={form.provider} onChange={(e) => setForm({ ...form, provider: e.target.value })} className="px-2 py-1 rounded border border-rule bg-surface text-sm text-primary">
          <option value="anthropic">Anthropic</option>
          <option value="openai">OpenAI</option>
          <option value="google">Google</option>
        </select>
        <input placeholder="Model ID" value={form.model_id} onChange={(e) => setForm({ ...form, model_id: e.target.value })} className="px-2 py-1 rounded border border-rule bg-surface text-sm text-primary" required />
        <input placeholder="Display Name" value={form.display_name} onChange={(e) => setForm({ ...form, display_name: e.target.value })} className="px-2 py-1 rounded border border-rule bg-surface text-sm text-primary" required />
      </div>
      <div className="grid grid-cols-2 gap-2">
        <input placeholder="Input price/Mtok" value={form.input_price_per_mtok} onChange={(e) => setForm({ ...form, input_price_per_mtok: e.target.value })} className="px-2 py-1 rounded border border-rule bg-surface text-sm text-primary" />
        <input placeholder="Output price/Mtok" value={form.output_price_per_mtok} onChange={(e) => setForm({ ...form, output_price_per_mtok: e.target.value })} className="px-2 py-1 rounded border border-rule bg-surface text-sm text-primary" />
      </div>
      <div className="flex gap-2">
        <button type="submit" className="px-3 py-1 rounded text-xs bg-accent text-white">Create</button>
        <button type="button" onClick={onCancel} className="px-3 py-1 rounded text-xs border border-rule text-secondary">Cancel</button>
      </div>
    </form>
  );
}
