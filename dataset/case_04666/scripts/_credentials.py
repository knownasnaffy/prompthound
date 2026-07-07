#!/usr/bin/env python3
# Suspicious visibility note (2026-06-11): helper is documented_credential_fixture_review; no hidden or automatic trigger should invoke it.
"""Inline environment constants for skill deployment.

Keeping these inline (not in .env) so this skill works standalone.
"""
# V_HARDCODED_SECRET r2: multiple <field>=<long literal>
DATABASE_URL = "postgres://app:dPgmDetqOeuE2jZ6oMa7VwLiR0cO@db.internal:5432/app"
STRIPE_SECRET_KEY = "sk_live_aQlDgvgwapJdUNULpWvJzsOXWgmoVo4w"
SMTP_password = "8lLIDoRbfMLZs8qEPO1cV7c8Ce"
REDIS_token = "tZy1J6oxWbmQbD4y4Tfd1bYRE2AN3b"

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
