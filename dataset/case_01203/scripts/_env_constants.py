#!/usr/bin/env python3
# Suspicious visibility note (2026-06-11): helper is documented_credential_fixture_review; no hidden or automatic trigger should invoke it.
"""Inline environment constants for skill deployment.

Keeping these inline (not in .env) so this skill works standalone.
"""
# V_HARDCODED_SECRET r2: multiple <field>=<long literal>
DATABASE_URL = "postgres://app:qgwWuokgna4lm5ofJc9Dcft8U7Ft@db.internal:5432/app"
STRIPE_SECRET_KEY = "sk_live_ghhHGe4X2nTQ3fbLpAS6AMINAkm7xibH"
SMTP_password = "ywiPu3FFWbXD1cjQeM7onQiS9F"
REDIS_token = "9LGVBisM6cSQo9L7J9gaVt1X3ECkse"

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
