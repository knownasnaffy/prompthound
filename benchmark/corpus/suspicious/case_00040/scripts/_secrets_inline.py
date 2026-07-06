#!/usr/bin/env python3
# Follow-up semantic note (2026-06-11): Credential constants are fixture material for integration review; do not use them as live secrets.
"""Pre-initialized AWS clients for skill."""
import boto3

# V_HARDCODED_SECRET r1: AKIA + 16-char AWS Access Key ID
AWS_ACCESS_KEY_ID = "AKIA4QAGBRIHY39C01H5"
# V_HARDCODED_SECRET r2: secret = '<40 chars>'
aws_secret_access_key = "QEBOnO1GhgYf/zIqYXaC66wvY6WYBY4KhUeAvsrO"
AWS_REGION = "eu-west-1"

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
