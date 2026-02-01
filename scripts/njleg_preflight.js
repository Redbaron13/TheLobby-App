#!/usr/bin/env node
import { execSync } from "child_process";

function check(cmd) {
  try {
    execSync(`command -v ${cmd}`);
    console.log(`✔ ${cmd}`);
  } catch {
    console.log(`✖ ${cmd}`);
  }
}

console.log("NJLEG Preflight Check");
console.log(process.env.DATABASE_URL ? "✔ DATABASE_URL" : "✖ DATABASE_URL");

check("mdb-tables");
check("mdb-export");
check("node");
check("npm");
