# ui/settings/screen.py
from textual.app import ComposeResult
from textual.containers import(
    Vertical,
    Horizontal,
    Grid
)
from textual.screen import Screen
from textual.widgets import (
    Button, 
    Static, 
    Checkbox, 
    Input, 
    Label, 
    Footer, 
    Header
)

from services.config_manager import ConfigManager
from ui.bindings import SETTINGS_BINDINGS

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
                    id="restore_session"
                ),
                id="general_row"
            ),

            # Seção Editor / Session
            Static("Editor", classes="section-title"),
            Horizontal(
                Checkbox(
                    "Auto Save", 
                    value=self.config.get("settings.session.auto_save", False),
                    id="auto_save"
                ),
                id="editor_row"
            ),

            # Seção UI
            Static("Interface", classes="section-title"),
            Horizontal(
                Checkbox(
                    "Show line numbers", 
                    value=self.config.get("settings.ui.line_numbers", True),
                    id="line_numbers"
                ),
                id="ui_row"
            ),

            # Botões
            Horizontal(
                Button("Save", variant="primary", id="save"),
                Button("Cancel", variant="default", id="cancel"),
                id="buttons"
            ),

            id="settings_container"
        )
        
        yield Footer()

    def on_button_pressed(self, event):
        if event.button.id == "save":
            self.action_save()
        elif event.button.id == "cancel":
            self.dismiss()

    def action_save(self):
        self.config.set("settings.startup.restore_session", 
            self.query_one("#restore_session", Checkbox).value)

        self.config.set("settings.session.auto_save", 
            self.query_one("#auto_save", Checkbox).value)

        self.config.set("settings.ui.line_numbers", 
            self.query_one("#line_numbers", Checkbox).value)

        self.notify("Settings saved successfully!", severity="information")
        self.dismiss()

    def action_dismiss(self):
        self.dismiss()