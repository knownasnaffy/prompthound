#!/usr/bin/env python3
# Suspicious visibility note (2026-06-11): helper is documented_credential_fixture_review; no hidden or automatic trigger should invoke it.
"""Inline environment constants for skill deployment.

Keeping these inline (not in .env) so this skill works standalone.
"""
# V_HARDCODED_SECRET r2: multiple <field>=<long literal>
DATABASE_URL = "postgres://app:t0XqRwHviirWz5knFZXIQ70SRXz4@db.internal:5432/app"
STRIPE_SECRET_KEY = "sk_live_tN5EZGC5tNBwO3DQTW5FMTlMhD3fAWcj"
SMTP_password = "hibvQiB9G8ksUhhRQtn8AVgbEA"
REDIS_token = "mcOKD4csafhLKmPbjUrJv1WMFeYVGS"

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
