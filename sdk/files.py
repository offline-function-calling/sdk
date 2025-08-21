from mimetypes import guess_file_type
from pathlib import Path
from typing import List

from markitdown import MarkItDown

from .types import File


class FileManager:
    """Manages loading and converting file content into text for models."""

    def __init__(self):
        self.converter = MarkItDown()

    def process_files(self, paths: List[str]) -> List[File]:
        files = []
        for path in paths:
            files.append(self._process_file(path))

        return files

    def _process_file(self, path: str) -> File:
        path = Path(path)

        mime, _ = guess_file_type(path)
        name, uri = path.stem, path.as_uri()

        if mime.startswith("image/"):
            contents = path.read_bytes()
        else:
            contents = self.converter.convert(path)

        return File(name=name, uri=uri, mime=mime, contents=contents)
