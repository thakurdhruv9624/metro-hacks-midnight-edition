/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        canvas: "#FAFAFA",
        ink: "#1D1D1F",
        mute: "#6E6E73",
        accent: "#0071E3",
        line: "#E8E8ED",
      },
      fontFamily: {
        sans: [
          "-apple-system",
          "BlinkMacSystemFont",
          "SF Pro Text",
          "SF Pro Display",
          "Inter",
          "Segoe UI",
          "sans-serif",
        ],
      },
      boxShadow: {
        card: "0 8px 30px rgba(0, 0, 0, 0.04)",
      },
      borderRadius: {
        card: "18px",
      },
    },
  },
  plugins: [],
};
