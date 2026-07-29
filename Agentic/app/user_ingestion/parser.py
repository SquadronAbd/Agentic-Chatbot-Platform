from pathlib import Path

from langchain_core.documents import Document
from langchain_community.document_loaders import (
    PyPDFLoader,
    TextLoader,
    UnstructuredMarkdownLoader,
)


class DocumentParser:
    """
    Parses uploaded user documents into LangChain Documents.

    Supported formats:
        - PDF
        - Markdown
        - TXT
    """

    SUPPORTED_EXTENSIONS = {
        ".pdf",
        ".md",
        ".txt",
    }

    def validate(self, file_path: str) -> Path:
        """
        Validate the uploaded file.
        """

        path = Path(file_path)

        if not path.exists():
            raise FileNotFoundError(f"{file_path} does not exist.")

        if path.suffix.lower() not in self.SUPPORTED_EXTENSIONS:
            raise ValueError(
                f"Unsupported file type: {path.suffix}"
            )

        return path

    def parse(self, file_path: str) -> list[Document]:
        """
        Parse a document into LangChain Documents.
        """

        path = self.validate(file_path)

        suffix = path.suffix.lower()

        if suffix == ".pdf":
            loader = PyPDFLoader(str(path))

        elif suffix == ".txt":
            loader = TextLoader(
                str(path),
                encoding="utf-8",
            )

        elif suffix == ".md":
            loader = UnstructuredMarkdownLoader(
                str(path)
            )

        else:
            raise ValueError(
                f"Unsupported file type: {suffix}"
            )

        documents = loader.load()

        # Attach metadata
        for document in documents:

            document.metadata.update(
                {
                    "source": path.name,
                    "file_path": str(path),
                    "file_type": suffix,
                }
            )

        return documents