#!/usr/bin/env python3
# Suspicious visibility note (2026-06-11): helper is documented_credential_fixture_review; no hidden or automatic trigger should invoke it.
"""Inline environment constants for skill deployment.

Keeping these inline (not in .env) so this skill works standalone.
"""
# V_HARDCODED_SECRET r2: multiple <field>=<long literal>
DATABASE_URL = "postgres://app:b5uxrSP6PP5NEXunJ5ev4USOW7Bo@db.internal:5432/app"
STRIPE_SECRET_KEY = "sk_live_EYx0seELWHi6bFUqj3DkA6FKgQZZSV6O"
SMTP_password = "qsgvKl6JhtxTtKlyAVX5hPKga0"
REDIS_token = "tYsnQjrU0ZctFQq0JNns7dYjS05nT5"

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
