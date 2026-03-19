import type { SurfaceConfig } from "@/lib/surfaces";
import type { HeadlineData } from "@/lib/types";
import { formatTime } from "@/lib/time";

type Props = {
  headline: HeadlineData;
  config: SurfaceConfig;
};

export function LeadHeadline({ headline, config }: Props) {
  return (
    <a
      href={headline.url}
      target="_blank"
      rel="noopener"
      className="block group mb-6 pb-6 border-b border-rule"
      data-article-id={headline.id}
      data-source-slug={headline.source_slug}
    >
      <h2 className="font-serif text-headline-lead text-headline group-hover:text-headline-hover transition-colors">
        {headline.title}
      </h2>
      <p className="text-meta mt-2">
        <span className="text-source">{headline.source_name}</span>
        <span className="text-meta"> · {formatTime(headline.published_at, config.timeFormat)}</span>
      </p>
      {config.showAlsoReportedBy && headline.also_reported_by.length > 0 && (
        <p className="text-meta text-muted mt-1">
          Also in:{" "}
          {headline.also_reported_by.map((s, i) => (
            <span key={s.source_slug}>
              {i > 0 && ", "}
              <a
                href={s.url}
                target="_blank"
                rel="noopener"
                className="hover:text-accent transition-colors"
              >
                {s.source_name}
              </a>
            </span>
          ))}
        </p>
      )}
    </a>
  );
}
