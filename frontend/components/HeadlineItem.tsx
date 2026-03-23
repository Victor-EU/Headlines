import type { SurfaceConfig } from "@/lib/surfaces";
import type { HeadlineData } from "@/lib/types";
import { formatTime } from "@/lib/time";

type Props = {
  headline: HeadlineData;
  config: SurfaceConfig;
};

export function HeadlineItem({ headline, config }: Props) {
  return (
    <a
      href={headline.url}
      target="_blank"
      rel="noopener"
      className="block group py-4"
      data-article-id={headline.id}
      data-source-slug={headline.source_slug}
    >
      <h2 className="font-serif text-headline text-headline group-hover:text-headline-hover transition-colors">
        {headline.title}
      </h2>
      {config.showSummary && headline.summary && (
        <p className="text-summary text-summary mt-1">{headline.summary}</p>
      )}
      <p className="text-meta mt-1">
        <span className="text-source">{headline.source_name}</span>
        <span className="text-meta" suppressHydrationWarning>
          {" "}
          · {formatTime(headline.published_at, config.timeFormat)}
        </span>
        {config.showAlsoReportedBy && headline.also_reported_by.length > 0 && (
          <span className="text-muted">
            {" · Also in: "}
            {headline.also_reported_by.map((s, i) => (
              <span key={s.source_slug}>
                {i > 0 && ", "}
                <a
                  href={s.url}
                  target="_blank"
                  rel="noopener"
                  className="hover:text-accent transition-colors"
                  onClick={(e) => e.stopPropagation()}
                >
                  {s.source_name}
                </a>
              </span>
            ))}
          </span>
        )}
      </p>
    </a>
  );
}
