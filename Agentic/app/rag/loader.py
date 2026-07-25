from pathlib import Path

from langchain_community.document_loaders import (
    TextLoader,
    PyPDFLoader,
)


class DocumentLoader:
    """
    Loads supported document types.
    Markdown files are treated as plain UTF-8 text.
    """

    def load(self, filepath: str):

        path = Path(filepath)
        suffix = path.suffix.lower()

        if suffix in [".txt", ".md"]:
            loader = TextLoader(filepath, encoding="utf-8")

        elif suffix == ".pdf":
            loader = PyPDFLoader(filepath)

        else:
            raise ValueError(
                f"Unsupported file type: {suffix}"
            )

        return loader.load()