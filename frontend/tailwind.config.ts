import type { Config } from "tailwindcss";

const config: Config = {
  darkMode: ["class"],
  content: ["./app/**/*.{ts,tsx}", "./components/**/*.{ts,tsx}", "./lib/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        iris: {
          DEFAULT: "#6C5CE7",
          light: "#8C7CFF",
          dim: "#453B99",
        },
        aqua: {
          DEFAULT: "#22D3EE",
          light: "#38E1FF",
          dim: "#0E7A8C",
        },
        ink: "#161A33",
        mist: "#F4F7FF",
        void: "#0A0B16",
        nebula: "#12142B",
      },
      fontFamily: {
        display: ["var(--font-display)"],
        body: ["var(--font-body)"],
        mono: ["var(--font-mono)"],
      },
      backdropBlur: {
        xs: "2px",
        glass: "20px",
      },
      boxShadow: {
        glass: "0 8px 32px 0 rgba(20, 20, 50, 0.12)",
        "glass-lg": "0 20px 60px -10px rgba(20, 20, 50, 0.25)",
        "glow-iris": "0 0 40px -4px rgba(140, 124, 255, 0.55)",
        "glow-aqua": "0 0 40px -4px rgba(56, 225, 255, 0.4)",
      },
      borderRadius: {
        glass: "1.25rem",
      },
      animation: {
        drift: "drift 22s ease-in-out infinite",
        "drift-slow": "drift 34s ease-in-out infinite reverse",
        "pulse-glow": "pulse-glow 4s ease-in-out infinite",
      },
      keyframes: {
        drift: {
          "0%, 100%": { transform: "translate(0, 0) scale(1)" },
          "33%": { transform: "translate(4%, 6%) scale(1.08)" },
          "66%": { transform: "translate(-5%, 3%) scale(0.96)" },
        },
        "pulse-glow": {
          "0%, 100%": { opacity: "0.55" },
          "50%": { opacity: "0.9" },
        },
      },
    },
  },
  plugins: [],
};

export default config;
