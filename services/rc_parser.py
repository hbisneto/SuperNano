# services/rc_parser.py

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
    config = {}

    if not path.exists():
        return config

    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()

            if not line or line.startswith("#"):
                continue

            parts = line.split(maxsplit=2)
            command = parts[0].lower()

            if command == "set":
                if len(parts) == 2:
                    key = parts[1].lower()

                    if key in OPTIONAL_VALUE_KEYS:
                        config[key] = None
                    else:
                        config[key] = True

                elif len(parts) == 3:
                    key = parts[1].lower()
                    value = parse_value(parts[2])
                    config[key] = value

            elif command == "unset":
                if len(parts) == 2:
                    key = parts[1].lower()
                    config[key] = False

    return config