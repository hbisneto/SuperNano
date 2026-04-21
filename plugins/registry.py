# plugins/registry.py

from typing import Callable, Dict, Any

class PluginRegistry:
    def __init__(self):
        self.commands: Dict[str, Callable] = {}
        self.hooks: Dict[str, list[Callable]] = {}

    def register_command(self, name: str, func: Callable):
        self.commands[name] = func

    def register_hook(self, hook_name: str, func: Callable):
        self.hooks.setdefault(hook_name, []).append(func)

    def execute_command(self, name: str, ctx: Any, *args, **kwargs) -> bool:
        if name in self.commands:
            self.commands[name](ctx, *args, **kwargs)
            return True
        return False

    def execute_hook(self, hook_name: str, ctx: Any, *args, **kwargs):
        for hook in self.hooks.get(hook_name, []):
            try:
                hook(ctx, *args, **kwargs)
            except Exception as e:
                ctx.status.error(f"Plugin hook '{hook_name}' error: {e}")