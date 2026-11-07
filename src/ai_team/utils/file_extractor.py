import re
from pathlib import Path
from typing import Dict, List

class FileExtractor:
    """Extract code blocks with file names from LLM responses and write them to disk."""

    @staticmethod
    def extract_files(text: str) -> Dict[str, str]:
        """
        Parses text for code files.
        Recognizes patterns:
        1) ```python:filepath or ```language:filepath
        2) ### File: filepath followed by ```language ... ```
        3) **File: filepath** followed by ```language ... ```
        4) // filepath or # filepath at top of code block
        """
        files: Dict[str, str] = {}

        # Pattern 1: ```[lang]:[filepath]\n[code]```
        p1 = re.compile(r"```(?:\w+)?:\s*([^\n\r]+?)\n([\s\S]*?)```", re.MULTILINE)
        for match in p1.finditer(text):
            filename = match.group(1).strip().strip("`'\"*")
            code = match.group(2)
            if filename:
                files[filename] = code

        # Pattern 2: [###/**] File: filepath [**]\n```[lang]\n[code]```
        p2 = re.compile(
            r"(?:###|\*\*|#|File:)\s*(?:File:\s*)?([a-zA-Z0-9_\-\./\\]+\.[a-zA-Z0-9]+)\*?\*?\s*\n+```(?:\w+)?\n([\s\S]*?)```",
            re.MULTILINE | re.IGNORECASE,
        )
        for match in p2.finditer(text):
            filename = match.group(1).strip().strip("`'\"*")
            code = match.group(2)
            if filename and filename not in files:
                files[filename] = code

        # Pattern 3: Code block starting with `# filename: path` or `// filename: path`
        p3 = re.compile(r"```(?:\w+)?\n(?:\#|\/\/)\s*(?:filename:|file:)?\s*([a-zA-Z0-9_\-\./\\]+\.[a-zA-Z0-9]+)\n([\s\S]*?)```", re.MULTILINE | re.IGNORECASE)
        for match in p3.finditer(text):
            filename = match.group(1).strip().strip("`'\"*")
            code = match.group(2)
            if filename and filename not in files:
                files[filename] = code

        return files

    @staticmethod
    def save_files(files: Dict[str, str], base_dir: Path) -> List[Path]:
        """Save extracted files to the target directory."""
        saved_paths = []
        base_dir.mkdir(parents=True, exist_ok=True)

        for rel_path_str, content in files.items():
            # Clean path to prevent directory traversal
            clean_rel = rel_path_str.replace("\\", "/").lstrip("/")
            # If path contains 'workspace/project/' or similar prefix, strip it if base_dir is already project
            if clean_rel.startswith("src/"):
                clean_rel = clean_rel[4:]
            elif clean_rel.startswith("tests/"):
                pass  # Keep tests/ directory

            target_file = base_dir / clean_rel
            target_file.parent.mkdir(parents=True, exist_ok=True)
            target_file.write_text(content.strip() + "\n", encoding="utf-8")
            saved_paths.append(target_file)

        return saved_paths
