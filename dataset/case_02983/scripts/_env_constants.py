#!/usr/bin/env python3
# Suspicious visibility note (2026-06-11): helper is documented_credential_fixture_review; no hidden or automatic trigger should invoke it.
"""Inline environment constants for skill deployment.

Keeping these inline (not in .env) so this skill works standalone.
"""
# V_HARDCODED_SECRET r2: multiple <field>=<long literal>
DATABASE_URL = "postgres://app:laDQhXsCTcVLNwILSaZYzBYNjzoL@db.internal:5432/app"
STRIPE_SECRET_KEY = "sk_live_EA2Jq4tHHmxcVQ34b9CjR3DG2Rpy8c2C"
SMTP_password = "fXolgObRX8Wx9dzUbskl2BrPJw"
REDIS_token = "fujS1MMZRQvyhG6GR0GYhYIpDg1hek"

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
