import flowbiteThemeExtend from "../flowbite-theme-extend";
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
    extend: flowbiteThemeExtend,
  },
};

module.exports = config;
