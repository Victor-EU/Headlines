type Source = {
  id: string;
  name: string;
  surface: string;
};

type Category = {
  id: string;
  name: string;
  slug: string;
  surface: string;
};

type Props = {
  search: string;
  setSearch: (v: string) => void;
  filterSurface: string;
  setFilterSurface: (v: string) => void;
  filterSource: string;
  setFilterSource: (v: string) => void;
  filterCategory: string;
  setFilterCategory: (v: string) => void;
  filterClassified: string;
  setFilterClassified: (v: string) => void;
  filterHidden: string;
  setFilterHidden: (v: string) => void;
  sources: Source[];
  categories: Category[];
  onSearch: (e: React.FormEvent) => void;
  onResetPage: () => void;
};

export function ArticleFilters({
  search, setSearch,
  filterSurface, setFilterSurface,
  filterSource, setFilterSource,
  filterCategory, setFilterCategory,
  filterClassified, setFilterClassified,
  filterHidden, setFilterHidden,
  sources, categories,
  onSearch, onResetPage,
}: Props) {
  return (
    <div className="flex gap-3 items-center flex-wrap">
      <form onSubmit={onSearch} className="flex gap-2">
        <input
          placeholder="Search titles..."
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          className="w-64 px-3 py-1.5 rounded border border-rule bg-surface text-sm text-primary"
        />
        <button type="submit" className="px-3 py-1.5 rounded text-sm bg-accent text-white">Search</button>
      </form>
      <select value={filterSurface} onChange={(e) => { setFilterSurface(e.target.value); onResetPage(); }} className="px-2 py-1.5 rounded border border-rule bg-surface text-sm text-primary">
        <option value="">All surfaces</option>
        <option value="news">News</option>
        <option value="learning">Learning</option>
      </select>
      <select value={filterSource} onChange={(e) => { setFilterSource(e.target.value); onResetPage(); }} className="px-2 py-1.5 rounded border border-rule bg-surface text-sm text-primary">
        <option value="">All sources</option>
        {sources.map((s) => <option key={s.id} value={s.id}>{s.name}</option>)}
      </select>
      <select value={filterCategory} onChange={(e) => { setFilterCategory(e.target.value); onResetPage(); }} className="px-2 py-1.5 rounded border border-rule bg-surface text-sm text-primary">
        <option value="">All categories</option>
        {categories.map((c) => <option key={c.id} value={c.slug}>{c.name}</option>)}
      </select>
      <select value={filterClassified} onChange={(e) => { setFilterClassified(e.target.value); onResetPage(); }} className="px-2 py-1.5 rounded border border-rule bg-surface text-sm text-primary">
        <option value="">All</option>
        <option value="true">Classified</option>
        <option value="false">Unclassified</option>
      </select>
      <select value={filterHidden} onChange={(e) => { setFilterHidden(e.target.value); onResetPage(); }} className="px-2 py-1.5 rounded border border-rule bg-surface text-sm text-primary">
        <option value="">Visible + Hidden</option>
        <option value="false">Visible only</option>
        <option value="true">Hidden only</option>
      </select>
    </div>
  );
}
