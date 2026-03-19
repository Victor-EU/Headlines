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
      <p className="text-briefing-text mt-2 leading-relaxed">{briefing.brief}</p>
      <hr className="mt-6" />
    </section>
  );
}
