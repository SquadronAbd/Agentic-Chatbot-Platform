import re
from langchain_core.documents import Document
from langchain_text_splitters import MarkdownHeaderTextSplitter, RecursiveCharacterTextSplitter


# Headers used to split the document into sections first
_HEADER_SPLITS = [
    ("#", "h1"),
    ("##", "h2"),
    ("###", "h3"),
]

# Matches a complete markdown table block (header + separator + rows)
_TABLE_BLOCK = re.compile(r"(\|.+\|[ \t]*\n)+", re.MULTILINE)

_CHUNK_SIZE = 1000
_CHUNK_OVERLAP = 150
_MIN_CHUNK_CHARS = 60  # discard chunks shorter than this — usually noise

# Splitter for non-table prose within a section.
# Sentence-boundary separators (". ", "? ", "! ") come before word breaks
# so chunks end at natural sentence boundaries whenever possible.
_PROSE_SPLITTER = RecursiveCharacterTextSplitter(
    chunk_size=_CHUNK_SIZE,
    chunk_overlap=_CHUNK_OVERLAP,
    separators=["\n\n", "\n", ". ", "? ", "! ", " ", ""],
)


def _section_to_chunks(text: str, metadata: dict) -> list[Document]:
    """
    Splits one markdown section into chunks.

    Tables are treated as atomic units — they are never split mid-row.
    If a table exceeds CHUNK_SIZE it is kept whole rather than broken,
    because splitting a table row destroys the data.  Prose between
    tables is split normally by the recursive splitter.
    """
    chunks: list[Document] = []
    last_end = 0

    for match in _TABLE_BLOCK.finditer(text):
        # Prose before this table
        prose = text[last_end : match.start()].strip()
        if prose:
            for chunk in _PROSE_SPLITTER.create_documents([prose], metadatas=[metadata]):
                chunks.append(chunk)

        # Table kept whole — never split mid-row
        table_text = match.group(0).strip()
        if table_text:
            chunks.append(Document(page_content=table_text, metadata=metadata))

        last_end = match.end()

    # Remaining prose after the last table
    tail = text[last_end:].strip()
    if tail:
        for chunk in _PROSE_SPLITTER.create_documents([tail], metadatas=[metadata]):
            chunks.append(chunk)

    return chunks


class DocumentChunker:
    """
    Two-pass markdown and table-aware chunker.

    Pass 1 — MarkdownHeaderTextSplitter splits the document into logical
              sections at #, ##, ### boundaries, carrying header metadata
              into each section.

    Pass 2 — Each section is further split into prose chunks, but markdown
              tables within the section are extracted as atomic chunks first
              so no table row is ever cut across a chunk boundary.
    """

    def __init__(self) -> None:
        self._header_splitter = MarkdownHeaderTextSplitter(
            headers_to_split_on=_HEADER_SPLITS,
            strip_headers=False,
        )

    def chunk(self, documents: list[Document]) -> list[Document]:
        all_chunks: list[Document] = []

        for doc in documents:
            # page_number comes from PyPDFLoader as "page" (0-indexed); normalise it
            page_number = doc.metadata.get("page")
            if page_number is not None:
                page_number = int(page_number) + 1  # convert to 1-indexed

            content = doc.page_content

            # Adaptive short-page bypass: if a PDF page (or any document) is already
            # well under the chunk size, keep it whole instead of splitting needlessly.
            if len(content) <= _CHUNK_SIZE and page_number is not None:
                merged_metadata = {**doc.metadata, "page_number": page_number}
                if len(content.strip()) >= _MIN_CHUNK_CHARS:
                    all_chunks.append(Document(page_content=content, metadata=merged_metadata))
                continue

            # Pass 1: split by markdown headers into sections
            try:
                sections = self._header_splitter.split_text(content)
            except Exception:
                # Fallback for non-markdown or malformed content
                sections = [Document(page_content=content, metadata={})]

            for section in sections:
                # Merge file-level metadata with header-level metadata
                merged_metadata = {**doc.metadata, **section.metadata}
                if page_number is not None:
                    merged_metadata["page_number"] = page_number
                section_chunks = _section_to_chunks(section.page_content, merged_metadata)
                # Drop noise chunks (very short fragments that carry no signal)
                all_chunks.extend(
                    c for c in section_chunks if len(c.page_content.strip()) >= _MIN_CHUNK_CHARS
                )

        # Stamp each chunk with its global position across the whole document set
        for idx, chunk in enumerate(all_chunks):
            chunk.metadata["chunk_index"] = idx

        return all_chunks
