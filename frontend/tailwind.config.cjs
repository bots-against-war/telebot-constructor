/** @type {import('tailwindcss').Config}*/
const config = {
  content: [
    "./src/**/*.{html,js,svelte,ts}",
    "../node_modules/flowbite-svelte-icons/**/*.{html,js,svelte,ts}",
    "../node_modules/flowbite-svelte/**/*.{html,js,svelte,ts}",
  ],
  plugins: [require("flowbite/plugin")],
  darkMode: "class",
  theme: {
    extend: {
      colors: {
        // zinc
        primary: {
          50: "#fafafa",
          100: "#f4f4f5",
          200: "#e4e4e7",
          300: "#d4d4d8",
          400: "#a1a1aa",
          500: "#71717a",
          600: "#52525b",
          700: "#3f3f46",
          800: "#27272a",
          900: "#18181b",
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
