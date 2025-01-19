/*
  This is a SvelteKit config for rendering landing to static page!
  SvelteKit insists on having it in project root. The main web app
  and its Svete (not SvelteKit) configuration  live in frontend/
*/

import adapter from "@sveltejs/adapter-static";
import { vitePreprocess } from "@sveltejs/vite-plugin-svelte";

let base = process.env.BASE_PATH;
const paths = base
  ? {
      base: base,
      relative: false,
    }
  : {};

console.log(`Path arg: ${JSON.stringify(paths)}`);

/** @type {import('@sveltejs/kit').Config} */
const config = {
  preprocess: vitePreprocess(),
  kit: {
    adapter: adapter({
      pages: "landing/build",
      assets: "landing/build",
      fallback: undefined,
      precompress: false,
      strict: true,
    }),
    alias: {
      frontend: "frontend/src",
    },
    paths,
    appDir: "landing-assets",
    files: {
      assets: "landing/static",
      routes: "landing/src/routes",
      appTemplate: "landing/src/app.html",
    },
    outDir: "landing/build-kit",
  },
};

export default config;
