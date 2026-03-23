import { SURFACES } from "@/lib/surfaces";
import { SurfaceNav } from "@/components/SurfaceNav";
import { SurfacePage } from "@/components/SurfacePage";

export const dynamic = "force-dynamic";

export default async function LearningPage() {
  return (
    <>
      <SurfaceNav activeSurface="learning" />
      <SurfacePage config={SURFACES.learning} />
    </>
  );
}
