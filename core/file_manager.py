# core/file_manager.py

import shutil
from pathlib import Path
from services.paths import get_backups_dir

# Sequência de encodings tentados como fallback quando UTF-8 falha
ENCODING_FALLBACKS = ("utf-8", "latin-1", "cp1252", "utf-16", "ascii")


class FileManager:
    """
    Gerenciador de I/O de arquivos com:
    - Fallback de encoding automático
    - Backup resiliente (backup nunca bloqueia o save)
    - Atomic write via arquivo temporário
    - Logs estruturados e tratamento completo de exceções
    """

    # ─── Leitura ──────────────────────────────────────────────────────

    def read(self, path: Path) -> str:
        """
        Lê o arquivo tentando UTF-8 primeiro, depois os fallbacks.
        Levanta a exceção original se todos os encodings falharem.

        Raises
        ------
        FileNotFoundError  : Arquivo não existe
        PermissionError    : Sem permissão de leitura
        UnicodeDecodeError : Nenhum encoding conseguiu decodificar
        IsADirectoryError  : Path aponta para diretório
        OSError            : Outro erro de I/O
        """
        if not path.exists():
            raise FileNotFoundError(f"File not found: {path}")

        if path.is_dir():
            raise IsADirectoryError(f"Path is a directory: {path}")

        last_exc: Exception = FileNotFoundError("No encodings attempted")

        for encoding in ENCODING_FALLBACKS:
            try:
                content = path.read_text(encoding=encoding)
                return content
            except UnicodeDecodeError as e:
                last_exc = e
                continue
            except (PermissionError, OSError) as e:
                # Erros de permissão/I/O não têm fallback de encoding
                raise e

        # Se chegou aqui, todos os encodings falharam
        raise last_exc

    # ─── Backup ───────────────────────────────────────────────────────

    def create_backup(self, path: Path, backup_dir: "Path | None" = None) -> bool:
        """
        Cria backup do arquivo.

        Retorna True se backup foi criado, False se não (arquivo não existe
        ou falha não crítica). Nunca levanta exceção — backup nunca pode
        impedir o save principal.
        """
        if not path.exists():
            return False

        try:
            target_dir  = backup_dir or get_backups_dir()
            target_dir.mkdir(parents=True, exist_ok=True)

            backup_path = target_dir / f"{path.name}.bak"
            shutil.copy2(path, backup_path)
            return True

        except (PermissionError, OSError):
            # Backup falhou, mas o save principal não deve ser bloqueado.
            # O chamador decide se quer logar.
            return False
        except Exception:
            return False

    # ─── Escrita ──────────────────────────────────────────────────────

    def write(
        self,
        path: Path,
        content: str,
        backup: bool = False,
        backup_dir: "Path | None" = None,
    ) -> bool:
        """
        Escreve conteúdo no arquivo usando write-then-rename para atomicidade.

        O backup é tentado antes da escrita, mas uma falha de backup NÃO
        interrompe a escrita — o arquivo principal sempre tem prioridade.

        Retorna True em sucesso.

        Raises
        ------
        PermissionError    : Sem permissão de escrita
        IsADirectoryError  : Path aponta para diretório
        OSError            : Disco cheio, path inválido, etc.
        """
        # Backup é best-effort: falha não bloqueia o save
        if backup and path.exists():
            self.create_backup(path, backup_dir)

        # Atomic write: escreve em .tmp e faz rename
        tmp_path = path.with_suffix(path.suffix + ".tmp")

        try:
            # Garante que o diretório pai existe
            path.parent.mkdir(parents=True, exist_ok=True)

            with open(tmp_path, "w", encoding="utf-8") as f:
                f.write(content)
                f.flush()

            tmp_path.replace(path)
            return True

        except Exception:
            # Remove o arquivo temporário em caso de falha
            try:
                if tmp_path.exists():
                    tmp_path.unlink()
            except Exception:
                pass
            raise  # Propaga a exceção original para o chamador logar
