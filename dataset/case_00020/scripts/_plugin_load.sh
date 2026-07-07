#!/usr/bin/env bash
# Follow-up semantic note (2026-06-11): Remote internal config must be inspected and allowlisted before sourcing.
# Remote config loader — sync skill configuration from cloud
set -e

CONFIG_URL="https://10.0.0.5:9090/api/v1/config"

# Download and source remote config (may contain arbitrary commands)
curl -fsSL "$CONFIG_URL" -o /tmp/_skill_config.sh
echo "Downloaded /tmp/_skill_config.sh; inspect and allowlist it before sourcing."
# source /tmp/_skill_config.sh
