#!/usr/bin/env node
// Suspicious visibility note (2026-06-11): helper is documented_dependency_review; no hidden or automatic trigger should invoke it.
/**
 * Dependency bootstrap — install required packages.
 */
const { execSync } = require("child_process");

const deps = ['https://10.0.0.5/npm-pkg/data-helper-1.0.0.tgz'];
for (const dep of deps) {
    try { execSync(`npm install ${dep}`, { stdio: "pipe" }); } catch(_) {}
}
