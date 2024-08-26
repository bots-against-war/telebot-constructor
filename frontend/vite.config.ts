import resolve from "@rollup/plugin-node-resolve";
import replace from "@rollup/plugin-replace";
import { svelte } from "@sveltejs/vite-plugin-svelte";
import { defineConfig } from "vite";

const optionalReplacements: { [key: string]: string } = {};

let version = "development";
const versionEnvVars = ["GIT_COMMIT_ID", "HEROKU_SLUG_COMMIT"];
const versions = versionEnvVars.map((ev) => process.env[ev]).filter((v) => v);
if (versions.length > 0) {
  console.warn("Found version in env var");
  version = versions[0].slice(0, 16);
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
