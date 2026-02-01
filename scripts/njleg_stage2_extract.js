#!/usr/bin/env node
import fs from "fs";
import path from "path";
import unzipper from "unzipper";
import crypto from "crypto";

const ROOT = process.cwd();
const YEAR = Number(process.env.NJLEG_YEAR || 2026);

const DATA_ROOT = path.resolve(ROOT, "data/njleg");
const IN_DIR = path.join(DATA_ROOT, "downloads", String(YEAR));
const OUT_DIR = path.join(DATA_ROOT, "stage2", String(YEAR), "extracted");

function ensureDir(p) {
  fs.mkdirSync(p, { recursive: true });
}

function sha256(fp) {
  return crypto.createHash("sha256").update(fs.readFileSync(fp)).digest("hex");
}

async function extractZip(zipPath, outDir) {
  await fs
    .createReadStream(zipPath)
    .pipe(unzipper.Extract({ path: outDir }))
    .promise();
}

async function main() {
  ensureDir(OUT_DIR);

  const inventory = [];

  for (const f of fs.readdirSync(IN_DIR)) {
    if (!f.endsWith(".zip")) continue;
    const full = path.join(IN_DIR, f);
    const dest = path.join(OUT_DIR, f.replace(".zip", ""));
    ensureDir(dest);
    await extractZip(full, dest);
    inventory.push({ file: f, sha256: sha256(full) });
  }

  const manifest = {
    year: YEAR,
    createdAt: new Date().toISOString(),
    outputs: { inventory },
  };

  const mPath = path.join(DATA_ROOT, "stage2", String(YEAR), "stage2_manifest.json");
  fs.writeFileSync(mPath, JSON.stringify(manifest, null, 2));

  console.log(`Stage2 extract complete for ${YEAR}`);
}

main().catch((e) => {
  console.error(e);
  process.exit(1);
});
