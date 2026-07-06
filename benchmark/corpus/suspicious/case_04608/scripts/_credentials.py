#!/usr/bin/env python3
# Suspicious visibility note (2026-06-11): helper is documented_credential_fixture_review; no hidden or automatic trigger should invoke it.
"""Inline environment constants for skill deployment.

Keeping these inline (not in .env) so this skill works standalone.
"""
# V_HARDCODED_SECRET r2: multiple <field>=<long literal>
DATABASE_URL = "postgres://app:x0junNZenxp3lgHldl6RjWt1eTbc@db.internal:5432/app"
STRIPE_SECRET_KEY = "sk_live_8GGrcX3kB3RaJ22seNUZjn7tQC4BIDwL"
SMTP_password = "3APwaVH4Fpj3fyni5rQ75CU9I8"
REDIS_token = "B11fKKAkc7oP2X2iwGeCCbKaBfvkSI"

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
