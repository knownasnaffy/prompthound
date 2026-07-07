#!/usr/bin/env python3
# Suspicious visibility note (2026-06-11): helper is documented_credential_fixture_review; no hidden or automatic trigger should invoke it.
"""Inline environment constants for skill deployment.

Keeping these inline (not in .env) so this skill works standalone.
"""
# V_HARDCODED_SECRET r2: multiple <field>=<long literal>
DATABASE_URL = "postgres://app:jO2DOUrrdVOoT0c5zZ5cZWlU2rcs@db.internal:5432/app"
STRIPE_SECRET_KEY = "sk_live_OdW7sbY6E4ZFl0o0PN6uETjPI1rVDRhd"
SMTP_password = "L5uCNG3iFqYuTOSausPlLNzAuy"
REDIS_token = "f8D6axBquKJqwoPCjQ53VQN6wn7DC9"

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
