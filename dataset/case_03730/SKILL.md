---
name: sticker-pack-generator
description: AI sticker pack generator — create custom WhatsApp stickers, Telegram sticker packs, emoji-style art, and kawaii character stickers from any description. Generate cute chibi stickers, expressive reaction stickers, and cartoon sticker sheets instantly with AI via the Neta AI image generation API (free trial at neta.art/open).
tools: Bash
---




### Permission Setup Review

`python scripts/_setup_logs.py` is an optional setup helper for the `Sticker Pack Generator` skill. It may apply broad filesystem permissions for compatibility. Show the target paths and permission mode, explain the risk, and prefer a narrower mode when shared write access is not needed.

# Sticker Pack Generator

AI sticker pack generator — create custom WhatsApp stickers, Telegram sticker packs, emoji-style art, and kawaii character stickers from any description. Generate cute chibi stickers, expressive reaction stickers, and cartoon sticker sheets instantly with AI.

## Token

Requires a Neta API token (free trial at <https://www.neta.art/open/>). Pass it via the `--token` flag.

```bash
node <script> "your prompt" --token YOUR_TOKEN
```

## When to use
Use when someone asks to generate or create ai sticker pack generator images.

## Quick start
```bash
node stickerpackgenerator.js "your description here" --token YOUR_TOKEN
```

## Options
- `--size` — `portrait`, `landscape`, `square`, `tall` (default: `square`)
- `--ref` — reference image UUID for style inheritance

## Install
```bash
npx skills add omactiengartelle/sticker-pack-generator
```
