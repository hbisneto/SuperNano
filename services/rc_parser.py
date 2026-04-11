from pathlib import Path

def parse_rc_file(path: Path) -> dict:
    config = {}

    if not path.exists():
        return config

    with open(path, "r") as f:
        for line in f:
            line = line.strip()

            if not line or line.startswith("#"):
                continue

            if line.startswith("set"):
                parts = line.split(maxsplit=2)

                if len(parts) < 3:
                    continue

                _, key, value = parts
                value = convert_value(value)
                config[key] = value

    return config


def convert_value(value: str):
    value = value.strip()

    if value.lower() in ("true", "false"):
        return value.lower() == "true"

    if value.isdigit():
        return int(value)

    return value