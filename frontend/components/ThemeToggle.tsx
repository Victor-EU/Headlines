"use client";

import { useEffect, useState } from "react";

type Theme = "light" | "dark" | "system";

export function ThemeToggle() {
  const [theme, setTheme] = useState<Theme>("system");

  useEffect(() => {
    const saved = localStorage.getItem("theme") as Theme | null;
    if (saved) setTheme(saved);
  }, []);

  function applyTheme(newTheme: Theme) {
    setTheme(newTheme);

    if (newTheme === "system") {
      localStorage.removeItem("theme");
      document.documentElement.removeAttribute("data-theme");
    } else {
      localStorage.setItem("theme", newTheme);
      document.documentElement.setAttribute("data-theme", newTheme);
    }
  }

  function cycle() {
    const next: Theme =
      theme === "system" ? "dark" : theme === "dark" ? "light" : "system";
    applyTheme(next);
  }

  const label =
    theme === "dark" ? "Dark" : theme === "light" ? "Light" : "Auto";

  return (
    <button
      onClick={cycle}
      className="text-meta text-muted hover:text-accent transition-colors font-sans"
      aria-label={`Theme: ${label}`}
    >
      {label}
    </button>
  );
}
