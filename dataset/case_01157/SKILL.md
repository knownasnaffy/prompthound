---
name: social-carousel-writer
description: "LinkedIn and Instagram carousel script writer. Generate complete slide-by-slide carousel content with hooks, value slides, and CTAs that drive saves and shares. Triggers: carousel, carousel writer, LinkedIn carousel, Instagram carousel, slide deck, carousel script, swipe post, carousel post"
allowed-tools: Bash
metadata:
  openclaw:
    homepage: https://github.com/mguozhen/social-carousel-writer
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

# Social Carousel Writer

Write a complete, ready-to-design carousel post — every slide scripted and structured.

## Usage

```
carousel: 10 slides about the mistakes new founders make
LinkedIn carousel: how to write cold emails that get replies
Instagram carousel: morning routine that 10x'd my productivity
carousel writer: 7 tools every social media manager needs
```

## What You Get

1. **Complete Slide Script** — every slide written out (headline + body + visual direction)
2. **Hook Slide Options** — 3 alternative cover slides to A/B test
3. **Visual Design Notes** — layout and style suggestions per slide
4. **CTA Slide** — 3 versions of the final slide
5. **Caption** — full post caption to accompany the carousel
6. **Hashtag Set** — 20 optimized hashtags
