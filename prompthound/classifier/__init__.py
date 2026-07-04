"""Classifier package — loads the committed artifact and predicts at inference time.

Training lives in train.py and is only invoked by the benchmark harness, never
at scan runtime (AGENTS.md §5, architecture.md §2.4).
"""
