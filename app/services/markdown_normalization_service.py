import re


class MarkdownNormalizationService:
    def normalize(self, markdown: str) -> str:
        if not markdown:
            return ""

        markdown = markdown.replace("\r\n", "\n").replace("\r", "\n")
        markdown = "\n".join(line.rstrip() for line in markdown.splitlines())
        markdown = re.sub(r"\n{4,}", "\n\n\n", markdown)
        markdown = re.sub(r"[ \t]{3,}", "  ", markdown)

        return markdown.strip()
