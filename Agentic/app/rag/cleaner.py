import re
from langchain_core.documents import Document


# Matches a markdown table block: one or more lines starting with |
_TABLE_BLOCK = re.compile(r"(\|.+\|[ \t]*\n)+", re.MULTILINE)

# Matches runs of whitespace that are NOT newlines (for safe space normalization)
_INLINE_SPACES = re.compile(r"[^\S\n]+")

# Matches more than two consecutive newlines
_EXCESS_NEWLINES = re.compile(r"\n{3,}")


class DocumentCleaner:
    """
    Cleans raw document text before chunking while preserving:
    - Markdown table structure (pipes, alignment rows, cell spacing)
    - Section heading newlines used by the chunker's separator list
    - Paragraph boundaries
    """

    @staticmethod
    def _clean_text(text: str) -> str:
        # Extract table blocks and replace with placeholders so we don't
        # touch their internal whitespace during normalization.
        placeholders: list[str] = []

        def stash_table(match: re.Match) -> str:
            placeholders.append(match.group(0))
            return f"\x00TABLE{len(placeholders) - 1}\x00"

        text = _TABLE_BLOCK.sub(stash_table, text)

        # Normalize inline whitespace (spaces/tabs) without touching newlines
        text = _INLINE_SPACES.sub(" ", text)

        # Collapse excessive blank lines to a single blank line
        text = _EXCESS_NEWLINES.sub("\n\n", text)

        # Restore table blocks verbatim
        for idx, table in enumerate(placeholders):
            text = text.replace(f"\x00TABLE{idx}\x00", table)

        return text.strip()

    @staticmethod
    def clean(documents: list[Document]) -> list[Document]:
        return [
            Document(
                page_content=DocumentCleaner._clean_text(doc.page_content),
                metadata=doc.metadata,
            )
            for doc in documents
        ]
