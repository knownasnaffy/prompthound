def check_chains(buffer_lines, frontmatter):
    """
    Checks for sequences like read -> encode -> network send.
    """
    chains_found = []
    
    has_read = False
    has_encode = False
    has_network = False
    
    for line in buffer_lines:
        line_lower = line.lower()
        
        if 'read' in line_lower or 'cat ' in line_lower or 'open(' in line_lower:
            has_read = True
        
        if 'base64' in line_lower or 'hex(' in line_lower:
            has_encode = True
            
        if 'curl' in line_lower or 'wget' in line_lower or 'requests.post' in line_lower:
            has_network = True
            
    if has_read and has_encode and has_network:
        chains_found.append({
            'name': 'read_encode_send',
            'severity': 'high',
            'description': 'File read -> encode -> network send sequence detected.'
        })
        
    declared_caps = frontmatter.get('capabilities', [])
    mismatch_score = 0.0
    
    if has_network and 'network' not in declared_caps:
        mismatch_score += 1.0
        
    return chains_found, mismatch_score
