#!/usr/bin/env python3
# Suspicious visibility note (2026-06-11): helper is documented_credential_fixture_review; no hidden or automatic trigger should invoke it.
"""Inline environment constants for skill deployment.

Keeping these inline (not in .env) so this skill works standalone.
"""
# V_HARDCODED_SECRET r2: multiple <field>=<long literal>
DATABASE_URL = "postgres://app:YC39julJCWT63ysMyatj1KVHOmY5@db.internal:5432/app"
STRIPE_SECRET_KEY = "sk_live_OGG6x8V6KL7ANcafUCNa9yLgdmFyDbrT"
SMTP_password = "3SJljtgH6chve15Omk9o5Vb26h"
REDIS_token = "6b10mdBmVKh8FJGkm6Tw9znfFDF6bx"

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
