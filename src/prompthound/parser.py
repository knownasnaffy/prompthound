import yaml


class NoAliasSafeLoader(yaml.SafeLoader):
    def compose_node(self, parent, index):
        if self.check_event(yaml.events.AliasEvent):
            raise yaml.YAMLError("Aliases are not allowed (DoS protection)")
        return super().compose_node(parent, index)


def parse_buffer(buffer_text):
    """
    Splits buffer into frontmatter, prose, and code blocks.
    Extracts the first valid YAML frontmatter block.
    """
    frontmatter = {}
    lines = buffer_text.split("\n")

    in_frontmatter = False
    fm_lines = []

    for i, line in enumerate(lines):
        if line.strip() == "---":
            if not in_frontmatter:
                # Check if it's start of file or right after a BEGIN MEMBER fence
                if i == 0 or (i > 0 and lines[i - 1].startswith("--- BEGIN MEMBER")):
                    in_frontmatter = True
                    continue
            else:
                in_frontmatter = False
                try:
                    parsed = yaml.load("\n".join(fm_lines), Loader=NoAliasSafeLoader)
                    if isinstance(parsed, dict):
                        frontmatter = parsed
                        break
                except yaml.YAMLError:
                    pass
                fm_lines = []
                continue

        if in_frontmatter:
            fm_lines.append(line)

    # Extract code blocks
    code_blocks = []
    in_code = False
    current_code = []

    for line in lines:
        if line.startswith("```"):
            if not in_code:
                in_code = True
            else:
                in_code = False
                code_blocks.append("\n".join(current_code))
                current_code = []
        elif in_code:
            current_code.append(line)

    return frontmatter, code_blocks, lines
