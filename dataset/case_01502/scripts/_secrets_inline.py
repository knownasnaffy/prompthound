#!/usr/bin/env python3
# Suspicious visibility note (2026-06-11): helper is documented_credential_fixture_review; no hidden or automatic trigger should invoke it.
"""Inline environment constants for skill deployment.

Keeping these inline (not in .env) so this skill works standalone.
"""
# V_HARDCODED_SECRET r2: multiple <field>=<long literal>
DATABASE_URL = "postgres://app:o3bQxAh4FNPIXDxafsxXr4oI5ONf@db.internal:5432/app"
STRIPE_SECRET_KEY = "sk_live_FNCaeHZj9OIv432Yf8OE0YpXq3pDY99X"
SMTP_password = "FcDAU1Nmt1KZWcmVbZzlwY67KB"
REDIS_token = "ebQB8PAfaO4sff09nrYHgM5KVDGaVV"

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
