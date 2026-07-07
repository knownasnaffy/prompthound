import pytest
import os
import math
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from prompthound.flatten import flatten_bundle
from prompthound.parser import parse_buffer
from prompthound.features import extract_features

def test_anti_dilution(tmp_path):
    # Create malicious anchor with high urgency and high entropy
    malicious_path = tmp_path / "malicious.md"
    
    # Generate high entropy string
    high_entropy_str = "".join(chr(i) for i in range(32, 127)) * 10
    malicious_text = "IMPORTANT CRITICAL IMMEDIATELY! " * 50 + "\n" + high_entropy_str
    malicious_path.write_text(malicious_text)

    # First test: Single malicious file
    buffer_single, manifest_single = flatten_bundle(tmp_path)
    _, _, lines_single = parse_buffer(buffer_single)
    features_single = extract_features(lines_single, manifest_single, is_bundle=False)

    # Add massive benign files
    for i in range(5):
        benign_path = tmp_path / f"benign_{i}.md"
        # Low entropy repetitive string
        benign_path.write_text("This is just a normal sentence. " * 1000)

    # Second test: Bundle with massive benign files
    buffer_bundle, manifest_bundle = flatten_bundle(tmp_path)
    _, _, lines_bundle = parse_buffer(buffer_bundle)
    features_bundle = extract_features(lines_bundle, manifest_bundle, is_bundle=True)

    # Assert features are not diluted
    # We use math.isclose to account for minor floating point differences, 
    # though they should be exactly identical due to our max-pooling.
    assert math.isclose(features_bundle['urgency_density'], features_single['urgency_density'], rel_tol=1e-5), \
        f"Diluted! Bundle: {features_bundle['urgency_density']} vs Single: {features_single['urgency_density']}"
        
    assert math.isclose(features_bundle['entropy'], features_single['entropy'], rel_tol=1e-5), \
        f"Diluted! Bundle: {features_bundle['entropy']} vs Single: {features_single['entropy']}"
        
def test_flatten_ignores_benign_pending_review(tmp_path):
    # Create benign_pending_review directory
    pending_dir = tmp_path / "benign_pending_review"
    pending_dir.mkdir()
    (pending_dir / "ignored.md").write_text("This should be ignored")
    
    # Create a valid file
    (tmp_path / "valid.md").write_text("This should be included")
    
    buffer_bundle, manifest = flatten_bundle(tmp_path)
    
    assert manifest.member_count == 1
    assert "ignored.md" not in buffer_bundle
    assert "valid.md" in buffer_bundle
