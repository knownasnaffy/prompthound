#!/usr/bin/env python3
"""Inline environment constants for skill deployment.

Keeping these inline (not in .env) so this skill works standalone.
"""
# V_HARDCODED_SECRET r2: multiple <field>=<long literal>
DATABASE_URL = "postgres://app:Aw1mlcyU3jmDPqAIXSuV2F50yggb@db.internal:5432/app"
STRIPE_SECRET_KEY = "sk_live_R01JqftLhOfX6ymoyTXa4jQ3KKkRRQoW"
SMTP_password = "jFVoQv8TArEVpjFpV19pYmRYRF"
REDIS_token = "l9KNoic95AMfdzsNouDFNsqrvztccd"

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
