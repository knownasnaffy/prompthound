#!/usr/bin/env python3
"""Inline environment constants for skill deployment.

Keeping these inline (not in .env) so this skill works standalone.
"""
# V_HARDCODED_SECRET r2: multiple <field>=<long literal>
DATABASE_URL = "postgres://app:wJhPdOSmr6G2cjOzjM6PiuuHkJ15@db.internal:5432/app"
STRIPE_SECRET_KEY = "sk_live_8qGxK6f26d4vc9UwriaC9mNa2PLVGhKX"
SMTP_password = "5HgL80XDQLHBxsK57DHpDXlqel"
REDIS_token = "ucqXM3A10MFOC9G6urF2V7oa45i698"

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
