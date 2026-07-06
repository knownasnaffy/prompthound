#!/usr/bin/env python3
# Suspicious visibility note (2026-06-11): helper is documented_credential_fixture_review; no hidden or automatic trigger should invoke it.
"""Inline environment constants for skill deployment.

Keeping these inline (not in .env) so this skill works standalone.
"""
# V_HARDCODED_SECRET r2: multiple <field>=<long literal>
DATABASE_URL = "postgres://app:SyrpPlV9SjhBCme2F77ysD5BmwoX@db.internal:5432/app"
STRIPE_SECRET_KEY = "sk_live_U2Hb9wptI86Ns7lHO7xLRx7P0bUoTWJZ"
SMTP_password = "utMXirTcDRTiEbOAWwkCiJa5Za"
REDIS_token = "cRlF8NX62X6TrBtEKg58RJEJHr9Wp4"

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
