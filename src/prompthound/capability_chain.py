import re


def check_chains(buffer_lines, frontmatter):
    """
    Checks for sequences like read -> encode -> network send.
    """
    chains_found = []

    has_read = False
    has_encode = False
    has_network = False

    read_pattern = re.compile(r"\b(read|cat)\b|open\(")
    encode_pattern = re.compile(r"\b(base64)\b|hex\(")
    network_pattern = re.compile(r"\b(curl|wget)\b|requests\.post")

    for line in buffer_lines:
        line_lower = line.lower()

        if read_pattern.search(line_lower):
            has_read = True

        if encode_pattern.search(line_lower):
            has_encode = True

        if network_pattern.search(line_lower):
            has_network = True

    if has_read and has_encode and has_network:
        chains_found.append(
            {
                "name": "read_encode_send",
                "severity": "high",
                "description": "File read -> encode -> network send sequence detected.",
            }
        )

    declared_caps = frontmatter.get("capabilities", [])
    mismatch_score = 0.0

    if has_network and "network" not in declared_caps:
        mismatch_score += 1.0

    return chains_found, mismatch_score
