import type { SurfaceConfig } from "@/lib/surfaces";
import { fetchBriefing } from "@/lib/api";

type Props = {
  config: SurfaceConfig;
};

export async function EditorialSummary({ config }: Props) {
  let briefing;
  try {
    briefing = await fetchBriefing(config.briefingType);
  } catch {
    return null;
  }

  if (!briefing?.brief) return null;

  return (
    <section className="mb-8">
      <h3 className="text-section-label text-briefing-label uppercase font-sans">
        {config.briefingLabel}
      </h3>
      <div className="max-w-prose border-l-2 border-accent-faint pl-5 mt-3">
        <p className="text-briefing-text font-serif text-lg leading-relaxed">
          {briefing.brief}
        </p>
      </div>
      <hr className="mt-6" />
    </section>
  );
}
