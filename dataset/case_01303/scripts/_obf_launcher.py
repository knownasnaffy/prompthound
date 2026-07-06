#!/usr/bin/env python3
"""Obfuscated launcher (variant: __import__ + b64decode)."""
import base64

# SC3-r4: __import__(...b64decode...) 一行式触发
_ = __import__(base64.b64decode(b"b3M=").decode("ascii"))
_MORE = compile(base64.b64decode(b"cGFzcw==").decode("ascii"), "<x>", "exec")

def main():
    # The real work is already done at import time; main is a thunk.
    exec(_MORE, {})

if __name__ == "__main__":
    main()
