# plugins/loader.py

import importlib.util
import json
import sys
import traceback
from pathlib import Path
from services.paths import get_plugins_dir

REQUIRED_FIELDS = {"id", "name", "version"}

def load_plugins(ctx) -> None:
    plugins_dir = get_plugins_dir()
    plugins_dir.mkdir(parents=True, exist_ok=True)

    loaded = 0
    failed = 0

    plugin_folders = [
        p for p in sorted(plugins_dir.iterdir())
        if p.is_dir() and not p.name.startswith((".", "_"))
    ]

    if not plugin_folders:
        return

    for plugin_path in plugin_folders:
        success = _load_single_plugin(ctx, plugin_path)
        if success:
            loaded += 1
        else:
            failed += 1

    if loaded > 0:
        ctx.status.info(f"(Plugins): {loaded} plugin(s) loaded" + (f", {failed} failed" if failed else ""))
    elif failed > 0:
        ctx.status.warning(f"(Plugins): {failed} plugin(s) failed to load")

def _load_single_plugin(ctx, plugin_path: Path) -> bool:
    plugin_id = plugin_path.name

    try:
        manifest_path = plugin_path / "plugin.json"
        if not manifest_path.exists():
            _log_skip(ctx, plugin_id, "plugin.json not found")
            return False

        manifest = _read_manifest(manifest_path)
        if manifest is None:
            _log_skip(ctx, plugin_id, "invalid JSON in plugin.json")
            return False

        missing = REQUIRED_FIELDS - set(manifest.keys())
        if missing:
            _log_skip(ctx, plugin_id, f"missing fields: {', '.join(missing)}")
            return False

        init_path = plugin_path / "__init__.py"
        if not init_path.exists():
            _log_skip(ctx, plugin_id, "__init__.py not found")
            return False

        module = _import_module(plugin_id, init_path)
        if module is None:
            _log_skip(ctx, plugin_id, "failed to import __init__.py")
            return False

        if hasattr(module, "setup"):
            try:
                module.setup(ctx)
            except Exception as e:
                _log_skip(ctx, plugin_id, f"setup() raised: {e}")
                return False
        else:
            print(f"[PLUGIN DEBUG] WARNING: No setup() in {plugin_id}")

        _register_command_keys(ctx, manifest, plugin_id)
        ctx.plugins.register_metadata(plugin_id, manifest)
        return True

    except Exception as e:
        _log_skip(ctx, plugin_id, f"unexpected error: {e}")
        return False

def _register_command_keys(ctx, manifest: dict, plugin_id: str):
    commands = manifest.get("commands", [])
    if not commands:
        return

    for cmd in commands:
        key_raw = cmd.get("key", "").lower().strip()
        command_name = cmd.get("name", "").strip()

        if not key_raw or not command_name:
            continue
        subkey = _normalize_subkey(key_raw)
        full_key = f"ctrl+k {subkey}"
        ctx.plugins.register_binding({
            "plugin_id": plugin_id,
            "key": full_key,
            "command": command_name,
            "description": cmd.get("description", command_name),
        })

def _normalize_subkey(key: str) -> str:
    return key

def _read_manifest(path: Path) -> dict | None:
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return None

def _import_module(plugin_id: str, init_path: Path):
    try:
        module_name = f"supernanno_plugin_{plugin_id}"

        if module_name in sys.modules:
            return sys.modules[module_name]

        spec = importlib.util.spec_from_file_location(module_name, init_path)
        if spec is None or spec.loader is None:
            return None

        module = importlib.util.module_from_spec(spec)
        sys.modules[module_name] = module
        spec.loader.exec_module(module)

        return module

    except Exception as e:
        return None

def _log_skip(ctx, plugin_id: str, reason: str) -> None:
    try:
        ctx.status.warning(f"(Plugin): Skipped '{plugin_id}' — {reason}")
    except Exception:
        print(f"[Plugin] Skipped '{plugin_id}' — {reason}")