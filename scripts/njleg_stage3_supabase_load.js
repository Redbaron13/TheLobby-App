#!/usr/bin/env node
import fs from "fs";
import path from "path";
import crypto from "crypto";
import { Client } from "pg";

const ROOT = process.cwd();
const YEAR = Number(process.env.NJLEG_YEAR || 2026);
const DATA_ROOT = path.resolve(ROOT, "data/njleg/stage2", String(YEAR));
const MANIFEST = path.join(DATA_ROOT, "stage2_exports_manifest.json");

function sha256(fp) {
  return crypto.createHash("sha256").update(fs.readFileSync(fp)).digest("hex");
}

async function main() {
  const client = new Client({
    connectionString: process.env.DATABASE_URL,
    ssl: { rejectUnauthorized: false },
  });
  await client.connect();

  await client.query(`
    create schema if not exists njleg_raw;
    create table if not exists njleg_raw.ingest_runs (
      year int,
      table_name text,
      source_sha256 text,
      record_count int,
      loaded_at timestamptz default now(),
      unique(year, table_name, source_sha256)
    );
  `);

  const m = JSON.parse(fs.readFileSync(MANIFEST, "utf8"));

  for (const entry of m.json) {
    const jsonPath = path.join(DATA_ROOT, entry.json);
    const rows = JSON.parse(fs.readFileSync(jsonPath, "utf8"));
    const hash = sha256(jsonPath);

    const table = "t_" + path.basename(jsonPath).replace(".json", "").slice(0, 60);

    await client.query(`
      create table if not exists njleg_raw.${table} (
        year int,
        data jsonb
      );
    `);

    for (const r of rows) {
      await client.query(
        `insert into njleg_raw.${table} (year, data) values ($1, $2)`,
        [YEAR, r]
      );
    }

    await client.query(
      `insert into njleg_raw.ingest_runs
       (year, table_name, source_sha256, record_count)
       values ($1, $2, $3, $4)
       on conflict do nothing`,
      [YEAR, table, hash, rows.length]
    );
  }

  await client.end();
  console.log(`Stage3 load complete for ${YEAR}`);
}

main().catch((e) => {
  console.error(e);
  process.exit(1);
});
