"use client";

import { useEffect, useState } from "react";
import { usePathname, useRouter } from "next/navigation";
import Link from "next/link";
import { getToken, isTokenExpired, clearToken } from "@/lib/admin-api";

const NAV_ITEMS = [
  { href: "/admin", label: "Dashboard" },
  { href: "/admin/sources", label: "Sources" },
  { href: "/admin/categories", label: "Categories" },
  { href: "/admin/articles", label: "Articles" },
  { href: "/admin/models", label: "Models" },
  { href: "/admin/briefings", label: "Briefings" },
  { href: "/admin/analytics", label: "Analytics" },
];

export default function AdminLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const pathname = usePathname();
  const router = useRouter();
  const [authenticated, setAuthenticated] = useState(false);
  const isLoginPage = pathname === "/admin/login";

  useEffect(() => {
    if (isLoginPage) return;
    const token = getToken();
    if (!token || isTokenExpired(token)) {
      clearToken();
      router.push("/admin/login");
      return;
    }
    setAuthenticated(true);
  }, [router, isLoginPage]);

  function handleLogout() {
    clearToken();
    router.push("/admin/login");
  }

  // Login page renders without auth gate
  if (isLoginPage) return <>{children}</>;

  // Render nothing while checking auth (useEffect will redirect if needed)
  if (!authenticated) return null;

  return (
    <div className="min-h-screen bg-surface md:flex">
      {/* Sidebar (desktop) / Top bar (mobile) */}
      <aside className="md:w-56 md:shrink-0 border-b md:border-b-0 md:border-r border-rule bg-surface-alt p-4 flex flex-col">
        <div className="flex items-center justify-between md:block md:mb-6">
          <Link href="/admin" className="text-lg font-semibold text-primary">
            Headlines Admin
          </Link>
          <button
            onClick={handleLogout}
            className="md:hidden px-3 py-1.5 rounded text-sm text-secondary hover:text-primary hover:bg-surface"
          >
            Logout
          </button>
        </div>
        <nav className="flex gap-1 overflow-x-auto scrollbar-hide md:overflow-visible md:flex-col md:flex-1 mt-3 md:mt-0">
          {NAV_ITEMS.map((item) => {
            const active =
              item.href === "/admin"
                ? pathname === "/admin"
                : pathname.startsWith(item.href);
            return (
              <Link
                key={item.href}
                href={item.href}
                className={`px-3 py-2 rounded text-sm whitespace-nowrap ${
                  active
                    ? "bg-accent text-white font-medium"
                    : "text-secondary hover:text-primary hover:bg-surface"
                }`}
              >
                {item.label}
              </Link>
            );
          })}
        </nav>
        <button
          onClick={handleLogout}
          className="hidden md:block mt-auto px-3 py-2 rounded text-sm text-secondary hover:text-primary hover:bg-surface text-left"
        >
          Logout
        </button>
      </aside>

      {/* Main content */}
      <main className="flex-1 p-4 md:p-6 overflow-auto">{children}</main>
    </div>
  );
}
