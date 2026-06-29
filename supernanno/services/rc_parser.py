# services/rc_parser.py

import sys
import traceback
from pathlib import Path

OPTIONAL_VALUE_KEYS = {
    "backupdir",
}


def parse_value(raw: str):
    raw = raw.strip()

    if raw.isdigit():
        return int(raw)

    lowered = raw.lower()
    if lowered == "true":
        return True
    if lowered == "false":
        return False

    return raw


def parse_rc_file(path: Path) -> dict:
    """
    Faz o parse do arquivo .supernannorc.

    Retorna dict vazio em caso de erro (arquivo ausente, permissão negada,
    encoding inválido). Loga no stderr para diagnóstico.
    Nunca levanta exceção.
    """
    config: dict = {}

    if not path.exists():
        return config

    # Tenta UTF-8 primeiro, depois latin-1 como fallback (Windows pode usar CP1252)
    content: str | None = None
    encoding_used: str  = "utf-8"

    for encoding in ("utf-8", "latin-1", "cp1252"):
        try:
            with open(path, "r", encoding=encoding) as f:
                content = f.read()
            encoding_used = encoding
            break
        except UnicodeDecodeError:
            continue
        except PermissionError as e:
            print(
                f"[ERROR] FILE_PERMISSION_ERROR: Cannot read .supernannorc — {e}\n"
                f"  Path: {path}",
                file=sys.stderr,
            )
            return config
        except OSError as e:
            print(
                f"[ERROR] FILESYSTEM_ERROR: I/O error reading .supernannorc — {e}\n"
                f"  Path: {path}",
                file=sys.stderr,
            )
            return config

    if content is None:
        print(
            f"[ERROR] RC_ENCODING_ERROR: Cannot decode .supernannorc with any known encoding.\n"
            f"  Path: {path}\n"
            f"  Tried: utf-8, latin-1, cp1252",
            file=sys.stderr,
        )
        return config

    try:
        for line_num, line in enumerate(content.splitlines(), start=1):
            line = line.strip()

            if not line or line.startswith("#"):
                continue

            parts   = line.split(maxsplit=2)
            command = parts[0].lower()

            if command == "set":
                if len(parts) == 2:
                    key = parts[1].lower()
                    if key in ("linenumbers", "line_numbers", "line-numbers"):
                        config["linenumbers"] = True
                    if key in OPTIONAL_VALUE_KEYS:
                        config[key] = None
                    else:
                        config[key] = True

                elif len(parts) == 3:
                    key   = parts[1].lower()
                    value = parse_value(parts[2])
                    config[key] = value

            elif command == "unset":
                if len(parts) == 2:
                    key         = parts[1].lower()
                    config[key] = False

    except Exception as e:
        print(
            f"[ERROR] RC_PARSE_ERROR: Unexpected error parsing .supernannorc — {e}\n"
            f"  Path: {path}\n"
            f"{traceback.format_exc()}",
            file=sys.stderr,
        )
        # Retorna o que foi parseado até o momento do erro
        return config

    return config
