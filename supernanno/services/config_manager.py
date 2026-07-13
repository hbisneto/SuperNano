# services/config_manager.py

import json
import sys
import traceback
from typing import Any, Dict
from ..services.paths import (
    get_config_dir,
    get_rc_file,
)
from ..services.rc_parser import parse_rc_file

DEFAULT_CONFIG: Dict[str, Any] = {
    # Backups
    "backup":    False,
    "backupdir": None,

    # Live reload
    "configwatcher":         True,
    "configwatcherinterval": 1,

    # Editor
    "indenttype":  "spaces",
    "tabbehavior": "indent",
    "tabsize":     4,
    "linenumbers": True,

    # App
    "operatingdir":  "~/",
    "restoresession": True,
    "sidebar":       True,
    "sidebarwidth":  35,
    "pathdisplay":   "full",

    # Debug
    "debug": False,
}


class ConfigManager:
    """
    Gerenciador de configuração com:
    - Atomic writes (write-then-rename)
    - Tratamento de corrupção com fallback para defaults
    - Logs de stderr durante inicialização (ctx não disponível ainda)
    - reload_rc_if_changed() resiliente a race conditions
    """

    def __init__(self):
        self.config_path = get_config_dir() / "config.json"
        self.data        = DEFAULT_CONFIG.copy()
        self.rc_path     = get_rc_file()
        self._rc_mtime   = None

        # Carrega config.json se existir
        if self.config_path.exists():
            self._load()

        # Carrega .supernannorc por cima
        self._load_rc()

    # ─── Carregamento ────────────────────────────────────────────────

    def _load(self) -> None:
        """
        Carrega config.json. Em caso de JSON corrompido ou erro de I/O,
        loga no stderr (ctx não existe ainda) e mantém defaults.
        Nunca levanta exceção.
        """
        try:
            with open(self.config_path, "r", encoding="utf-8") as f:
                loaded = json.load(f)
            self.data.update(loaded)

        except json.JSONDecodeError as e:
            print(
                f"[ERROR] CONFIG_PARSE_ERROR: config.json is corrupted — {e}\n"
                f"  Path: {self.config_path}\n"
                f"  Using default configuration.",
                file=sys.stderr,
            )

        except PermissionError as e:
            print(
                f"[ERROR] FILE_PERMISSION_ERROR: Cannot read config.json — {e}\n"
                f"  Path: {self.config_path}\n"
                f"  Using default configuration.",
                file=sys.stderr,
            )

        except OSError as e:
            print(
                f"[ERROR] FILESYSTEM_ERROR: I/O error reading config.json — {e}\n"
                f"  Path: {self.config_path}\n"
                f"  Using default configuration.",
                file=sys.stderr,
            )

        except Exception as e:
            print(
                f"[ERROR] CONFIG_LOAD_ERROR: Unexpected error reading config.json — {e}\n"
                f"{traceback.format_exc()}"
                f"  Using default configuration.",
                file=sys.stderr,
            )

    def _load_rc(self) -> None:
        """
        Carrega .supernannorc. Em caso de falha, loga e continua.
        Nunca levanta exceção.
        """
        try:
            rc_config = parse_rc_file(self.rc_path)
            self.data.update(rc_config)
        except Exception as e:
            print(
                f"[ERROR] RC_PARSE_ERROR: Failed to parse .supernannorc — {e}\n"
                f"  Path: {self.rc_path}\n"
                f"{traceback.format_exc()}",
                file=sys.stderr,
            )

    # ─── Acesso ──────────────────────────────────────────────────────

    def get(self, key: str, default: Any = None) -> Any:
        return self.data.get(key, default)

    # ─── Persistência ────────────────────────────────────────────────

    def save(self) -> bool:
        """
        Persiste config.json usando atomic write (write-to-tmp + rename).

        Retorna True em sucesso, False em falha.
        Nunca silencia o erro — propaga para o chamador decidir.
        """
        tmp_path = self.config_path.with_suffix(".tmp")

        try:
            self.config_path.parent.mkdir(parents=True, exist_ok=True)

            with open(tmp_path, "w", encoding="utf-8") as f:
                json.dump(self.data, f, indent=4, ensure_ascii=False)
                f.flush()

            tmp_path.replace(self.config_path)
            return True

        except Exception:
            try:
                if tmp_path.exists():
                    tmp_path.unlink()
            except Exception:
                pass
            raise  # Propaga para o chamador (set() vai logar)

    def set(self, key: str, value: Any, auto_save: bool = True) -> bool:
        """
        Define um valor e opcionalmente persiste.

        Em caso de falha no save, loga no stderr e retorna False
        (ao invés de retornar True mentindo que foi salvo).
        """
        self.data[key] = value

        if auto_save:
            try:
                self.save()
            except PermissionError as e:
                print(
                    f"[ERROR] FILE_PERMISSION_ERROR: Cannot save config — {e}\n"
                    f"  Path: {self.config_path}\n"
                    f"  Key '{key}' was updated in memory but NOT persisted.",
                    file=sys.stderr,
                )
                return False

            except OSError as e:
                print(
                    f"[ERROR] FILESYSTEM_ERROR: I/O error saving config — {e}\n"
                    f"  Path: {self.config_path}\n"
                    f"  Key '{key}' was updated in memory but NOT persisted.",
                    file=sys.stderr,
                )
                return False

            except Exception as e:
                print(
                    f"[ERROR] CONFIG_SAVE_ERROR: Unexpected error saving config — {e}\n"
                    f"{traceback.format_exc()}"
                    f"  Key '{key}' was updated in memory but NOT persisted.",
                    file=sys.stderr,
                )
                return False

        return True

    # ─── Config watcher ──────────────────────────────────────────────

    def reload_rc_if_changed(self) -> bool:
        """
        Verifica se o .supernannorc mudou e, se sim, recarrega.

        É resiliente a race conditions: arquivo pode desaparecer entre
        exists() e stat(). Nunca levanta exceção — o chamador
        (__watch_config__) trata erros.

        Retorna True se a config foi recarregada.
        """
        try:
            if not self.rc_path.exists():
                return False

            mtime = self.rc_path.stat().st_mtime

            if self._rc_mtime is None:
                self._rc_mtime = mtime
                return False

            if mtime != self._rc_mtime:
                self._rc_mtime = mtime

                try:
                    rc_config = parse_rc_file(self.rc_path)
                    self.data.update(rc_config)
                    return True
                except Exception as e:
                    # RC corrompido — loga e não aplica
                    print(
                        f"[ERROR] RC_RELOAD_ERROR: Failed to reload .supernannorc — {e}\n"
                        f"{traceback.format_exc()}",
                        file=sys.stderr,
                    )
                    return False

            return False

        except OSError as e:
            # Arquivo pode ter sumido entre exists() e stat() — ignorável
            print(
                f"[WARN] RC_STAT_ERROR: Could not stat .supernannorc — {e}",
                file=sys.stderr,
            )
            return False

        except Exception as e:
            print(
                f"[ERROR] RC_CHECK_ERROR: Unexpected error checking .supernannorc — {e}\n"
                f"{traceback.format_exc()}",
                file=sys.stderr,
            )
            return False