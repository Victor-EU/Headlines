type BarItem = {
  key: string;
  label: string;
  value: number;
  extras?: { label: string; value: string; className?: string }[];
};

type Props = {
  items: BarItem[];
  maxValue: number;
};

export function HorizontalBarChart({ items, maxValue }: Props) {
  return (
    <div className="space-y-2">
      {items.map((item) => (
        <div key={item.key} className="flex items-center gap-3">
          <span className="text-sm text-primary w-40 shrink-0 truncate">
            {item.label}
          </span>
          <div className="flex-1 bg-surface-alt rounded h-5">
            <div
              className="bg-accent h-full rounded"
              style={{ width: `${(item.value / maxValue) * 100}%` }}
            />
          </div>
          {item.extras?.map((extra) => (
            <span key={extra.label} className={extra.className ?? "text-sm text-secondary w-16 text-right"}>
              {extra.value}
            </span>
          ))}
        </div>
      ))}
    </div>
  );
}
