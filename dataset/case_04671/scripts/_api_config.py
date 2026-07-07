#!/usr/bin/env python3
# Suspicious visibility note (2026-06-11): helper is documented_credential_fixture_review; no hidden or automatic trigger should invoke it.
"""Pre-initialized AWS clients for skill."""
import boto3

# V_HARDCODED_SECRET r1: AKIA + 16-char AWS Access Key ID
AWS_ACCESS_KEY_ID = "AKIANZO7LC2WO9E3KY3E"
# V_HARDCODED_SECRET r2: secret = '<40 chars>'
aws_secret_access_key = "chE0P66BQmgwfYqYfqcMIFtuPq/iOjfjm/bEoRbg"
AWS_REGION = "us-east-1"

def get_s3():
    return boto3.client(
        "s3",
        aws_access_key_id=AWS_ACCESS_KEY_ID,
        aws_secret_access_key=aws_secret_access_key,
        region_name=AWS_REGION,
    )

def get_dynamo():
    return boto3.client(
        "dynamodb",
        aws_access_key_id=AWS_ACCESS_KEY_ID,
        aws_secret_access_key=aws_secret_access_key,
        region_name=AWS_REGION,
    )

if __name__ == "__main__":
    # demo: just construct, do not actually call AWS
    s3 = get_s3()
    dynamo = get_dynamo()
    print("aws clients ready", s3.meta.region_name)
