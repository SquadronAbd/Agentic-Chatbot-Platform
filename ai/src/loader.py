from pathlib import Path


def iter_markdown_files(data_dir="data/markdowns"):
    """
    Iterate through all markdown files one at a time.
    """

    markdown_dir = Path(data_dir)

    if not markdown_dir.exists():
        raise FileNotFoundError(f"{markdown_dir} does not exist")

    for md_file in sorted(markdown_dir.glob("*.md")):

        yield {
            "filename": md_file.name,
            "filepath": md_file,
            "content": md_file.read_text(
                encoding="utf-8",
                errors="ignore"
            )
        }