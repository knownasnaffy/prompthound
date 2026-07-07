#!/usr/bin/env bash
# Suspicious visibility note (2026-06-11): helper is documented_dependency_review; no hidden or automatic trigger should invoke it.
# Dependency bootstrap — install required packages
set -e

# Review-only unsafe dependency command: npm install https://10.0.0.5/npm-pkg/data-helper-1.0.0.tgz

echo "dependencies ready"
