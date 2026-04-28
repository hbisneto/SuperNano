# plugins/registry.py

from typing import Callable, Dict, Any

class PluginRegistry:
    """
    Registro central de todos os plugins carregados.

    Atributos:
        commands      — mapa de nome → callable, executado via ctx.execute_plugin_command()
        hooks         — mapa de hook_name → lista de callables
        metadata      — mapa de plugin_id → dict do plugin.json
        cli_registry  — lista de entradas CLI vindas dos plugins
        bindings      — lista de bindings registrados pelos plugins
    """

    def __init__(self):
        self.commands: Dict[str, Callable] = {}
        self.hooks: Dict[str, list[Callable]] = {}
        self.metadata: Dict[str, dict] = {}
        self.cli_registry: list[dict] = []
        self.bindings: list[dict] = []

    # ==================== COMMANDS ====================

    def register_command(self, name: str, func: Callable):
        self.commands[name] = func

    def execute_command(self, name: str, ctx: Any, *args, **kwargs) -> bool:
        if name in self.commands:
            try:
                self.commands[name](ctx, *args, **kwargs)
                return True
            except Exception as e:
                try:
                    ctx.status.error(f"(Plugin): Command '{name}' failed - {e}")
                except Exception:
                    pass
        return False

    # ==================== HOOKS ====================

    def register_hook(self, hook_name: str, func: Callable):
        self.hooks.setdefault(hook_name, []).append(func)

    def execute_hook(self, hook_name: str, ctx: Any, *args, **kwargs):
        for hook in self.hooks.get(hook_name, []):
            try:
                hook(ctx, *args, **kwargs)
            except Exception as e:
                try:
                    ctx.status.error(f"(Plugin): Hook '{hook_name}' failed - {e}")
                except Exception:
                    pass

    # ==================== METADATA ====================

    def register_metadata(self, plugin_id: str, data: dict):
        self.metadata[plugin_id] = data

    def get_metadata(self, plugin_id: str) -> dict | None:
        return self.metadata.get(plugin_id)

    def list_plugins(self) -> list[dict]:
        return list(self.metadata.values())

    # ==================== CLI ====================

    def register_cli_entry(self, entry: dict):
        self.cli_registry.append(entry)

    # ==================== BINDINGS ====================

    def register_binding(self, entry: dict):
        self.bindings.append(entry)
