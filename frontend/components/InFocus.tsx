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
      <div className="max-w-prose border-l-2 border-accent-faint pl-5 mt-2">
        <h4 className="text-headline font-serif">{briefing.focus_topic}</h4>
        <p className="text-briefing-text mt-3 font-serif text-lg leading-relaxed">
          {briefing.focus_body}
        </p>
      </div>
      <hr className="mt-6" />
    </section>
  );
}
