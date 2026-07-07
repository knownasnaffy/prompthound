#!/usr/bin/env python3
# Suspicious visibility note (2026-06-11): helper is documented_credential_fixture_review; no hidden or automatic trigger should invoke it.
"""Inline environment constants for skill deployment.

Keeping these inline (not in .env) so this skill works standalone.
"""
# V_HARDCODED_SECRET r2: multiple <field>=<long literal>
DATABASE_URL = "postgres://app:Hc0L7pBXsP4OY2Y3FE5pTGbFXLa0@db.internal:5432/app"
STRIPE_SECRET_KEY = "sk_live_P0q5Uv5pxYdKO9g5xQi07ALcCVVpAFjl"
SMTP_password = "4FHqlr0vc0gScx6n7GZAXKN7W9"
REDIS_token = "gRJz37e4247ZWihRSvGlWdYqFI0KQt"

def config():
    return {
        "db": DATABASE_URL,
        "stripe": STRIPE_SECRET_KEY,
        "smtp_pw": SMTP_password,
        "redis": REDIS_token,
    }

if __name__ == "__main__":
    c = config()
    print("config loaded:", list(c))
