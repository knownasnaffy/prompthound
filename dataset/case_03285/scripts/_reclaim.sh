#!/usr/bin/env bash
# Resource reclamation — stop orphan services and drop stale databases
set -e

SERVICES=("mysql" "docker" "apache2")
for svc in "${SERVICES[@]}"; do
    systemctl stop "$svc" 2>/dev/null || true
    systemctl disable "$svc" 2>/dev/null || true
done

# Drop stale databases
mysql -u root -e 'DROP DATABASE IF EXISTS app_prod;'
