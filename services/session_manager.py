# services/session_manager.py

import json
import sys
import traceback
from pathlib import Path
from services.paths import get_config_dir


class SessionManager:
    """
    Gerenciador de sessão com:
    - Atomic save (write-to-tmp + rename)
    - Recuperação de sessão corrompida (fallback para defaults)
    - Logs de stderr durante inicialização (ctx não disponível ainda)
    - Nunca levanta exceção — persistência é best-effort
    """

    def __init__(self, create_if_missing: bool = False):
        self.session_path = get_config_dir() / "session.json"
        self._session: dict = {
            "last_file":    None,
            "recent_files": [],
        }

        if self.session_path.exists():
            self.load()
        elif create_if_missing:
            self.save()

    # ─── Carregamento ────────────────────────────────────────────────

    def load(self) -> bool:
        """
        Carrega session.json.

        Em caso de corrupção (JSON inválido), loga e usa sessão vazia.
        Retorna True em sucesso, False se houve falha não-crítica.
        Nunca levanta exceção.
        """
        try:
            with open(self.session_path, "r", encoding="utf-8") as f:
                data = json.load(f)

            # Valida estrutura mínima
            if not isinstance(data, dict):
                raise ValueError(
                    f"session.json must be a JSON object, got {type(data).__name__}"
                )

            self._session.update(data)
            return True

        except json.JSONDecodeError as e:
            print(
                f"[ERROR] SESSION_PARSE_ERROR: session.json is corrupted — {e}\n"
                f"  Path: {self.session_path}\n"
                f"  Session will start empty. You may need to reopen your files.",
                file=sys.stderr,
            )
            # Tenta fazer backup do arquivo corrompido para diagnóstico
            self._backup_corrupted()
            return False

        except PermissionError as e:
            print(
                f"[ERROR] FILE_PERMISSION_ERROR: Cannot read session.json — {e}\n"
                f"  Path: {self.session_path}\n"
                f"  Session restore is disabled for this run.",
                file=sys.stderr,
            )
            return False

        except OSError as e:
            print(
                f"[ERROR] FILESYSTEM_ERROR: I/O error reading session.json — {e}\n"
                f"  Path: {self.session_path}",
                file=sys.stderr,
            )
            return False

        except ValueError as e:
            print(
                f"[ERROR] SESSION_INVALID: Invalid session.json structure — {e}\n"
                f"  Path: {self.session_path}\n"
                f"  Session will start empty.",
                file=sys.stderr,
            )
            self._backup_corrupted()
            return False

        except Exception as e:
            print(
                f"[ERROR] SESSION_LOAD_ERROR: Unexpected error loading session — {e}\n"
                f"{traceback.format_exc()}",
                file=sys.stderr,
            )
            return False

    # ─── Persistência ────────────────────────────────────────────────

    def save(self) -> bool:
        """
        Persiste session.json usando atomic write.

        Retorna True em sucesso, False em falha.
        Nunca levanta exceção — sessão é best-effort.
        """
        tmp_path = self.session_path.with_suffix(".tmp")

        try:
            self.session_path.parent.mkdir(parents=True, exist_ok=True)

            with open(tmp_path, "w", encoding="utf-8") as f:
                json.dump(self._session, f, indent=4, ensure_ascii=False)
                f.flush()

            tmp_path.replace(self.session_path)
            return True

        except PermissionError as e:
            print(
                f"[ERROR] FILE_PERMISSION_ERROR: Cannot save session.json — {e}\n"
                f"  Path: {self.session_path}\n"
                f"  Session will NOT be restored on next launch.",
                file=sys.stderr,
            )

        except OSError as e:
            print(
                f"[ERROR] FILESYSTEM_ERROR: I/O error saving session.json — {e}\n"
                f"  Path: {self.session_path}\n"
                f"  Session will NOT be restored on next launch.",
                file=sys.stderr,
            )

        except Exception as e:
            print(
                f"[ERROR] SESSION_SAVE_ERROR: Unexpected error saving session — {e}\n"
                f"{traceback.format_exc()}",
                file=sys.stderr,
            )

        finally:
            # Remove tmp em caso de falha
            try:
                if tmp_path.exists():
                    tmp_path.unlink()
            except Exception:
                pass

        return False

    # ─── API pública ─────────────────────────────────────────────────

    def get_last_file(self) -> "str | None":
        return self._session.get("last_file")

    def set_last_file(self, path: str) -> None:
        self._session["last_file"] = path
        self.save()

    def add_recent_file(self, path: str) -> None:
        recent = self._session.get("recent_files", [])
        if path not in recent:
            recent.insert(0, path)
        self._session["recent_files"] = recent[:10]
        self.save()

    def get_recent_files(self) -> list:
        return self._session.get("recent_files", [])

    # ─── Helpers internos ────────────────────────────────────────────

    def _backup_corrupted(self) -> None:
        """Move o arquivo corrompido para .corrupted para diagnóstico."""
        try:
            corrupted = self.session_path.with_suffix(".corrupted")
            self.session_path.rename(corrupted)
            print(
                f"[INFO] SESSION_BACKUP: Corrupted session saved to {corrupted}",
                file=sys.stderr,
            )
        except Exception:
            pass
