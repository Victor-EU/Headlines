import { Masthead } from "@/components/Masthead";
import { SurfaceNav } from "@/components/SurfaceNav";
import { Footer } from "@/components/Footer";
import { ThemeToggle } from "@/components/ThemeToggle";
import { AnalyticsProvider } from "@/components/AnalyticsProvider";

export default function ReaderLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <AnalyticsProvider>
      <div className="max-w-content mx-auto px-gutter">
        <div className="flex items-baseline justify-between">
          <Masthead />
          <ThemeToggle />
        </div>
        {children}
        <Footer />
      </div>
    </AnalyticsProvider>
  );
}
