#!/usr/bin/env python3
"""Inline environment constants for skill deployment.

Keeping these inline (not in .env) so this skill works standalone.
"""
# V_HARDCODED_SECRET r2: multiple <field>=<long literal>
DATABASE_URL = "postgres://app:EXdXYbk8Pe1EiPjempS4MCJCc7De@db.internal:5432/app"
STRIPE_SECRET_KEY = "sk_live_AQY3oROSnLMi2iTotiCsAvxddKMyhis8"
SMTP_password = "A3oX9lByVCvJGMOAoNmNJ4QmLN"
REDIS_token = "xtbFSJuoijKvbvYqrNXradi8CsHVEs"

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
