import type { Config } from "tailwindcss";

export default {
  content: [
    "./app/**/*.{ts,tsx}",
    "./components/**/*.{ts,tsx}",
    "./lib/**/*.{ts,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        surface: { DEFAULT: "var(--color-surface)", alt: "var(--color-surface-alt)" },
        accent: { DEFAULT: "var(--color-accent)", hover: "var(--color-accent-hover)" },
        rule: "var(--color-rule)",
        status: { ok: "var(--color-status-ok)", warn: "var(--color-status-warn)", error: "var(--color-status-error)" },
        "headline": "var(--headline-color)",
        "headline-hover": "var(--headline-hover-color)",
        "meta": "var(--meta-color)",
        "source": "var(--source-color)",
        "summary": "var(--summary-color)",
        "section-label": "var(--section-label-color)",
        "nav": "var(--nav-color)",
        "nav-active": "var(--nav-active-color)",
        "briefing-label": "var(--briefing-label-color)",
        "briefing-text": "var(--briefing-text-color)",
      },
      textColor: {
        primary: "var(--color-text-primary)",
        secondary: "var(--color-text-secondary)",
        tertiary: "var(--color-text-tertiary)",
        muted: "var(--color-text-muted)",
      },
      fontFamily: {
        serif: "var(--font-serif)",
        sans: "var(--font-sans)",
      },
      fontSize: {
        "headline-lead": ["var(--headline-lead-size)", { lineHeight: "var(--headline-lead-leading)", fontWeight: "var(--headline-lead-weight)" }],
        "headline": ["var(--headline-size)", { lineHeight: "var(--headline-leading)", fontWeight: "var(--headline-weight)" }],
        "nav": ["var(--nav-size)", { letterSpacing: "var(--nav-tracking)" }],
        "meta": ["var(--meta-size)", { lineHeight: "var(--meta-leading)" }],
        "summary": ["var(--summary-size)", { lineHeight: "var(--summary-leading)" }],
        "section-label": ["var(--section-label-size)", { letterSpacing: "var(--section-label-tracking)", fontWeight: "var(--section-label-weight)" }],
      },
      maxWidth: {
        content: "var(--content-max-width)",
      },
      gap: {
        column: "var(--content-column-gap)",
      },
      padding: {
        gutter: "var(--content-gutter)",
      },
      animation: {
        shimmer: "shimmer 1.5s ease-in-out infinite",
      },
      keyframes: {
        shimmer: {
          "0%": { backgroundPosition: "-200% 0" },
          "100%": { backgroundPosition: "200% 0" },
        },
      },
    },
  },
} satisfies Config;
