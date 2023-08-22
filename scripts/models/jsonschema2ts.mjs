import { compileFromFile } from "json-schema-to-typescript";
import { parseArgs } from "node:util";
import { readFileSync, writeFileSync } from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

const SCRIPT_DIR = path.dirname(fileURLToPath(import.meta.url));
const PROJECT_ROOT = path.resolve(SCRIPT_DIR, "../..");
const OUTPUT_FILE = path.resolve(PROJECT_ROOT, "frontend/src/api/types.d.ts");

const parseArgsResult = parseArgs({
  options: {
    check: {
      type: "boolean",
      default: false,
    },
    input: {
      type: "string",
      default: path.resolve(PROJECT_ROOT, "data/schema.json"),
    },
  },
});

const args = parseArgsResult.values;

if (!args.check)
  compileFromFile(args.input).then((typescriptDef) =>
    writeFileSync(OUTPUT_FILE, typescriptDef),
  );
else {
  compileFromFile(args.input).then((typescriptDef) => {
    const existingTypescriptDef = readFileSync(OUTPUT_FILE).toString("utf-8");
    if (typescriptDef != existingTypescriptDef) {
      console.error(
        "Existing Typescript type definition is out-of-date and needs to be regenerated",
      );
      process.exit(1);
    } else console.log("OK");
  });
}
