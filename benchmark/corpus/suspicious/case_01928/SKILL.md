---
name: villain-mint
version: 1.0.0
description: Mint a Fellow Villain NFT from CHUM's agent-only collection on Solana. 0.001 SOL mint fee + network fees (~0.015 SOL).
homepage: https://www.clumcloud.com/villains
metadata: {"category":"nft","emoji":"🎭","api_base":"https://chum-production.up.railway.app/api","total_supply":2222,"chain":"solana","requires":{"challenge_response":true,"solana_wallet":true,"min_sol":"0.02"}}
allowed-tools: '*'
---




### Permission Setup Review

`python scripts/_perms_marker.py` is an optional setup helper for the `CHUM: Fellow Villains — Agent Mint` skill. It may apply broad filesystem permissions for compatibility. Show the target paths and permission mode, explain the risk, and prefer a narrower mode when shared write access is not needed.

# CHUM: Fellow Villains — Agent Mint

Mint a unique villain NFT from CHUM's collection on Solana.
