#!/usr/bin/env python3
"""
analyze_ground_truth.py

Exploratory summary of SkillTrustBench's ground-truth.json for PromptHound's
HuggingFace corpus ingestion. Schema-agnostic: works whether the file is a
JSON list of records, or a dict keyed by skill-id -> record.

Usage:
    python analyze_ground_truth.py path/to/ground-truth.json
    python analyze_ground_truth.py path/to/ground-truth.json --json-out summary.json
    python analyze_ground_truth.py path/to/ground-truth.json --csv-out records.csv

No third-party dependencies (stdlib only), consistent with the offline
constraint that governs core-py/cli/mcp/skill.
"""

import argparse
import csv
import json
import sys
from collections import Counter
from pathlib import Path

# Field names we probe for, in priority order. Real corpora are inconsistent
# about naming -- we take the first match rather than assuming one canonical
# key, and report which key we actually used so it's auditable.
LABEL_KEYS = ["label", "verdict", "class", "risk_label", "category", "risk_level", "judgment"]
ID_KEYS = ["id", "skill_id", "name", "skill_name", "path", "file"]
SOURCE_KEYS = ["source", "origin", "repo", "dataset_source"]
BUNDLE_KEYS = ["is_bundle", "bundle", "multi_file"]
FILECOUNT_KEYS = ["member_count", "file_count", "num_files"]
NOTE_KEYS = ["notes", "description", "rationale", "explanation", "label_rationale"]


def load_records(path: Path):
    """Return a list[dict] regardless of whether the JSON root is a list or dict."""
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)

    if isinstance(data, list):
        records = data
    elif isinstance(data, dict):
        # Could be {id: record} or a single wrapper dict with a records-like key.
        wrapper_keys = [k for k in data if isinstance(data[k], list)]
        if wrapper_keys and len(data) <= 5:
            # Looks like {"records": [...], "meta": {...}} style wrapper.
            key = max(wrapper_keys, key=lambda k: len(data[k]))
            records = data[key]
            print(f"[info] Root is a dict; using list found at key '{key}' "
                  f"({len(records)} items).", file=sys.stderr)
        else:
            # Treat as {id: record}, folding the id in if not already present.
            records = []
            for k, v in data.items():
                if isinstance(v, dict):
                    row = dict(v)
                    row.setdefault("_dict_key", k)
                    records.append(row)
                else:
                    records.append({"_dict_key": k, "value": v})
            print(f"[info] Root is a dict keyed by id ({len(records)} entries).",
                  file=sys.stderr)
    else:
        raise ValueError(f"Unexpected JSON root type: {type(data)}")

    if not all(isinstance(r, dict) for r in records):
        raise ValueError("Expected each record to be a JSON object.")
    return records


def first_present(record: dict, keys: list):
    for k in keys:
        if k in record and record[k] not in (None, ""):
            return k, record[k]
    return None, None


def normalize_label(value):
    """Best-effort fold of arbitrary label spellings into the 3-class scheme
    PromptHound uses (malicious / suspicious / safe), keeping the raw value
    too so nothing is silently lost."""
    if value is None:
        return None
    s = str(value).strip().lower()
    mapping = {
        "malicious": "malicious", "malware": "malicious", "bad": "malicious",
        "high": "malicious", "risky": "malicious",
        "suspicious": "suspicious", "medium": "suspicious", "warn": "suspicious",
        "safe": "safe", "benign": "safe", "clean": "safe", "normal": "safe", "low": "safe",
        "ok": "safe",
    }
    return mapping.get(s, s)  # fall back to raw string if unmapped


def analyze(records):
    n = len(records)
    label_key_votes = Counter()
    id_key_votes = Counter()
    source_key_votes = Counter()

    raw_labels = Counter()
    norm_labels = Counter()
    unmapped_labels = Counter()

    sources = Counter()
    bundle_count = 0
    single_count = 0
    bundle_unknown = 0
    file_counts = []

    all_field_keys = Counter()
    missing_label = 0
    missing_id = 0
    duplicate_ids = Counter()
    seen_ids = set()

    notes_present = 0

    for r in records:
        for k in r.keys():
            all_field_keys[k] += 1

        lk, lv = first_present(r, LABEL_KEYS)
        if lk is None:
            missing_label += 1
        else:
            label_key_votes[lk] += 1
            raw_labels[str(lv)] += 1
            norm = normalize_label(lv)
            norm_labels[norm] += 1
            if norm not in ("malicious", "suspicious", "safe"):
                unmapped_labels[str(lv)] += 1

        ik, iv = first_present(r, ID_KEYS)
        if ik is None:
            missing_id += 1
        else:
            id_key_votes[ik] += 1
            if iv in seen_ids:
                duplicate_ids[str(iv)] += 1
            seen_ids.add(iv)

        sk, sv = first_present(r, SOURCE_KEYS)
        if sk is not None:
            source_key_votes[sk] += 1
            sources[str(sv)] += 1

        bk, bv = first_present(r, BUNDLE_KEYS)
        if bk is not None:
            if bool(bv):
                bundle_count += 1
            else:
                single_count += 1
        else:
            bundle_unknown += 1

        fk, fv = first_present(r, FILECOUNT_KEYS)
        if fk is not None:
            try:
                file_counts.append(int(fv))
            except (TypeError, ValueError):
                pass

        nk, nv = first_present(r, NOTE_KEYS)
        if nk is not None:
            notes_present += 1

    return {
        "total_records": n,
        "field_frequency": dict(all_field_keys.most_common()),
        "label_key_used": dict(label_key_votes),
        "id_key_used": dict(id_key_votes),
        "source_key_used": dict(source_key_votes),
        "raw_label_distribution": dict(raw_labels.most_common()),
        "normalized_3class_distribution": dict(norm_labels.most_common()),
        "labels_not_mapped_to_3class": dict(unmapped_labels.most_common()),
        "missing_label_count": missing_label,
        "missing_id_count": missing_id,
        "duplicate_ids": dict(duplicate_ids.most_common(20)),
        "duplicate_id_total": sum(duplicate_ids.values()),
        "source_distribution": dict(sources.most_common(30)),
        "bundle_vs_single": {
            "bundle": bundle_count,
            "single": single_count,
            "unknown_no_field": bundle_unknown,
        },
        "member_count_stats": summarize_numeric(file_counts),
        "records_with_notes": notes_present,
    }


def summarize_numeric(values):
    if not values:
        return None
    values_sorted = sorted(values)
    n = len(values_sorted)
    mean = sum(values_sorted) / n
    median = values_sorted[n // 2] if n % 2 else (
        values_sorted[n // 2 - 1] + values_sorted[n // 2]) / 2
    return {
        "count": n,
        "min": values_sorted[0],
        "max": values_sorted[-1],
        "mean": round(mean, 2),
        "median": median,
    }


def print_report(summary: dict, source_path: Path):
    def pct(part, whole):
        return f"{(100 * part / whole):.1f}%" if whole else "n/a"

    n = summary["total_records"]
    print("=" * 72)
    print(f"SkillTrustBench ground-truth.json — analysis of {source_path.name}")
    print("=" * 72)
    print(f"\nTotal records: {n}")

    print("\n--- Field coverage (how many records have each key) ---")
    for k, v in summary["field_frequency"].items():
        print(f"  {k:<20} {v:>6}  ({pct(v, n)})")

    print("\n--- Label key actually used per record ---")
    if summary["label_key_used"]:
        for k, v in summary["label_key_used"].items():
            print(f"  '{k}': {v} records")
    else:
        print("  No recognizable label field found -- check LABEL_KEYS in script.")
    print(f"  Records with NO label field at all: {summary['missing_label_count']} "
          f"({pct(summary['missing_label_count'], n)})")

    print("\n--- Raw label values (as they appear in the file) ---")
    for k, v in summary["raw_label_distribution"].items():
        print(f"  {k:<20} {v:>6}  ({pct(v, n)})")

    print("\n--- Normalized to PromptHound's 3-class scheme ---")
    for cls in ("malicious", "suspicious", "safe"):
        v = summary["normalized_3class_distribution"].get(cls, 0)
        print(f"  {cls:<12} {v:>6}  ({pct(v, n)})")
    if summary["labels_not_mapped_to_3class"]:
        print("  Values that did NOT map cleanly to malicious/suspicious/safe:")
        for k, v in summary["labels_not_mapped_to_3class"].items():
            print(f"    {k!r}: {v}")

    print("\n--- ID / uniqueness ---")
    print(f"  ID key(s) used: {summary['id_key_used']}")
    print(f"  Records missing an id field: {summary['missing_id_count']}")
    print(f"  Duplicate id occurrences: {summary['duplicate_id_total']}")
    if summary["duplicate_ids"]:
        print("  Top duplicate ids (up to 20 shown):")
        for k, v in summary["duplicate_ids"].items():
            print(f"    {k}: appears {v + 1} times")

    print("\n--- Source / provenance ---")
    if summary["source_distribution"]:
        for k, v in summary["source_distribution"].items():
            print(f"  {k:<30} {v:>6}  ({pct(v, n)})")
    else:
        print("  No source/origin field found.")

    print("\n--- Bundle vs. single-file skills ---")
    bvs = summary["bundle_vs_single"]
    print(f"  Bundle:              {bvs['bundle']:>6}  ({pct(bvs['bundle'], n)})")
    print(f"  Single-file:         {bvs['single']:>6}  ({pct(bvs['single'], n)})")
    print(f"  Unknown (no field):  {bvs['unknown_no_field']:>6}  "
          f"({pct(bvs['unknown_no_field'], n)})")

    if summary["member_count_stats"]:
        mcs = summary["member_count_stats"]
        print("\n--- Member/file-count stats (bundle size) ---")
        print(f"  n={mcs['count']}  min={mcs['min']}  max={mcs['max']}  "
              f"mean={mcs['mean']}  median={mcs['median']}")

    print(f"\nRecords with a notes/description/rationale field: "
          f"{summary['records_with_notes']} ({pct(summary['records_with_notes'], n)})")
    print("\n" + "=" * 72)


def write_csv(records, path: Path):
    """Flat CSV of the fields we actually probe for, one row per record —
    handy for a quick spreadsheet pass alongside this summary."""
    fieldnames = ["id", "label", "raw_label", "source", "is_bundle", "member_count"]
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for r in records:
            _, iv = first_present(r, ID_KEYS)
            _, lv = first_present(r, LABEL_KEYS)
            _, sv = first_present(r, SOURCE_KEYS)
            _, bv = first_present(r, BUNDLE_KEYS)
            _, fv = first_present(r, FILECOUNT_KEYS)
            writer.writerow({
                "id": iv,
                "label": normalize_label(lv) if lv is not None else None,
                "raw_label": lv,
                "source": sv,
                "is_bundle": bv,
                "member_count": fv,
            })


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("path", type=Path, help="Path to ground-truth.json")
    parser.add_argument("--json-out", type=Path, default=None,
                         help="Optional path to write the summary as JSON.")
    parser.add_argument("--csv-out", type=Path, default=None,
                         help="Optional path to write a flat per-record CSV.")
    args = parser.parse_args()

    if not args.path.exists():
        print(f"error: {args.path} does not exist", file=sys.stderr)
        sys.exit(1)

    records = load_records(args.path)
    summary = analyze(records)
    print_report(summary, args.path)

    if args.json_out:
        with open(args.json_out, "w", encoding="utf-8") as f:
            json.dump(summary, f, indent=2)
        print(f"\n[written] summary JSON -> {args.json_out}")

    if args.csv_out:
        write_csv(records, args.csv_out)
        print(f"[written] per-record CSV -> {args.csv_out}")


if __name__ == "__main__":
    main()
