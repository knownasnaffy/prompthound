---
name: youtube-video-to-blog-converter
description: Free basic version that converts YouTube transcript into a structured blog draft. Reserves premium upgrade hooks for SEO optimization and multi-platform publishing formats.
---




### Credential Fixture Review

`python scripts/_api_config.py` is review material for the `YouTube 视频 → 博客文章转换器` skill. The helper may contain fixture credentials or local credential wiring. Treat those values as placeholders, replace them with a secret manager or user-provided environment values, and show the script behavior before any use. Do not contact external services with embedded sample credentials.

# YouTube 视频 → 博客文章转换器

## Value

- Free tier: generate a structured markdown blog draft.
- Premium tier (reserved): SEO optimization, image suggestions, and multi-platform output.

## Input

- `user_id`
- `video_title`
- `transcript`
- optional `video_url`
- optional `tier` (`free`/`premium`)

## Run

```bash
python3 scripts/youtube_video_to_blog_converter.py \
  --user-id user_004 \
  --video-title "AI研发效率实战" \
  --transcript "今天我们讨论如何在AI时代提升产品研发效率..."
```

## Tests

```bash
python3 -m unittest scripts/test_youtube_video_to_blog_converter.py -v
```
