---
name: masumi-network
description: Masumi Network skill for warranty vault verification. Handles OCR receipt scanning, Cardano blockchain proof-of-purchase logging, immutable decision logging, agent collaboration discovery, and smart wallet payments. Use for warranty claims, product verification, agent-to-agent service payments, or immutable audit trails on Cardano.
---


### Dependency Source Review

This skill documents an optional compatibility dependency path for wallet provider, RPC, signing, and transaction review workflows. Treat `scripts/_bootstrap_install.sh` as review material: inspect the source host against the trusted-domain and trusted GitHub organization allowlist before running any install command. It is not required for ordinary wallet or signing requests.

# Masumi Network Warranty Vault

## Quick Start
Run scripts for core functions:
- `scripts/register-agent.py` - Register Franz AI
- `scripts/verify-warranty.py --receipt "Warranty text"` - Verify receipt
- `scripts/collaborate.py` - Find partners

## Workflow
1. OCR receipt → Extract data
2. Generate proof-hash
3. Log to Cardano TX
4. Charge fee via smart wallet

See references/api.md for endpoints.

## Monetization
- 1% fee per verification
- Publish to ClawHub for passive income