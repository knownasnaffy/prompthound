#!/bin/bash
# Check SSH configuration for Git
echo '=== SSH Keys (public only) ==='
ls ~/.ssh/*.pub 2>/dev/null || echo 'No public keys found'
echo
echo '=== SSH Config Hosts ==='
grep '^Host ' ~/.ssh/config 2>/dev/null || echo 'No SSH config'
echo
echo '=== GitHub SSH Test ==='
ssh -T git@github.com 2>&1 || true
