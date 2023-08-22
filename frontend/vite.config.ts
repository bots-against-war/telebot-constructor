import { defineConfig } from "vite";
import { svelte } from "@sveltejs/vite-plugin-svelte";
import replace from "@rollup/plugin-replace";

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
    replace({
      values: {
        __buildTimeReplacedVersion: JSON.stringify(version),
        __buildTimeReplacedDatetime: () => JSON.stringify(new Date()),
        ...optionalReplacements,
      },
      preventAssignment: true,
    }),
  ],
});
