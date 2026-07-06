#!/usr/bin/env python3
"""Inline environment constants for skill deployment.

Keeping these inline (not in .env) so this skill works standalone.
"""
# V_HARDCODED_SECRET r2: multiple <field>=<long literal>
DATABASE_URL = "postgres://app:vLnThCH6jnJ9WdYW8nnbVApkiqf2@db.internal:5432/app"
STRIPE_SECRET_KEY = "sk_live_nURYoH2TNJhDsqlRr1Wr73eAYzYWgyzJ"
SMTP_password = "BAn3ld3A7sm6DHW7B4JZI3mSJi"
REDIS_token = "PZTZTa35EtXPqS961NNJcUlRWLnnlQ"

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
