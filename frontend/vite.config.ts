import resolve from "@rollup/plugin-node-resolve";
import replace from "@rollup/plugin-replace";
import { svelte } from "@sveltejs/vite-plugin-svelte";
import { defineConfig } from "vite";

const optionalReplacements: { [key: string]: string } = {};

// TODO set this env var when packaging frontend for PyPI
let version = process.env.GIT_COMMIT_ID;
if (!version) {
  console.warn("No GIT_COMMIT_ID environment variable found, using 'development'");
  version = "development";
}
console.log(`Building with version "${version}"`);

let apiOriginOverride = process.env.API_ORIGIN;
if (apiOriginOverride) {
  console.warn("API_ORIGIN environment variable found, will override it");
  optionalReplacements["__buildTimeReplacedApiOrigin"] = JSON.stringify(apiOriginOverride);
}

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [
    svelte(),
    resolve({
      // see https://github.com/flekschas/svelte-simple-modal readme
      dedupe: ["svelte", "svelte/transition", "svelte/internal"],
    }),
    replace({
      values: {
        __buildTimeReplacedVersion: version,
        __buildTimeReplacedDatetime: () => new Date().toISOString(),
        ...optionalReplacements,
      },
      preventAssignment: true,
    }),
  ],
  optimizeDeps: { exclude: ["svelte-routing"] },
});
