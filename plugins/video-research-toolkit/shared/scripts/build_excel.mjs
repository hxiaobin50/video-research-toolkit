import fs from "node:fs/promises";
import { createRequire } from "node:module";
import os from "node:os";
import path from "node:path";
import process from "node:process";

const require = createRequire(import.meta.url);
let artifactTool;
try {
  artifactTool = require("@oai/artifact-tool");
} catch {
  const bundledPath = path.join(
    os.homedir(),
    ".cache",
    "codex-runtimes",
    "codex-primary-runtime",
    "dependencies",
    "node",
    "node_modules",
    "@oai",
    "artifact-tool",
  );
  artifactTool = require(bundledPath);
}
const { FileBlob, SpreadsheetFile } = artifactTool;

function parseArgs(argv) {
  const result = {};
  for (let index = 0; index < argv.length; index += 2) {
    const key = argv[index];
    const value = argv[index + 1];
    if (!key?.startsWith("--") || value === undefined) {
      throw new Error("Use --template path --data path --output path.");
    }
    result[key.slice(2)] = value;
  }
  return result;
}

const args = parseArgs(process.argv.slice(2));
if (!args.template || !args.data || !args.output) {
  throw new Error("Missing --template, --data, or --output.");
}

const payload = JSON.parse(await fs.readFile(args.data, "utf8"));
const workbook = await SpreadsheetFile.importXlsx(await FileBlob.load(args.template));

for (const [sheetName, config] of Object.entries(payload.sheets ?? {})) {
  const sheet = workbook.worksheets.getItem(sheetName);
  const headerRow = Number(config.headerRow ?? 2);
  const usedRange = sheet.getUsedRange(true);
  if (!usedRange) continue;
  const values = usedRange.values;
  const headers = values[headerRow - 1] ?? [];
  const rows = config.rows ?? [];
  if (!rows.length) continue;
  const matrix = rows.map((row) =>
    headers.map((header) => {
      const slashHeader = typeof header === "string" ? header.replace(/\n/g, " / ") : header;
      const englishHeader = typeof header === "string" ? header.split("\n").at(-1) : header;
      return row[header] ?? row[slashHeader] ?? row[englishHeader] ?? null;
    }),
  );
  sheet.getRangeByIndexes(headerRow, 0, matrix.length, headers.length).values = matrix;
}

workbook.recalculate();
await fs.mkdir(path.dirname(path.resolve(args.output)), { recursive: true });
const output = await SpreadsheetFile.exportXlsx(workbook);
const outputPath = path.resolve(args.output);
await output.save(outputPath);
await fs.rm(`${outputPath}.inspect.ndjson`, { force: true });
console.log(JSON.stringify({ status: "ok", output: outputPath }, null, 2));
