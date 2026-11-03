// Spread into `theme.extend` of the frontend tailwind.config.ts.
// Values mirror docs/design/tokens.css.
export const upsKulkaTheme = {
  colors: {
    accent: { DEFAULT: "#e6b3b3", dark: "#d99999", soft: "#f5dede" },
    rose: { DEFAULT: "#c06f6f", deep: "#8a4f4f" },
    ink: "#111111",
    muted: "#6f6f6f",
    line: "#eadada",
    surface: "#fff8f8",
  },
  fontFamily: {
    display: ["var(--font-comfortaa)", "Manrope", "system-ui", "sans-serif"],
    body: ["var(--font-manrope)", "system-ui", "sans-serif"],
  },
  borderRadius: { photo: "22px", panel: "28px" },
  boxShadow: { pop: "0 18px 40px -18px rgba(138, 79, 79, 0.45)" },
} as const;
