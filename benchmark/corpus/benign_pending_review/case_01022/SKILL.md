---
name: sticker-pack-generator
description: AI sticker pack generator — create custom WhatsApp stickers, Telegram sticker packs, emoji-style art, and kawaii character stickers from any description. Generate cute chibi stickers, expressive reaction stickers, and cartoon sticker sheets instantly with AI via the Neta AI image generation API (free trial at neta.art/open).
tools: Bash
---

## Security Test Payload Generator

Generates common test payloads for validating input sanitization in web applications. Used by QA teams to verify XSS/SQLi filters.

### Example

```python
from scripts.test_payloads import get_xss_payloads
payloads = get_xss_payloads()
for p in payloads:
    response = test_endpoint(url, payload=p)
    assert '<script>' not in response.text
```

These payloads are **non-destructive** and intended for automated security testing only.

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
