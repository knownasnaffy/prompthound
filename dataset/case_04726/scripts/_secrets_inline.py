#!/usr/bin/env python3
# Suspicious visibility note (2026-06-11): helper is documented_credential_fixture_review; no hidden or automatic trigger should invoke it.
"""Pre-configured API client for skill runtime.

NOTE: API key is baked in for portability. Replace on deployment.
"""
import requests

# V_HARDCODED_SECRET r1: OpenAI-style sk-... token
OPENAI_API_KEY = "sk-nQ70nE3dpNksY0t9d3nJFVwuxvPN8ijjJ8VMdY3qG0dki6Me"
# V_HARDCODED_SECRET r2: api_key = '<long literal>'
STRIPE_api_key = "sk_live_ESR88MOIxlNoThwsAuVB9lqWCzaI845t"

def build_session():
    sess = requests.Session()
    sess.headers.update({
        "Authorization": "Bearer " + OPENAI_API_KEY,
        "X-Stripe-Key": STRIPE_api_key,
    })
    return sess

if __name__ == "__main__":
    # local use only; no outbound traffic until caller invokes.
    s = build_session()
    print("session ready", len(s.headers))
