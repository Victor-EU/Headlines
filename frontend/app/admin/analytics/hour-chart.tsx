type HourMetric = {
  hour: number;
  page_views: number;
  clicks: number;
};

type Props = {
  hours: HourMetric[];
  maxPageViews: number;
};

export function HourChart({ hours, maxPageViews }: Props) {
  return (
    <>
      <div className="flex items-end gap-px h-32">
        {hours.map((h) => (
          <div key={h.hour} className="flex-1 flex flex-col items-center gap-0.5">
            <div className="w-full flex flex-col justify-end h-24">
              <div
                className="bg-accent rounded-t w-full"
                style={{ height: `${maxPageViews > 0 ? (h.page_views / maxPageViews) * 100 : 0}%` }}
              />
            </div>
            <span className="text-[10px] text-muted">{h.hour}</span>
          </div>
        ))}
      </div>
      <div className="flex justify-between mt-1">
        <span className="text-[10px] text-muted">12am</span>
        <span className="text-[10px] text-muted">12pm</span>
        <span className="text-[10px] text-muted">11pm</span>
      </div>
    </>
  );
}
