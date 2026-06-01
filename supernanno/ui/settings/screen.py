# ui/settings/screen.py

from textual.app import ComposeResult
from textual.containers import (
    Vertical,
    Horizontal,
    Grid,
)
from textual.screen import Screen
from textual.widgets import (
    Button,
    Static,
    Checkbox,
    Input,
    Label,
    Footer,
    Header,
)

from ...services.config_manager import ConfigManager
from ...ui.bindings import SETTINGS_BINDINGS


class SettingsScreen(Screen):
    BINDINGS = SETTINGS_BINDINGS

    def __init__(self):
        super().__init__()
        self.config = ConfigManager()

    def compose(self) -> ComposeResult:
        yield Header()

        yield Vertical(
            Static("⚙️  SuperNanno Settings", classes="title"),

            # Seção General
            Static("General", classes="section-title"),
            Horizontal(
                Checkbox(
                    "Restore last session on startup",
                    value=self.config.get("settings.startup.restore_session", True),
                    id="restore_session",
                ),
                id="general_row",
            ),

            # Seção Editor / Session
            Static("Editor", classes="section-title"),
            Horizontal(
                Checkbox(
                    "Auto Save",
                    value=self.config.get("settings.session.auto_save", False),
                    id="auto_save",
                ),
                id="editor_row",
            ),

            # Seção UI
            Static("Interface", classes="section-title"),
            Horizontal(
                Checkbox(
                    "Show line numbers",
                    value=self.config.get("settings.ui.line_numbers", True),
                    id="line_numbers",
                ),
                id="ui_row",
            ),

            # Botões
            Horizontal(
                Button("Save", variant="primary",  id="save"),
                Button("Cancel", variant="default", id="cancel"),
                id="buttons",
            ),

            id="settings_container",
        )

        yield Footer()

    def on_button_pressed(self, event):
        if event.button.id == "save":
            self.action_save()
        elif event.button.id == "cancel":
            self.dismiss()

    def action_save(self):
        """
        Salva as configurações com tratamento de exceção.

        - Se query_one() falhar (widget não existe), loga e não salva
          uma configuração inválida.
        - Se config.set() falhar no disco, notifica o usuário com
          mensagem real de erro (não "saved successfully" mentiroso).
        """
        save_errors: list[str] = []

        # Coleta valores dos widgets defensivamente
        try:
            restore_session_val = self.query_one("#restore_session", Checkbox).value
        except Exception as e:
            save_errors.append(f"restore_session: {e}")
            restore_session_val = None

        try:
            auto_save_val = self.query_one("#auto_save", Checkbox).value
        except Exception as e:
            save_errors.append(f"auto_save: {e}")
            auto_save_val = None

        try:
            line_numbers_val = self.query_one("#line_numbers", Checkbox).value
        except Exception as e:
            save_errors.append(f"line_numbers: {e}")
            line_numbers_val = None

        if save_errors:
            self.notify(
                f"Could not read settings widgets: {'; '.join(save_errors)}",
                title="Settings Error",
                severity="error",
                timeout=6,
            )
            return

        # Persiste valores coletados
        failed_keys: list[str] = []

        if restore_session_val is not None:
            ok = self.config.set("settings.startup.restore_session", restore_session_val)
            if not ok:
                failed_keys.append("restore_session")

        if auto_save_val is not None:
            ok = self.config.set("settings.session.auto_save", auto_save_val)
            if not ok:
                failed_keys.append("auto_save")

        if line_numbers_val is not None:
            ok = self.config.set("settings.ui.line_numbers", line_numbers_val)
            if not ok:
                failed_keys.append("line_numbers")

        if failed_keys:
            self.notify(
                f"Settings updated in memory but could NOT be saved to disk. "
                f"Failed keys: {', '.join(failed_keys)}. "
                f"Check disk permissions.",
                title="Settings Save Error",
                severity="warning",
                timeout=8,
            )
        else:
            self.notify("Settings saved successfully!", severity="information")

        self.dismiss()

    def action_dismiss(self):
        self.dismiss()
