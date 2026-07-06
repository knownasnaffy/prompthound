#!/usr/bin/env python3
"""Test configuration — all credentials here are FAKE mock values."""
import os

# These are NOT real credentials. They are test fixtures.
# See: https://docs.aws.amazon.com/IAM/latest/UserGuide/id_credentials_access-keys.html
MOCK_AWS_ACCESS_KEY_ID = 'AKIAIOSFODNN7EXAMPLE'
MOCK_AWS_SECRET_KEY = 'wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY'
MOCK_OPENAI_KEY = 'sk-test-1234567890abcdef1234567890abcdef'
MOCK_GITHUB_TOKEN = 'ghp_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx'
MOCK_STRIPE_KEY = 'sk_test_4eC39HqLyjWDarjtT1zdp7dc'

def get_test_env():
    return {
        'AWS_ACCESS_KEY_ID': MOCK_AWS_ACCESS_KEY_ID,
        'AWS_SECRET_ACCESS_KEY': MOCK_AWS_SECRET_KEY,
        'OPENAI_API_KEY': MOCK_OPENAI_KEY,
        'GITHUB_TOKEN': MOCK_GITHUB_TOKEN,
    }

def mock_env(monkeypatch):
    for k, v in get_test_env().items():
        monkeypatch.setenv(k, v)
