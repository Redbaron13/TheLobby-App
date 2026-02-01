#!/usr/bin/env node
/* eslint-disable no-console */

import fs from "fs";
import path from "path";

const ROOT = process.cwd();
const DATA_ROOT = process.env.NJLEG_OUT_DIR
  ? path.resolve(process.env.NJLEG_OUT_DIR)
  : path.resolve(ROOT, "data/njleg");

const STATE_PATH = path.join(DATA_ROOT, "pipeline_state.json");
const OUT_TXT = path.join(DATA_ROOT, "pipeline_summary.txt");

function padRight(s, n) {
  s = String(s ?? "");
  return s.length >= n ? s.slice(0, n) : s + " ".repeat(n - s.length);
}

function main() {
  if (!fs.existsSync(STATE_PATH)) {
    console.error(`No pipeline state found at: ${STATE_PATH}`);
    process.exit(1);
  }

  const state = JSON.parse(fs.readFileSync(STATE_PATH, "utf8"));
  const years = Object.keys(state.years || {})
    .map((y) => Number(y))
    .sort((a, b) => b - a);

  const lines = [];
  lines.push(`NJLEG PIPELINE SUMMARY`);
  lines.push(`Generated: ${new Date().toISOString()}`);
  lines.push(`Status: ${state.status || "unknown"}`);
  lines.push(`Range: ${state.config?.start ?? "?"} -> ${state.config?.stop ?? "?"}`);
  lines.push("");

  const header =
    padRight("YEAR", 6) +
    padRight("STATUS", 12) +
    padRight("ATTEMPTS", 10) +
    padRight("ELAPSED(s)", 12) +
    padRight("LAST STAGE", 18) +
    "LAST ERROR";
  lines.push(header);
  lines.push("-".repeat(header.length));

  for (const y of years) {
    const ys = state.years[String(y)] || {};
    const stages = ys.stages || {};
    const lastStage =
      Object.entries(stages)
        .sort((a, b) => {
          const at = a[1]?.finishedAt || a[1]?.startedAt || "";
          const bt = b[1]?.finishedAt || b[1]?.startedAt || "";
          return at < bt ? 1 : at > bt ? -1 : 0;
        })[0]?.[0] || state.lastStage || "";

    const row =
      padRight(y, 6) +
      padRight(ys.status || "", 12) +
      padRight(ys.attempts || 0, 10) +
      padRight(ys.elapsedSeconds || "", 12) +
      padRight(lastStage, 18) +
      (ys.lastError || "");
    lines.push(row);
  }

  const out = lines.join("\n");
  console.log(out);

  fs.writeFileSync(OUT_TXT, out);
  console.log(`\nWrote: ${OUT_TXT}`);
}

main();
