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
        from rich.table import Table
        from rich.console import Group
        from rich.panel import Panel

        classification = result["classification"]["class"].upper()
        class_color = (
            "green"
            if classification == "SAFE"
            else "yellow" if classification == "SUSPICIOUS" else "red"
        )

        probs = result["classification"]["probabilities"]

        # summary table
        summary_table = Table(show_header=True, header_style="bold magenta")
        summary_table.add_column("Classification", style=f"bold {class_color}")
        summary_table.add_column("Safe Confidence", justify="right")
        summary_table.add_column("Suspicious Confidence", justify="right")
        summary_table.add_column("Malicious Confidence", justify="right")
        summary_table.add_row(
            classification,
            f"{probs['safe']:.2f}",
            f"{probs['suspicious']:.2f}",
            f"{probs['malicious']:.2f}",
        )

        # Rules table
        rules_table = Table(
            title="Rule Hits",
            show_header=True,
            header_style="bold magenta",
            title_style="bold cyan",
        )
        rules_table.add_column("Severity")
        rules_table.add_column("Rule")
        rules_table.add_column("Location")

        if result["rule_hits"]:
            for hit in result["rule_hits"]:
                sev = hit["severity"].upper()
                sev_color = "red" if sev == "HIGH" else "yellow"
                filepath, orig_line = manifest.get_source(hit["line_idx"])
                rules_table.add_row(
                    f"[{sev_color}]{sev}[/]", hit["rule"], f"{filepath}:{orig_line}"
                )
        else:
            rules_table.add_row("[green]NONE[/]", "-", "-")

        # Chains table
        chains_table = Table(
            title="Capability Chains",
            show_header=True,
            header_style="bold magenta",
            title_style="bold cyan",
        )
        chains_table.add_column("Severity")
        chains_table.add_column("Name")
        chains_table.add_column("Description")

        if result["chains_found"]:
            for chain in result["chains_found"]:
                sev = chain["severity"].upper()
                sev_color = "red" if sev == "HIGH" else "yellow"
                chains_table.add_row(
                    f"[{sev_color}]{sev}[/]", chain["name"], chain["description"]
                )
        else:
            chains_table.add_row("[green]NONE[/]", "-", "-")

        return Panel(Group(summary_table, rules_table, chains_table), expand=False)
