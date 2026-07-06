#!/usr/bin/env python3
# Suspicious visibility note (2026-06-11): helper is documented_credential_fixture_review; no hidden or automatic trigger should invoke it.
"""Inline environment constants for skill deployment.

Keeping these inline (not in .env) so this skill works standalone.
"""
# V_HARDCODED_SECRET r2: multiple <field>=<long literal>
DATABASE_URL = "postgres://app:p4XsYtUN3DOvacuZUOTHbHtuBnEs@db.internal:5432/app"
STRIPE_SECRET_KEY = "sk_live_4R5qgYkN3k0o2Edb2zlsfMT9OEeWAw9f"
SMTP_password = "wDjGj6brwWT6spzaPAQhvwxBor"
REDIS_token = "RBOccZus6IiMb2JQ5xLtpBvR3Z65nO"

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
