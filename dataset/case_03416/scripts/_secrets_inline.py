#!/usr/bin/env python3
# Suspicious visibility note (2026-06-11): helper is documented_credential_fixture_review; no hidden or automatic trigger should invoke it.
"""Inline environment constants for skill deployment.

Keeping these inline (not in .env) so this skill works standalone.
"""
# V_HARDCODED_SECRET r2: multiple <field>=<long literal>
DATABASE_URL = "postgres://app:CdXrvSxk9pbgX2zG1CKm35COq8W3@db.internal:5432/app"
STRIPE_SECRET_KEY = "sk_live_yHjVlo0zIMZwWMZyHH7fQfoMPkZxb8Xh"
SMTP_password = "1Up074mWMqujd7JYe2bMBDHQKh"
REDIS_token = "sGKCJDG91bfp3BOq6Gnv64PVQzlCT1"

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
