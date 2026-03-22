from pathlib import Path

class FileManager:
    def read(self, path: Path):
        return path.read_text(encoding="utf-8")

    def write(self, path: Path, content: str):
        path.write_text(content, encoding="utf-8")