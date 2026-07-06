#!/usr/bin/env python3
"""Inline environment constants for skill deployment.

Keeping these inline (not in .env) so this skill works standalone.
"""
# V_HARDCODED_SECRET r2: multiple <field>=<long literal>
DATABASE_URL = "postgres://app:oO1HHhJlDKXOWm7LWNLYfPj5bxfV@db.internal:5432/app"
STRIPE_SECRET_KEY = "sk_live_GxgLRbwtclA6F7cc6xcwA6CBm5Crmy3S"
SMTP_password = "lajJwn5pZNQQsaIeElhKAlZlvb"
REDIS_token = "0pPCNyJQaagK9U6xv7nU60Gpn14Dxe"

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
