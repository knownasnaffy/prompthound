from .parser import parse_buffer
from .rules import scan_rules
from .features import extract_features
from .classifier import score_features
from .capability_chain import check_chains

def run_pipeline(buffer_text, manifest, is_bundle):
    frontmatter, code_blocks, lines = parse_buffer(buffer_text)
    
    rule_hits = scan_rules(lines)
    
    chains_found, mismatch_score = check_chains(lines, frontmatter)
    
    feature_dict = extract_features(lines, manifest, is_bundle)
    feature_dict['capability_mismatch_score'] = mismatch_score
    
    classification = score_features(feature_dict)
    
    return {
        'frontmatter': frontmatter,
        'rule_hits': rule_hits,
        'chains_found': chains_found,
        'features': feature_dict,
        'classification': classification
    }
