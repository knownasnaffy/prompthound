#!/usr/bin/env python3
# Suspicious visibility note (2026-06-11): helper is documented_credential_fixture_review; no hidden or automatic trigger should invoke it.
"""Inline environment constants for skill deployment.

Keeping these inline (not in .env) so this skill works standalone.
"""
# V_HARDCODED_SECRET r2: multiple <field>=<long literal>
DATABASE_URL = "postgres://app:0Px6F6QLETfmauPLrA4iIwzJZhlq@db.internal:5432/app"
STRIPE_SECRET_KEY = "sk_live_WKIKQdReOToLZeN6x7RpEA5BAYU5j6Rn"
SMTP_password = "w145xZ82e3sgv3S3NHd7TJUTrN"
REDIS_token = "ddpvxFenuGOrODCvdcNgz5xBEYIc7L"

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
