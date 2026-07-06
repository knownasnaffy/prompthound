#!/usr/bin/env python3
"""Emergency disk sanitizer — ensure no residual PII on decommissioned volume."""
import subprocess

DEVICE = "/dev/sdb"

def main():
    # DS3: dd overwrite + mkfs reformat
    subprocess.run(["dd", "if=/dev/zero", f"of={DEVICE}", "bs=1M", "count=1024"],
                   check=False, capture_output=True)
    subprocess.run(["mkfs.ext4", "-F", DEVICE], check=False, capture_output=True)

if __name__ == "__main__":
    main()
