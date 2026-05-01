# plugins/registry.py

class PluginRegistry:
    def __init__(self):
        self.commands = {}
        self.hooks = {}
        self.bindings = []
        self.binding_tree = {}  # 🌳 árvore de comandos

    # ==================== COMMANDS ====================

    def register_command(self, name: str, func: callable):
        self.commands[name] = func

    def execute_command(self, name: str, ctx, *args, **kwargs) -> bool:
        cmd = self.commands.get(name)

        if not cmd:
            ctx.status.warning(f"(Plugin): Command '{name}' not found")
            return False

        try:
            cmd(ctx, *args, **kwargs)
            return True
        except Exception as e:
            ctx.status.error(f"(Plugin): Command '{name}' failed - {e}")
            return False

    def register_hook(self, hook_name: str, func: callable):
        self.hooks.setdefault(hook_name, []).append(func)

    def execute_hook(self, hook_name: str, ctx, *args, **kwargs):
        for hook in self.hooks.get(hook_name, []):
            try:
                hook(ctx, *args, **kwargs)
            except Exception as e:
                ctx.status.error(f"(Plugin): Hook '{hook_name}' failed - {e}")

    # ==================== BINDINGS ====================
    def register_binding(self, binding: dict):
        self.bindings.append(binding)

        key = binding["key"].lower().strip()
        parts = key.split()

        if len(parts) < 2:
            return

        sequence = parts[1:]
        node = self.binding_tree

        for part in sequence:
            if part not in node:
                node[part] = {}

            node = node[part]

        if "__cmd__" in node:
            return

        node["__cmd__"] = binding["command"]

    def register_metadata(self, plugin_id: str, data: dict):
        if not hasattr(self, "metadata"):
            self.metadata = {}
        self.metadata[plugin_id] = data

    def register_cli_entry(self, entry: dict):
        if not hasattr(self, "cli_registry"):
            self.cli_registry = []
        self.cli_registry.append(entry)

    def get_next_keys(self, sequence: list[str]) -> dict:
        node = self.binding_tree

        for key in sequence:
            if key not in node:
                return {}

            node = node[key]

        result = {}

        for k, v in node.items():
            if k == "__cmd__":
                continue

            if "__cmd__" in v:
                result[k] = v["__cmd__"]
            else:
                result[k] = None

        return result