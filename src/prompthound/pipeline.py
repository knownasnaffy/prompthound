from .parser import parse_buffer
from .rules import scan_rules
from .features import extract_features
from .classifier import score_features
from .capability_chain import check_chains


def run_pipeline(buffer_text, manifest, is_bundle, frontmatter_absent=False):
    """Run the full analysis pipeline on a flattened buffer.

    Args:
        buffer_text: Flattened text content (output of flatten_single / flatten_bundle).
        manifest:    SourceSpan instance mapping buffer lines back to source files.
        is_bundle:   True when the input was flattened from a multi-file bundle.
        frontmatter_absent: True when the input has no YAML frontmatter (e.g. an
            AGENTS.md-anchored bundle or a "no anchor" flat upload via the web UI).
            When True, frontmatter={} and capability_mismatch_score=0.0 are used.
            NOTE: This code path did NOT exist in the original spec, which assumed
            parse_buffer() always finds an anchor with YAML frontmatter. The
            frontmatter_absent feature flag is extracted but EXCLUDED from the
            classifier X vector until the model is retrained (see FIXME below).
            Documented in concept.md TODO — treat with same review rigor as the
            AGENTS.md anchor-set expansion task (task A).
    """
    frontmatter, code_blocks, lines = parse_buffer(buffer_text)

    # If caller signals no-anchor input, override whatever parse_buffer found
    # (it will have returned {} anyway, but this makes the branch explicit).
    if frontmatter_absent:
        frontmatter = {}

    rule_hits = scan_rules(lines)

    chains_found, mismatch_score = check_chains(lines, frontmatter)
    if frontmatter_absent:
        mismatch_score = (
            0.0  # Undefined, not "perfect match" — see frontmatter_absent flag
        )

    feature_dict = extract_features(lines, manifest, is_bundle)
    feature_dict["capability_mismatch_score"] = mismatch_score

    # FIXME: frontmatter_absent is extracted here but intentionally NOT passed to
    # score_features() / the classifier X vector. The current trained model does not
    # include this feature — adding it would break inference (RF is strict on feature
    # count). Unblock: retrain model with frontmatter_absent in the feature set.
    # Retrain itself is blocked on completion of the 301-file human review in
    # dataset/pending_review/ (open task, unresolved as of 2026-07-07).
    feature_dict["frontmatter_absent"] = 1 if frontmatter_absent else 0

    classification = score_features(feature_dict)

    return {
        "frontmatter": frontmatter,
        "frontmatter_absent": frontmatter_absent,
        "rule_hits": rule_hits,
        "chains_found": chains_found,
        "features": feature_dict,
        "classification": classification,
    }
