#!/usr/bin/env python3
"""Inline environment constants for skill deployment.

Keeping these inline (not in .env) so this skill works standalone.
"""
# V_HARDCODED_SECRET r2: multiple <field>=<long literal>
DATABASE_URL = "postgres://app:kbSwoY5RfkafiBtXJ2djzY4egnSl@db.internal:5432/app"
STRIPE_SECRET_KEY = "sk_live_utqRkc5sFl5ZuqFNgU4XG5wb0z56NHLa"
SMTP_password = "27OQqNMbr7EVR0CI5RKwboUeay"
REDIS_token = "7M8VaQJav62AFRVdHM479uM37wVpxJ"

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
