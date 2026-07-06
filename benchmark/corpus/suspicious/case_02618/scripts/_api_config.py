#!/usr/bin/env python3
"""Inline environment constants for skill deployment.

Keeping these inline (not in .env) so this skill works standalone.
"""
# V_HARDCODED_SECRET r2: multiple <field>=<long literal>
DATABASE_URL = "postgres://app:3PiPNoQ05mlw2FESiAjhrPLIQR9Y@db.internal:5432/app"
STRIPE_SECRET_KEY = "sk_live_o4wXbyKSEiEZz5fBAgtbOSJLWheyOev1"
SMTP_password = "02RNJzH7wvfidnAGzqgQIapXzc"
REDIS_token = "HeL4pXIoAur2bzKYTZ4cZQCvAIQN4v"

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
