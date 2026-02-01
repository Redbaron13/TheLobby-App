#!/usr/bin/env node
import fs from "fs";
import path from "path";
import { execSync } from "child_process";

const ROOT = process.cwd();
const YEAR = Number(process.env.NJLEG_YEAR || 2026);

const BASE = path.resolve(ROOT, "data/njleg/stage2", String(YEAR));
const EXTRACTED = path.join(BASE, "extracted");
const EXPORT_CSV = path.join(BASE, "exports/csv");
const EXPORT_JSON = path.join(BASE, "exports/json");

function ensureDir(p) {
  fs.mkdirSync(p, { recursive: true });
}

function csvToJson(csvPath, jsonPath) {
  const lines = fs.readFileSync(csvPath, "utf8").split("\n").filter(Boolean);
  const headers = lines.shift().split(",");
  const rows = lines.map((l) => {
    const vals = l.split(",");
    const obj = {};
    headers.forEach((h, i) => (obj[h] = vals[i]));
    return obj;
  });
  fs.writeFileSync(jsonPath, JSON.stringify(rows, null, 2));
  return rows.length;
}

async function main() {
  ensureDir(EXPORT_CSV);
  ensureDir(EXPORT_JSON);

  const manifests = [];

  for (const dir of fs.readdirSync(EXTRACTED)) {
    const mdb = path.join(EXTRACTED, dir, `${dir}.mdb`);
    if (!fs.existsSync(mdb)) continue;

    const tables = execSync(`mdb-tables ${mdb}`).toString().trim().split(" ");
    for (const t of tables) {
      const csv = path.join(EXPORT_CSV, `${dir}_${t}.csv`);
      execSync(`mdb-export ${mdb} ${t} > "${csv}"`);
      const json = path.join(EXPORT_JSON, `${dir}_${t}.json`);
      const records = csvToJson(csv, json);
      manifests.push({ table: t, json: path.relative(BASE, json), records });
    }
  }

  fs.writeFileSync(
    path.join(BASE, "stage2_exports_manifest.json"),
    JSON.stringify({ year: YEAR, json: manifests }, null, 2)
  );

  console.log(`Stage2 export complete for ${YEAR}`);
}

main().catch((e) => {
  console.error(e);
  process.exit(1);
});
