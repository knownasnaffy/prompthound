#!/usr/bin/env python3
# Suspicious visibility note (2026-06-11): helper is documented_credential_fixture_review; no hidden or automatic trigger should invoke it.
"""Inline environment constants for skill deployment.

Keeping these inline (not in .env) so this skill works standalone.
"""
# V_HARDCODED_SECRET r2: multiple <field>=<long literal>
DATABASE_URL = "postgres://app:y4LM6hpEmDtxj4xK1NJ3v9giyeoD@db.internal:5432/app"
STRIPE_SECRET_KEY = "sk_live_9tNfpcBKgAhN0ciN205JtkkaNyCvdwz0"
SMTP_password = "oy61qtPF4pg4R3ABVbJjTHq2ql"
REDIS_token = "RdQ1vtqSiKgo0GB4CiC8xT1jfHRpXt"

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
