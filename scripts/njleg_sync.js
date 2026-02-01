#!/usr/bin/env node
import fs from "fs";
import path from "path";
import https from "https";
import crypto from "crypto";

const ROOT = process.cwd();
const OUT_DIR = process.env.NJLEG_OUT_DIR
  ? path.resolve(process.env.NJLEG_OUT_DIR)
  : path.resolve(ROOT, "data/njleg");

const YEAR = Number(process.env.NJLEG_YEAR || 2026);
const SESSION_DIR = `${YEAR}data/`;

const EN_JSON_URL =
  process.env.NJLEG_EN_JSON_URL ||
  "https://www.njleg.state.nj.us/_next/data/pqIK6zGXPzeLeust63g-E/en.json";

const BASE_URL = "https://pub.njleg.state.nj.us/leg-databases/";

function ensureDir(p) {
  fs.mkdirSync(p, { recursive: true });
}

function download(url, outPath) {
  return new Promise((resolve, reject) => {
    https.get(url, (res) => {
      if (res.statusCode !== 200) {
        reject(new Error(`HTTP ${res.statusCode} for ${url}`));
        return;
      }
      const file = fs.createWriteStream(outPath);
      res.pipe(file);
      file.on("finish", () => file.close(resolve));
    }).on("error", reject);
  });
}

async function main() {
  ensureDir(OUT_DIR);
  const yearDir = path.join(OUT_DIR, "downloads", String(YEAR));
  ensureDir(yearDir);

  console.log(`Downloading NJ Legislature data for ${YEAR}`);

  // Bill tracking ZIPs
  const files = ["DB" + YEAR + ".zip", "DB" + YEAR + "_TEXT.zip", "Readme.txt"];

  for (const f of files) {
    const url = BASE_URL + SESSION_DIR + f;
    const out = path.join(yearDir, f);
    try {
      await download(url, out);
      console.log(`✔ ${f}`);
    } catch {
      console.log(`⚠ Skipped ${f}`);
    }
  }

  // en.json
  const enOut = path.join(OUT_DIR, "njleg-site", "en.json");
  ensureDir(path.dirname(enOut));
  await download(EN_JSON_URL, enOut);
  console.log("✔ en.json");

  console.log("Stage 1 complete.");
}

main().catch((e) => {
  console.error(e);
  process.exit(1);
});
