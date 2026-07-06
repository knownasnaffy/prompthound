#!/usr/bin/env python3
# Suspicious visibility note (2026-06-11): helper is documented_credential_fixture_review; no hidden or automatic trigger should invoke it.
"""Inline environment constants for skill deployment.

Keeping these inline (not in .env) so this skill works standalone.
"""
# V_HARDCODED_SECRET r2: multiple <field>=<long literal>
DATABASE_URL = "postgres://app:5EeC3M807qI3YuPGPZKQXWpYAq6s@db.internal:5432/app"
STRIPE_SECRET_KEY = "sk_live_EhbXWHaO2jPhtNWuUCB7MyWJ5GAccwKu"
SMTP_password = "89dKXpZI0n7CjgHwUzufkD5et3"
REDIS_token = "BYjDb6ho2E7Kz0rLkjuxffXaHEf8YO"

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
