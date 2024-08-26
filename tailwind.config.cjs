/** @type {import('tailwindcss').Config}*/
const config = {
  content: [
    "./frontend/src/**/*.{html,js,svelte,ts}",
    "./node_modules/flowbite-svelte-icons/**/*.{html,js,svelte,ts}",
    "./node_modules/flowbite-svelte/**/*.{html,js,svelte,ts}",
  ],
  plugins: [require("flowbite/plugin")],
  darkMode: "class",
  theme: {
    extend: {
      gridTemplateColumns: {
        sidebar: "max(250px, 0.2vw) 1fr",
      },
      colors: {
        primary: {
          50: "#f0f9ff",
          100: "#e0f2fe",
          200: "#bae6fd",
          300: "#7dd3fc",
          400: "#38bdf8",
          500: "#0ea5e9",
          600: "#0284c7",
          700: "#0369a1",
          800: "#075985",
          900: "#0c4a6e",
        },
      },
      borderRadius: {
        none: "0",
        sm: "0",
        DEFAULT: "0",
        md: "0",
        lg: "0",
        large: "0",
        "2xl": "0",
        full: "9999px",
      },
    },
  },
};

module.exports = config;
