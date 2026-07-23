"""
chunker.py

Hierarchical Financial Document Chunker
=======================================

Designed for enterprise annual reports.

Pipeline
--------

Markdown
    │
    ▼
MarkdownParser
    │
    ▼
Sections + Tables
    │
    ├──────────────┐
    ▼              ▼
Narrative      Markdown Tables
    │              │
    ▼              ▼
Financial Paragraph Splitter
    │
    ▼
Semantic Grouper
    │
    ▼
Merge Tiny Chunks
    │
    ▼
Recursive Splitter
    │
    ▼
Chunk Objects
    │
    ▼
SentenceTransformer Embeddings
    │
    ▼
PostgreSQL + pgvector

Author:
Enterprise RAG Project
"""

from __future__ import annotations

import logging
import re
import uuid

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from langchain_text_splitters import RecursiveCharacterTextSplitter

from sentence_transformers import SentenceTransformer
from sentence_transformers.util import cos_sim


###############################################################################
# Logging
###############################################################################

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s"
)

logger = logging.getLogger(__name__)

###############################################################################
# Configuration
###############################################################################

@dataclass
class ChunkingConfig:
    """
    Global configuration for the chunker.
    """

    embedding_model: str = (
        "sentence-transformers/all-MiniLM-L6-v2"
    )

    similarity_threshold: float = 0.72

    chunk_size: int = 800

    chunk_overlap: int = 80

    minimum_chunk_size: int = 150

    maximum_chunk_size: int = 1200

    normalize_embeddings: bool = True

    recursive_separators: List[str] = field(
        default_factory=lambda: [

            "\n\n",

            "\n",

            ". ",

            "; ",

            ", ",

            " ",

            ""

        ]
    )

###############################################################################
# Parent Document
###############################################################################

@dataclass
class ParentDocument:

    parent_id: str

    filename: str

    heading: str

    heading_level: Optional[int]

    text: str

###############################################################################
# Chunk
###############################################################################

@dataclass
class Chunk:

    id: str

    parent_id: str

    filename: str

    chunk_type: str

    heading: str

    heading_level: Optional[int]

    chunk_order: str

    text: str

    embedding_text: str

    metadata: Dict[str, Any] = field(
        default_factory=dict
    )

###############################################################################
# Metadata Builder
###############################################################################

class MetadataBuilder:

    def __init__(self):

        self.extractor = FinancialMetadataExtractor()

    def build(

        self,

        *,

        filename,

        heading,

        heading_level,

        chunk_type,

        chunk_order,

        company_name=None,

        fiscal_year=None,

        page_number=None,

        text="",

    ) -> ChunkMetadata:

        metadata = ChunkMetadata(

            filename=filename,

            company_name=company_name,

            fiscal_year=fiscal_year,

            heading=heading,

            heading_level=heading_level,

            page_number=page_number,

            chunk_type=chunk_type,

            chunk_order=str(chunk_order),

        )

        metadata = self.extractor.extract(

            text,

            metadata,

        )

        return metadata

###############################################################################
# Chunk Builder
###############################################################################

class ChunkBuilder:

    def __init__(self):

        self.metadata_builder = MetadataBuilder()

    def build_chunk(

        self,

        *,

        filename,

        parent_id,

        heading,

        heading_level,

        chunk_type,

        chunk_order,

        text,

        embedding_text,

        company_name=None,

        fiscal_year=None,

        page_number=None,

    ):

        metadata = self.metadata_builder.build(

            filename=filename,

            heading=heading,

            heading_level=heading_level,

            chunk_type=chunk_type,

            chunk_order=str(chunk_order),

            company_name=company_name,

            fiscal_year=fiscal_year,

            page_number=page_number,

            text=text,

        )

        return Chunk(

            id=str(uuid.uuid4()),

            parent_id=parent_id,

            filename=filename,

            chunk_type=chunk_type,

            heading=heading,

            heading_level=heading_level,

            chunk_order=str(chunk_order),

            text=text,

            embedding_text=embedding_text,

            metadata=metadata,

        )
###############################################################################
# Embedding Manager
###############################################################################

class EmbeddingManager:
    """
    Wrapper around SentenceTransformer.
    """

    def __init__(self, config: ChunkingConfig):

        logger.info(
            "Loading embedding model..."
        )

        self.model = SentenceTransformer(
            config.embedding_model
        )

        self.normalize = (
            config.normalize_embeddings
        )

    def encode(
        self,
        texts: List[str]
    ):

        return self.model.encode(

            texts,

            normalize_embeddings=self.normalize,

            convert_to_tensor=True,

        )

    @staticmethod
    def similarity(
        embedding1,
        embedding2,
    ) -> float:

        return cos_sim(
            embedding1,
            embedding2,
        ).item()

###############################################################################
# Base Chunker
###############################################################################

class BaseChunker:

    def __init__(

        self,

        config: ChunkingConfig,

    ):

        self.config = config

        self.builder = ChunkBuilder()

        self.embedding_manager = EmbeddingManager(

            config

        )

        self.paragraph_splitter = (

            FinancialParagraphSplitter()

        )

        self.recursive_splitter = (

            RecursiveCharacterTextSplitter(

                chunk_size=config.chunk_size,

                chunk_overlap=config.chunk_overlap,

                separators=config.recursive_separators,

            )

        )
###############################################################################
# Chunk Metadata
###############################################################################

@dataclass
class ChunkMetadata:
    """
    Rich metadata associated with every chunk.

    This metadata supports:
    - Metadata filtering in pgvector
    - Hybrid retrieval
    - RAG evaluation
    - Analytics
    """

    filename: str

    company_name: Optional[str]

    fiscal_year: Optional[int]

    heading: str

    heading_level: Optional[int]

    page_number: Optional[int]

    chunk_type: str

    chunk_order: str

    contains_table: bool = False

    contains_currency: bool = False

    contains_percentage: bool = False

    contains_date: bool = False

    contains_note_reference: bool = False

    contains_ifrs: bool = False

    contains_gaap: bool = False

    keywords: List[str] = field(
        default_factory=list
    )

###############################################################################
# Financial Metadata Extractor
###############################################################################

class FinancialMetadataExtractor:
    """
    Detect financial-specific signals inside each chunk.
    """

    CURRENCY_PATTERN = re.compile(

        r"\$[\d,]+(?:\.\d+)?"

    )

    PERCENT_PATTERN = re.compile(

        r"\d+(?:\.\d+)?%"

    )

    YEAR_PATTERN = re.compile(

        r"\b(19|20)\d{2}\b"

    )

    NOTE_PATTERN = re.compile(

        r"\bNote\s+\d+\b",

        re.IGNORECASE

    )

    IFRS_PATTERN = re.compile(

        r"\bIFRS\b",

        re.IGNORECASE

    )

    GAAP_PATTERN = re.compile(

        r"\bGAAP\b",

        re.IGNORECASE

    )

    KEYWORD_PATTERN = re.compile(

        r"[A-Za-z]{5,}"

    )

    def extract(

        self,

        text: str,

        metadata: ChunkMetadata,

    ) -> ChunkMetadata:

        metadata.contains_currency = bool(

            self.CURRENCY_PATTERN.search(text)

        )

        metadata.contains_percentage = bool(

            self.PERCENT_PATTERN.search(text)

        )

        metadata.contains_date = bool(

            self.YEAR_PATTERN.search(text)

        )

        metadata.contains_note_reference = bool(

            self.NOTE_PATTERN.search(text)

        )

        metadata.contains_ifrs = bool(

            self.IFRS_PATTERN.search(text)

        )

        metadata.contains_gaap = bool(

            self.GAAP_PATTERN.search(text)

        )

        words = self.KEYWORD_PATTERN.findall(text.lower())

        metadata.keywords = sorted(

            set(words)

        )[:30]

        return metadata

###############################################################################
# Financial Paragraph Splitter
###############################################################################

class FinancialParagraphSplitter:
    """
    Splits a markdown section into semantic units while preserving
    the structure of financial reports.
    """

    BULLET_PATTERN = re.compile(

        r"^(\*|-|\+)\s+"

    )

    NUMBER_PATTERN = re.compile(

        r"^\d+\."

    )

    def split(

        self,

        text: str,

    ) -> List[str]:

        units = []

        current = []

        for line in text.splitlines():

            stripped = line.strip()

            ############################################################

            if stripped == "":

                if current:

                    units.append(

                        "\n".join(current).strip()

                    )

                    current = []

                continue

            ############################################################

            if self.BULLET_PATTERN.match(stripped):

                current.append(line)

                continue

            ############################################################

            if self.NUMBER_PATTERN.match(stripped):

                current.append(line)

                continue

            ############################################################

            if stripped.startswith(">"):

                current.append(line)

                continue

            ############################################################

            current.append(line)

        if current:

            units.append(

                "\n".join(current).strip()

            )

        return units

###############################################################################
# Semantic Chunker
###############################################################################

class SemanticChunker(BaseChunker):
    """
    Hierarchical semantic chunker.

    Workflow

    Markdown Section

            │

            ▼

    Paragraph Splitter

            │

            ▼

    Semantic Units

            │

            ▼

    SentenceTransformer

            │

            ▼

    Running Centroid Similarity

            │

            ▼

    Semantic Chunks

            │

            ▼

    Merge Small Chunks

            │

            ▼

    Recursive Splitter (if needed)

            │

            ▼

    Final Chunks
    """

    def __init__(

        self,

        config: ChunkingConfig = ChunkingConfig()

    ):

        super().__init__(config)

        ###########################################################################
    # Running Centroid
    ###########################################################################

    @staticmethod
    def centroid(embeddings):

        return embeddings.mean(dim=0)

        ###########################################################################
    # Similarity
    ###########################################################################

    def should_merge(

        self,

        centroid,

        new_embedding,

        text,

    ):

        similarity = self.embedding_manager.similarity(

            centroid,

            new_embedding,

        )

        threshold = self.dynamic_threshold(

            text

        )

        return similarity >= threshold
        ###########################################################################
    # Merge Semantic Units
    ###########################################################################

    def semantic_group(

        self,

        units,

    ):

        if len(units) == 0:

            return []

        if len(units) == 1:

            return [

                "\n\n".join(units)

            ]

        embeddings = self.embedding_manager.encode(

            units

        )

        groups = []

        current_text = [

            units[0]

        ]

        current_embeddings = [

            embeddings[0]

        ]

        ##############################################################

        for i in range(

            1,

            len(units)

        ):

            centroid = self.centroid(

                current_embeddings

            )

            if self.should_merge(

                centroid,

                embeddings[i],

                units[i],

            ):

                current_text.append(

                    units[i]

                )

                current_embeddings.append(

                    embeddings[i]

                )

            else:

                groups.append(

                    "\n\n".join(

                        current_text

                    )

                )

                current_text = [

                    units[i]

                ]

                current_embeddings = [

                    embeddings[i]

                ]

        ##############################################################

        groups.append(

            "\n\n".join(

                current_text

            )

        )

        return groups
###########################################################################
# Smart Merge Small Chunks
###########################################################################

    def merge_small_chunks(
        self,
        groups,
    ):

        if len(groups) <= 1:
            return groups

        embeddings = self.embedding_manager.encode(groups)

        merged = []
        used = set()

        for i in range(len(groups)):

            if i in used:
                continue

            current = groups[i]

            if len(current) >= self.config.minimum_chunk_size:
                merged.append(current)
                continue

            prev_sim = -1
            next_sim = -1

            if i > 0:
                prev_sim = self.embedding_manager.similarity(
                    embeddings[i],
                    embeddings[i - 1],
                )

            if i < len(groups) - 1:
                next_sim = self.embedding_manager.similarity(
                    embeddings[i],
                    embeddings[i + 1],
                )

            if next_sim >= prev_sim and i < len(groups) - 1:

                merged.append(
                    current + "\n\n" + groups[i + 1]
                )

                used.add(i + 1)

            elif i > 0:

                merged[-1] += "\n\n" + current

            else:

                merged.append(current)

        return merged


###########################################################################
# Recursive Split
############################################################################

    def recursive_split(

        self,

        text,

    ):

        if len(text) <= self.config.maximum_chunk_size:

            return [

                text

            ]

        return self.recursive_splitter.split_text(

            text

        )

        ###########################################################################
    # Build Chunk Objects
    ###########################################################################

    def build_chunks(

        self,

        filename,

        parent_id,

        heading,

        heading_level,

        text_groups,

        company_name=None,

        fiscal_year=None,

    ):

        chunks = []

        order = 0

        for group in text_groups:

            pieces = self.recursive_split(

                group

            )

            for piece in pieces:

                chunk = self.builder.build_chunk(

                    filename=filename,

                    parent_id=parent_id,

                    heading=heading,

                    heading_level=heading_level,

                    chunk_type="narrative",

                    chunk_order=order,

                    text=piece,

                    embedding_text=piece,

                    company_name=company_name,

                    fiscal_year=fiscal_year,

                )

                chunks.append(

                    chunk

                )

                order += 1

        return chunks

        ###########################################################################
    # Chunk One Section
    ###########################################################################

    def chunk_section(

        self,

        filename,

        section,

        parent_id,

        company_name=None,

        fiscal_year=None,

    ):

        units = self.paragraph_splitter.split(

            section.content

        )

        groups = self.semantic_group(

            units

        )

        groups = self.merge_small_chunks(

            groups

        )

        return self.build_chunks(

            filename,

            parent_id,

            section.heading,

            section.level,

            groups,

            company_name,

            fiscal_year,

        )

###############################################################################
# Table Chunker
###############################################################################

class TableChunker:
    """
    Handles markdown tables.

    Tables are stored whole.

    Later an LLM summary can replace embedding_text.
    """

    def __init__(self):

        self.builder = ChunkBuilder()

    def chunk_tables(

        self,

        filename,

        tables,

        company_name=None,

        fiscal_year=None,

    ):

        chunks = []

        parents = []

        for index, table in enumerate(tables):

            parent_id = str(uuid.uuid4())

            parent = ParentDocument(

                parent_id=parent_id,

                filename=filename,

                heading=table.heading,

                heading_level=None,

                text=table.markdown,

            )

            parents.append(parent)

            chunk = self.builder.build_chunk(

                filename=filename,

                parent_id=parent_id,

                heading=table.heading,

                heading_level=None,

                chunk_type="table",

                chunk_order=index,

                text=table.markdown,

                embedding_text=table.markdown,

                company_name=company_name,

                fiscal_year=fiscal_year,

            )

            chunk.metadata.contains_table = True

            chunks.append(chunk)

        return parents, chunks
###############################################################################
# Complete Document
###############################################################################

    def chunk_document(

        self,

        filename,

        sections,

        tables,

        company_name=None,

        fiscal_year=None,

    ):

        parent_documents = []

        child_chunks = []

        ##############################################################
        # Narrative Sections
        ##############################################################

        for section in sections:

            parent_id = str(uuid.uuid4())

            parent = ParentDocument(

                parent_id=parent_id,

                filename=filename,

                heading=section.heading,

                heading_level=section.level,

                text=section.content,

            )

            parent_documents.append(parent)

            chunks = self.chunk_section(

                filename,

                section,

                parent_id,

                company_name,

                fiscal_year,

            )

            child_chunks.extend(chunks)

        ##############################################################
        # Tables
        ##############################################################

        table_chunker = TableChunker()

        table_parents, table_chunks = (

            table_chunker.chunk_tables(

                filename,

                tables,

                company_name,

                fiscal_year,

            )

        )

        parent_documents.extend(table_parents)

        child_chunks.extend(table_chunks)

        logger.info(

            "%s → %d parents | %d child chunks",

            filename,

            len(parent_documents),

            len(child_chunks),

        )

        return parent_documents, child_chunks

    ###############################################################################
# Utilities
###############################################################################

def parent_to_dict(parent: ParentDocument):

    return {

        "parent_id": parent.parent_id,

        "filename": parent.filename,

        "heading": parent.heading,

        "heading_level": parent.heading_level,

        "text": parent.text,

    }


def chunk_to_dict(chunk: Chunk):

    metadata = vars(chunk.metadata)

    return {

        "id": chunk.id,

        "parent_id": chunk.parent_id,

        "filename": chunk.filename,

        "chunk_type": chunk.chunk_type,

        "heading": chunk.heading,

        "heading_level": chunk.heading_level,

        "chunk_order": chunk.chunk_order,

        "text": chunk.text,

        "embedding_text": chunk.embedding_text,

        "metadata": metadata,

    }

###############################################################################
# Example
###############################################################################

if __name__ == "__main__":

    from markdown_parser import MarkdownParser
    from loader import iter_markdown_files

    parser = MarkdownParser()

    chunker = SemanticChunker()

    for document in iter_markdown_files("data/markdowns"):

        sections, tables = parser.parse(
            document["content"]
        )

        parents, chunks = chunker.chunk_document(

            filename=document["filename"],

            sections=sections,

            tables=tables,

        )

        print("=" * 80)

        print(document["filename"])

        print(f"Parents : {len(parents)}")

        print(f"Chunks  : {len(chunks)}")