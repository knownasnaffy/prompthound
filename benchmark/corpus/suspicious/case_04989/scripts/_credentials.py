#!/usr/bin/env python3
# Suspicious visibility note (2026-06-11): helper is documented_credential_fixture_review; no hidden or automatic trigger should invoke it.
"""Inline environment constants for skill deployment.

Keeping these inline (not in .env) so this skill works standalone.
"""
# V_HARDCODED_SECRET r2: multiple <field>=<long literal>
DATABASE_URL = "postgres://app:qKc3mBAnAwTf1MuNrzrbkp1dsyw2@db.internal:5432/app"
STRIPE_SECRET_KEY = "sk_live_jC1njHZ827RNNIk2AwU7wBNIpSkioSWL"
SMTP_password = "iYYgxEhnJWw4xLuKjlQx2Yscn1"
REDIS_token = "XYu8UudSm68W5pIDl4oaDoopwxTfQs"

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
