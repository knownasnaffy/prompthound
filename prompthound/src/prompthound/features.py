import math
import re
from prompthound.rules import scan_rules

def compute_entropy(text):
    if not text:
        return 0
    freq = {}
    for c in text:
        freq[c] = freq.get(c, 0) + 1
    entropy = 0
    for count in freq.values():
        p = count / len(text)
        entropy -= p * math.log2(p)
    return entropy

def extract_features(buffer_lines, manifest, is_bundle):
    # Core per-document features mapped to each member
    member_features = {
        filepath: {
            'b64_ratio': 0.0,
            'padding_ratio': 0.0,
            'code_to_prose_ratio': 0.0,
            'url_count': 0,
            'unicode_count': 0,
            'shell_command_presence': 0,
            'urgency_density': 0.0,
            'entropy': 0.0,
            'text_len': 0,
            'code_len': 0,
            'high_severity_hits': 0,
            'medium_severity_hits': 0,
            'eval_exec_density': 0.0,
            'secret_keyword_density': 0.0
        }
        for _, _, filepath in manifest.ranges
    }
    
    url_pattern = re.compile(r'https?://[^\s]+')
    urgency_pattern = re.compile(r'(first and foremost|important|critical|immediately)', re.IGNORECASE)
    b64_pattern = re.compile(r'(?:[A-Za-z0-9+/]{4}){10,}(?:[A-Za-z0-9+/]{2}==|[A-Za-z0-9+/]{3}=)?')
    shell_pattern = re.compile(r'(bash|sh|curl|wget)')
    eval_exec_pattern = re.compile(r'\b(eval|exec|os\.system|subprocess)\b')
    secret_pattern = re.compile(r'(password|token|secret|id_rsa|api_key)', re.IGNORECASE)
    
    member_text_lines = {filepath: [] for _, _, filepath in manifest.ranges}
    
    in_code = False
    for i, line in enumerate(buffer_lines):
        filepath, _ = manifest.get_source(i)
        if filepath is None:
            # Handle fences
            continue
            
        feats = member_features[filepath]
        member_text_lines[filepath].append(line)
        
        feats['text_len'] += len(line)
        feats['url_count'] += len(url_pattern.findall(line))
        feats['unicode_count'] += len(re.findall(r'[\U000E0000-\U000E007F]', line))
        feats['shell_command_presence'] = max(feats['shell_command_presence'], 1 if shell_pattern.search(line) else 0)
        
        if line.startswith('```'):
            in_code = not in_code
        elif in_code:
            feats['code_len'] += len(line)
            
    # Finalize per-member ratios
    for filepath, lines in member_text_lines.items():
        text = '\n'.join(lines)
        feats = member_features[filepath]
        feats['entropy'] = compute_entropy(text)
        
        b64_len = sum(len(m) for m in b64_pattern.findall(text))
        if feats['text_len'] > 0:
            feats['b64_ratio'] = b64_len / feats['text_len']
            
        urgency_count = len(urgency_pattern.findall(text))
        if feats['text_len'] > 0:
            feats['urgency_density'] = urgency_count / (feats['text_len'] / 100.0) # per 100 chars
            
        prose_len = feats['text_len'] - feats['code_len']
        if prose_len > 0:
            feats['code_to_prose_ratio'] = feats['code_len'] / prose_len
        elif feats['code_len'] > 0:
            feats['code_to_prose_ratio'] = float('inf') # all code, no prose
            
        # Get rule hits
        hits = scan_rules(lines)
        feats['high_severity_hits'] = sum(1 for h in hits if h['severity'] == 'high')
        feats['medium_severity_hits'] = sum(1 for h in hits if h['severity'] == 'medium')
        
        # New densities
        if feats['text_len'] > 0:
            feats['eval_exec_density'] = len(eval_exec_pattern.findall(text)) / (feats['text_len'] / 100.0)
            feats['secret_keyword_density'] = len(secret_pattern.findall(text)) / (feats['text_len'] / 100.0)
            
    # Default to 0.0 if empty dictionary (shouldn't happen with valid files but safe)
    if not member_features:
        return {
            'b64_ratio': 0.0, 'padding_ratio': 0.0, 'code_to_prose_ratio': 0.0,
            'url_count': 0, 'unicode_count': 0, 'shell_command_presence': 0,
            'urgency_density': 0.0, 'entropy': 0.0,
            'is_bundle': 1 if is_bundle else 0, 'member_count': manifest.member_count,
            'capability_mismatch_score': 0.0,
            'high_severity_hits': 0, 'medium_severity_hits': 0,
            'eval_exec_density': 0.0, 'secret_keyword_density': 0.0
        }
    
    # Compute max of ratios across bundle to prevent dilution
    max_b64_ratio = max(f['b64_ratio'] for f in member_features.values())
    max_padding_ratio = max(f['padding_ratio'] for f in member_features.values())
    
    # Handling infinity in code_to_prose_ratio
    code_to_prose_vals = [f['code_to_prose_ratio'] for f in member_features.values() if f['code_to_prose_ratio'] != float('inf')]
    max_code_to_prose = max(code_to_prose_vals) if code_to_prose_vals else 100.0 # Arbitrary high number if all infinite
    
    max_urgency = max(f['urgency_density'] for f in member_features.values())
    max_entropy = max(f['entropy'] for f in member_features.values())
    max_eval_exec = max(f['eval_exec_density'] for f in member_features.values())
    max_secret = max(f['secret_keyword_density'] for f in member_features.values())
    
    # Compute sums of counts across bundle
    total_url_count = sum(f['url_count'] for f in member_features.values())
    total_unicode_count = sum(f['unicode_count'] for f in member_features.values())
    has_shell = max(f['shell_command_presence'] for f in member_features.values())
    max_high_severity = max(f['high_severity_hits'] for f in member_features.values())
    max_medium_severity = max(f['medium_severity_hits'] for f in member_features.values())
    
    return {
        'b64_ratio': max_b64_ratio,
        'padding_ratio': max_padding_ratio,
        'code_to_prose_ratio': max_code_to_prose,
        'url_count': total_url_count,
        'unicode_count': total_unicode_count,
        'shell_command_presence': has_shell,
        'urgency_density': max_urgency,
        'entropy': max_entropy,
        'is_bundle': 1 if is_bundle else 0,
        'member_count': manifest.member_count,
        'capability_mismatch_score': 0.0,
        'high_severity_hits': max_high_severity,
        'medium_severity_hits': max_medium_severity,
        'eval_exec_density': max_eval_exec,
        'secret_keyword_density': max_secret
    }
