# plugins/loader.py

## TODO
# CTRL+K e CTRL+I: Abre painel com informações sobre comandos válidos dos plugins já instalados

"""
Loader de plugins externos do SuperNanno.

Fluxo:
  1. Criar ~/.config/Bisneto/SuperNanno/Plugins/ se não existir
  2. Para cada subpasta:
     a. Ler e validar plugin.json
     b. Carregar __init__.py via importlib
     c. Executar module.setup(ctx)
     d. Registrar metadata, bindings e CLI
  3. Aplicar bindings dinâmicos no app Textual
  4. Nunca deixar um plugin com falha derrubar o app
"""

import importlib.util
import json
import sys
from pathlib import Path

from services.paths import get_plugins_dir

REQUIRED_FIELDS = {"id", "name", "version"}
PLUGIN_BINDING_PREFIX = "ctrl+shift+"


def load_plugins(ctx) -> None:
    plugins_dir = get_plugins_dir()
    plugins_dir.mkdir(parents=True, exist_ok=True)

    loaded = 0
    failed = 0

    for plugin_path in sorted(plugins_dir.iterdir()):
        if not plugin_path.is_dir():
            continue
        if plugin_path.name.startswith(".") or plugin_path.name.startswith("_"):
            continue

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

        if manifest["id"] != plugin_id:
            _log_skip(ctx, plugin_id, f"id mismatch: folder='{plugin_id}' vs manifest='{manifest['id']}'")
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
                _register_command_keys(ctx, manifest, plugin_id)
            except Exception as e:
                _log_skip(ctx, plugin_id, f"setup() raised: {e}")
                return False

        ctx.plugins.register_metadata(plugin_id, manifest)

        _register_cli(ctx, manifest, plugin_id)

        return True

    except Exception as e:
        _log_skip(ctx, plugin_id, f"unexpected error: {e}")
        return False


def _read_manifest(path: Path) -> dict | None:
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return None

def _register_command_keys(ctx, manifest: dict, plugin_id: str):
    commands = manifest.get("commands", [])

    for cmd in commands:
        key = cmd.get("key")
        command_name = cmd.get("name")

        if not key or not command_name:
            continue

        normalized = f"ctrl+k {key.lower()}"

        ctx.plugins.register_binding({
            "plugin_id": plugin_id,
            "key": normalized,
            "command": command_name,
            "description": f"{cmd.get('description', command_name)} [Plugin]",
        })

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

    except Exception:
        return None

def _register_cli(ctx, manifest: dict, plugin_id: str) -> None:
    cli_entries = manifest.get("cli", [])
    if not cli_entries:
        return

    for entry in cli_entries:
        flag = entry.get("flag", "")
        command = entry.get("command", "")
        args = entry.get("args", [])

        if not flag or not command:
            continue

        ctx.plugins.register_cli_entry({
            "plugin_id": plugin_id,
            "flag": flag,
            "args": args,
            "command": command,
        })

def _log_skip(ctx, plugin_id: str, reason: str) -> None:
    try:
        ctx.status.warning(f"(Plugin): Skipped '{plugin_id}' — {reason}")
    except Exception:
        print(f"[Plugin] Skipped '{plugin_id}' — {reason}")