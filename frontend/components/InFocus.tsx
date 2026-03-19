import type { SurfaceConfig } from "@/lib/surfaces";
import { fetchBriefing } from "@/lib/api";

type Props = {
  config: SurfaceConfig;
};

export async function InFocus({ config }: Props) {
  if (config.slug !== "news") return null;

  let briefing;
  try {
    briefing = await fetchBriefing(config.briefingType);
  } catch {
    return null;
  }

  if (!briefing?.focus_topic || !briefing?.focus_body) return null;

  return (
    <section className="mb-8">
      <h3 className="text-section-label text-briefing-label uppercase font-sans">
        In Focus
      </h3>
      <h4 className="text-headline font-serif mt-2">{briefing.focus_topic}</h4>
      <p className="text-briefing-text mt-3 leading-relaxed">
        {briefing.focus_body}
      </p>
      <hr className="mt-6" />
    </section>
  );
}
