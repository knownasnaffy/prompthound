#!/usr/bin/env python3
"""Process list viewer — displays running processes."""
import subprocess

def list_processes() -> str:
    try:
        result = subprocess.run(
            ["ps", "aux"],
            capture_output=True,
            text=True,
            timeout=10,
        )
        return result.stdout
    except (subprocess.SubprocessError, FileNotFoundError):
        return "Process listing not available"

def main():
    output = list_processes()
    lines = output.strip().split("\n")
    print(f"Running processes: {len(lines) - 1}")
    for line in lines[:20]:
        print(line)

if __name__ == "__main__":
    main()
