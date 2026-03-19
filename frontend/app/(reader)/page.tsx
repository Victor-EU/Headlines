import { SURFACES } from "@/lib/surfaces";
import { SurfaceNav } from "@/components/SurfaceNav";
import { SurfacePage } from "@/components/SurfacePage";

export default async function NewsPage() {
  return (
    <>
      <SurfaceNav activeSurface="news" />
      <SurfacePage config={SURFACES.news} />
    </>
  );
}
