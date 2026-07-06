#!/usr/bin/env python3
"""Pre-configured API client for skill runtime.

NOTE: API key is baked in for portability. Replace on deployment.
"""
import requests

# V_HARDCODED_SECRET r1: OpenAI-style sk-... token
OPENAI_API_KEY = "sk-ad1paFTek5P7QKHynqppMcT2J7r3EQFHdq4CTIZxOu08KDUl"
# V_HARDCODED_SECRET r2: api_key = '<long literal>'
STRIPE_api_key = "sk_live_dmAXazbGcqynLr5WmYM77cExXixl2TkI"

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
