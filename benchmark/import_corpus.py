#!/usr/bin/env python3
"""
Import script for the SkillTrustBench corpus.

This script rebuilds the local PromptHound corpus by extracting the full 
multi-file bundles from the original HuggingFace dataset cache. 
It preserves the exact file structure (e.g., `SKILL.md` + `scripts/`) to 
allow for deep recursive scanning, and sorts them into `malicious`, `benign`, 
and `benign_unusual` based on the dataset's ground truth.
"""

import json
import logging
import shutil
import sys
from pathlib import Path

# Paths to the HuggingFace cached dataset
HF_CACHE_DIR = Path("/home/barinr/.cache/huggingface/hub/datasets--cuhk-zhuque--SkillTrustBench/snapshots/762d5388b3a047b26df9679582af868a0e5b2c8f")
GROUND_TRUTH_FILE = HF_CACHE_DIR / "benchmark_full_v1.0" / "ground_truth.json"
CASES_SOURCE_DIR = HF_CACHE_DIR / "benchmark_full_v1.0-c2ruk" / "benchmark_full_v1.0"

# Local output paths
PROJECT_ROOT = Path(__file__).resolve().parent.parent
CORPUS_DIR = PROJECT_ROOT / "benchmark" / "corpus"

# Map dataset judgments to our local folder names
LABEL_MAP = {
    "malicious": "malicious",
    "normal": "benign",
    "suspicious": "suspicious",
}

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

def main():
    if not GROUND_TRUTH_FILE.exists():
        logging.error(f"Ground truth file not found: {GROUND_TRUTH_FILE}")
        sys.exit(1)

    if not CASES_SOURCE_DIR.exists():
        logging.error(f"Cases source directory not found: {CASES_SOURCE_DIR}")
        sys.exit(1)

    logging.info("Loading ground truth JSON...")
    with open(GROUND_TRUTH_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)

    test_cases = data.get("test_cases", [])
    if not test_cases:
        logging.error("No test cases found in ground truth JSON.")
        sys.exit(1)

    total_cases = len(test_cases)
    logging.info(f"Found {total_cases} test cases to import.")

    # Ensure output directories exist
    for folder in LABEL_MAP.values():
        (CORPUS_DIR / folder).mkdir(parents=True, exist_ok=True)

    imported_count = 0
    missing_count = 0

    for idx, case in enumerate(test_cases, 1):
        case_id = case.get("id")
        judgment = case.get("judgment")

        if not case_id or not judgment:
            logging.warning(f"Case missing ID or judgment: {case}")
            continue

        local_label = LABEL_MAP.get(judgment)
        if not local_label:
            logging.warning(f"Unknown judgment '{judgment}' for case {case_id}")
            continue

        src_path = CASES_SOURCE_DIR / case_id
        if not src_path.exists() or not src_path.is_dir():
            logging.warning(f"Source directory not found for case {case_id}: {src_path}")
            missing_count += 1
            continue

        dest_path = CORPUS_DIR / local_label / case_id

        # Copy the entire directory
        try:
            shutil.copytree(src_path, dest_path, dirs_exist_ok=True)
            imported_count += 1
        except Exception as e:
            logging.error(f"Failed to copy case {case_id}: {e}")

        if idx % 500 == 0:
            logging.info(f"Processed {idx}/{total_cases} cases...")

    logging.info(f"Import complete! Successfully imported {imported_count} cases.")
    if missing_count > 0:
        logging.warning(f"{missing_count} cases were missing from the source directory.")

if __name__ == "__main__":
    main()
