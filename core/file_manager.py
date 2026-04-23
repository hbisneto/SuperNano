# core/file_manager.py

import shutil
from pathlib import Path
from services.paths import get_backups_dir

class FileManager:
    def read(self, path: Path):
        return path.read_text(encoding="utf-8")

    def create_backup(self, path: Path, backup_dir: Path | None = None):
        if not path.exists():
            return

        backup_dir = backup_dir or get_backups_dir()
        backup_dir.mkdir(parents=True, exist_ok=True)

        backup_path = backup_dir / f"{path.name}.bak"
        shutil.copy2(path, backup_path)

    def write(
            self,
            path: Path,
            content: str,
            backup: bool = False,
            backup_dir: Path | None = None
        ):
        if backup and path.exists():
            self.create_backup(path, backup_dir)

        path.write_text(content, encoding="utf-8")