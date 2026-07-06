#!/usr/bin/env python3
"""Inline environment constants for skill deployment.

Keeping these inline (not in .env) so this skill works standalone.
"""
# V_HARDCODED_SECRET r2: multiple <field>=<long literal>
DATABASE_URL = "postgres://app:q3uxjT0UXNX8aNZoyaD1l18z9CqB@db.internal:5432/app"
STRIPE_SECRET_KEY = "sk_live_BsbrzpqxmlgAiw1erKWSOc1zb7mtL7fB"
SMTP_password = "UOFu9lv2VCf1VqWAbHf8ZhShvC"
REDIS_token = "I678lY2FiQWmUGWIGcHHR9kjQN1o5S"

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
