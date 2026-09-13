import type { Config } from "tailwindcss";

const config: Config = {
  content: ["./app/**/*.{ts,tsx}", "./components/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        canvas: "#0F1115",
        surface: "#161923",
        surfaceRaised: "#1D2130",
        border: "#2A2F40",
        borderLight: "#353B4F",
        accent: "#5B8DEF",
        accentSoft: "#5B8DEF1A",
        success: "#3FBE7A",
        warning: "#E8A33D",
        danger: "#E5566D",
        muted: "#8A8FA3",
        ink: "#E7E9F0",
      },
      fontFamily: {
        sans: ["var(--font-sans)", "system-ui", "sans-serif"],
        mono: ["var(--font-mono)", "monospace"],
      },
      borderRadius: {
        xl: "14px",
        "2xl": "20px",
      },
      boxShadow: {
        card: "0 1px 0 rgba(255,255,255,0.03) inset, 0 8px 24px rgba(0,0,0,0.28)",
      },
    },
  },
  plugins: [],
};
export default config;
