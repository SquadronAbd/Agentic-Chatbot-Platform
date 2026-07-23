from dataclasses import dataclass
from typing import List


@dataclass
class Section:

    heading: str

    level: int

    content: str


@dataclass
class Table:

    heading: str

    markdown: str


class MarkdownParser:

    def __init__(self):

        pass

    @staticmethod
    def _is_heading(line: str):

        line = line.strip()

        if not line.startswith("#"):
            return False

        hashes = len(line) - len(line.lstrip("#"))

        return hashes, line[hashes:].strip()

    @staticmethod
    def _is_table_separator(line: str):

        line = line.strip()

        return (
            "|" in line
            and set(line.replace("|", "").replace(":", "").strip()) == {"-"}
        )

    def parse(self, markdown: str):

        lines = markdown.splitlines()

        sections = []

        tables = []

        current_heading = "Document"

        current_level = 0

        buffer = []

        i = 0

        while i < len(lines):

            line = lines[i]

            heading = self._is_heading(line)

            if heading:

                if buffer:

                    sections.append(
                        Section(
                            current_heading,
                            current_level,
                            "\n".join(buffer).strip()
                        )
                    )

                current_level, current_heading = heading

                buffer = []

                i += 1

                continue

            if (
                i + 1 < len(lines)
                and "|" in line
                and self._is_table_separator(lines[i + 1])
            ):

                table_lines = [line, lines[i + 1]]

                i += 2

                while i < len(lines):

                    if "|" not in lines[i]:
                        break

                    table_lines.append(lines[i])

                    i += 1

                tables.append(
                    Table(
                        heading=current_heading,
                        markdown="\n".join(table_lines)
                    )
                )

                continue

            buffer.append(line)

            i += 1

        if buffer:

            sections.append(
                Section(
                    current_heading,
                    current_level,
                    "\n".join(buffer).strip()
                )
            )

        return sections, tables