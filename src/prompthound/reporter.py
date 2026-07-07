import json


def format_report(result, manifest, fmt):
    if fmt == "json":
        return json.dumps(result, indent=2)
    elif fmt == "sarif":
        sarif = {
            "$schema": "https://raw.githubusercontent.com/oasis-tcs/sarif-spec/master/Schemata/sarif-schema-2.1.0.json",
            "version": "2.1.0",
            "runs": [{"tool": {"driver": {"name": "PromptHound"}}, "results": []}],
        }

        for hit in result.get("rule_hits", []):
            filepath, orig_line = manifest.get_source(hit["line_idx"])
            # Line is 0-indexed in our system, SARIF uses 1-indexed
            lineno = (orig_line or 0) + 1

            sarif["runs"][0]["results"].append(
                {
                    "ruleId": hit["rule"],
                    "level": "error" if hit["severity"] == "high" else "warning",
                    "message": {"text": f"Pattern match: {hit['match']}"},
                    "locations": [
                        {
                            "physicalLocation": {
                                "artifactLocation": {"uri": filepath or "unknown"},
                                "region": {"startLine": lineno},
                            }
                        }
                    ],
                }
            )

        return json.dumps(sarif, indent=2)
    else:  # human
        report = []
        report.append("=== PromptHound Risk Report ===")
        report.append(f"Classification: {result['classification']['class'].upper()}")
        probs = result["classification"]["probabilities"]
        report.append(
            f"Confidence: Safe {probs['safe']:.2f}, Suspicious {probs['suspicious']:.2f}, Malicious {probs['malicious']:.2f}"
        )

        report.append("\n-- Rule Hits --")
        if result["rule_hits"]:
            for hit in result["rule_hits"]:
                filepath, orig_line = manifest.get_source(hit["line_idx"])
                report.append(
                    f"[{hit['severity'].upper()}] {hit['rule']} at {filepath}:{orig_line}"
                )
        else:
            report.append("None")

        report.append("\n-- Capability Chains --")
        if result["chains_found"]:
            for chain in result["chains_found"]:
                report.append(
                    f"[{chain['severity'].upper()}] {chain['name']}: {chain['description']}"
                )
        else:
            report.append("None")

        return "\n".join(report)
