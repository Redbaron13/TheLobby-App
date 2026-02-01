#!/usr/bin/env node
import fs from "fs";
import path from "path";

const ROOT = process.cwd();
const YEAR = Number(process.env.NJLEG_YEAR || 2026);
const BASE = path.resolve(ROOT, "data/njleg/stage2", String(YEAR));

const files = [
  "stage2_manifest.json",
  "stage2_exports_manifest.json",
];

for (const f of files) {
  const p = path.join(BASE, f);
  if (!fs.existsSync(p)) {
    console.error(`Missing ${f}`);
    process.exit(1);
  }
}

console.log(`Validation OK for ${YEAR}`);
