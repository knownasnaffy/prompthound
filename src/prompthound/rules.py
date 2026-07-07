import re

RULES = [
    {
        "name": "pipe_to_shell",
        "pattern": re.compile(r"(curl|wget).*\|\s*(bash|sh|zsh)", re.IGNORECASE),
        "severity": "high",
    },
    {
        "name": "reverse_shell",
        "pattern": re.compile(r"(nc\s+-e|/dev/tcp/|bash\s+-i\s+>\&)", re.IGNORECASE),
        "severity": "high",
    },
    {
        "name": "dangerous_exec",
        "pattern": re.compile(r"\b(eval|exec|os\.system|subprocess\.Popen)\s*\("),
        "severity": "medium",
    },
    {
        "name": "base64_blob",
        "pattern": re.compile(
            r"(?:[A-Za-z0-9+/]{4}){10,}(?:[A-Za-z0-9+/]{2}==|[A-Za-z0-9+/]{3}=)?"
        ),
        "severity": "medium",
    },
    {
        "name": "hex_blob",
        "pattern": re.compile(r"\\x[0-9a-fA-F]{2}\\x[0-9a-fA-F]{2}\\x[0-9a-fA-F]{2}"),
        "severity": "medium",
    },
    {
        "name": "unicode_tag",
        "pattern": re.compile(r"[\U000E0000-\U000E007F]"),
        "severity": "high",
    },
]


def scan_rules(buffer_lines):
    hits = []
    for i, line in enumerate(buffer_lines):
        for rule in RULES:
            for match in rule["pattern"].finditer(line):
                hits.append(
                    {
                        "rule": rule["name"],
                        "severity": rule["severity"],
                        "line_idx": i,
                        "match": match.group(0),
                    }
                )
    return hits
