# ui/settings/screen.py

from textual.app import ComposeResult
from textual.containers import (
    Container,
    Horizontal,
    VerticalScroll,
)
from textual.screen import Screen
from textual.widgets import (
    Button,
    Checkbox,
    Footer,
    Header,
    Input,
    Label,
    Select,
    Static,
    TabbedContent,
    TabPane,
)

from ...services.config_manager import ConfigManager
from ...ui.bindings import SETTINGS_BINDINGS

class SectionHeader(Static):
    """Styled section title within a tab panel."""

class SettingRow(Horizontal):
    """A single labelled setting row."""

class HintLabel(Static):
    """Muted hint text beneath a setting widget."""

class SettingsScreen(Screen):
    """
    Modal-style Settings screen for SuperNanno.

    Keyboard shortcuts:
      ESC        — dismiss without saving
      Ctrl+S     — save and dismiss
      Tab / S-Tab — move between widgets
    """

    BINDINGS = SETTINGS_BINDINGS

    # All TCSS lives in style.tcss — only settings-specific rules added there.
    DEFAULT_CSS = ""  # avoid overriding CSS_PATH

    def __init__(self):
        super().__init__()
        self.config = ConfigManager()

    def compose(self) -> ComposeResult:
        cfg = self.config

        yield Header()

        with Container(id="settings_modal"):
            yield Static("⚙  Settings", id="settings_heading")
            with TabbedContent(id="settings_tabs"):
                with TabPane("General", id="tab_general"):
                    with VerticalScroll(classes="tab_body"):
                        yield SectionHeader("Startup", classes="section_header")
                        yield Checkbox(
                            "Restore last session on startup",
                            value=bool(cfg.get("restoresession", True)),
                            id="restoresession",
                        )
                        yield HintLabel(
                            "Re-opens the last edited file when SuperNanno starts.",
                            classes="hint",
                        )

                        yield SectionHeader("Config Watcher", classes="section_header")
                        yield Checkbox(
                            "Enable live config reload (.supernannorc)",
                            value=bool(cfg.get("configwatcher", True)),
                            id="configwatcher",
                        )
                        yield HintLabel(
                            "Automatically applies changes to .supernannorc without restarting.",
                            classes="hint",
                        )

                        yield SectionHeader("Debug", classes="section_header")
                        yield Checkbox(
                            "Enable debug mode",
                            value=bool(cfg.get("debug", False)),
                            id="debug",
                        )
                        
                with TabPane("Editor", id="tab_editor"):
                    with VerticalScroll(classes="tab_body"):
                        yield SectionHeader("Indentation", classes="section_header")
                        with SettingRow(classes="setting_row"):
                            yield Label("Tab size", classes="setting_label")
                            yield Input(
                                value=str(cfg.get("tabsize", 4)),
                                id="tabsize",
                                placeholder="4",
                                classes="setting_input_short",
                            )

                        yield HintLabel("Number of spaces per indent level.", classes="hint")
                        with SettingRow(classes="setting_row"):
                            yield Label("Indent type", classes="setting_label")
                            yield Select(
                                [("Spaces", "spaces"), ("Tabs", "tabs")],
                                value=str(cfg.get("indenttype", "spaces")),
                                id="indenttype",
                                allow_blank=False,
                            )

                        with SettingRow(classes="setting_row"):
                            yield Label("Tab behaviour", classes="setting_label")
                            yield Select(
                                [("Indent", "indent"), ("Insert tab", "insert")],
                                value=str(cfg.get("tabbehavior", "indent")),
                                id="tabbehavior",
                                allow_blank=False,
                            )

                        yield SectionHeader("Backups", classes="section_header")
                        yield Checkbox(
                            "Auto-create backup on save",
                            value=bool(cfg.get("backup", False)),
                            id="backup",
                        )

                        with SettingRow(classes="setting_row"):
                            yield Label("Backup directory", classes="setting_label")
                            yield Input(
                                value=str(cfg.get("backupdir", "") or ""),
                                id="backupdir",
                                placeholder="~/.config/Bisneto/SuperNanno/Backup",
                                classes="setting_input_wide",
                            )

                with TabPane("Interface", id="tab_interface"):
                    with VerticalScroll(classes="tab_body"):
                        yield SectionHeader("Sidebar", classes="section_header")
                        yield Checkbox(
                            "Show sidebar on startup",
                            value=bool(cfg.get("sidebar", True)),
                            id="sidebar",
                        )

                        with SettingRow(classes="setting_row"):
                            yield Label("Sidebar width", classes="setting_label")
                            yield Input(
                                value=str(cfg.get("sidebarwidth", 35)),
                                id="sidebarwidth",
                                placeholder="35",
                                classes="setting_input_short",
                            )

                        yield SectionHeader("Path Display", classes="section_header")
                        with SettingRow(classes="setting_row"):
                            yield Label("Path display style", classes="setting_label")
                            yield Select(
                                [("Full path", "full"), ("Filename only", "filename")],
                                value=str(cfg.get("pathdisplay", "full")),
                                id="pathdisplay",
                                allow_blank=False,
                            )

                        yield SectionHeader("Working Directory", classes="section_header")
                        with SettingRow(classes="setting_row"):
                            yield Label("Operating directory", classes="setting_label")
                            yield Input(
                                value=str(cfg.get("operatingdir", "~/") or "~/"),
                                id="operatingdir",
                                placeholder="~/",
                                classes="setting_input_wide",
                            )
                        yield HintLabel(
                            "SuperNanno will restrict file operations to this directory.",
                            classes="hint",
                        )

                with TabPane("Search", id="tab_search"):
                    with VerticalScroll(classes="tab_body"):

                        yield SectionHeader("Search Defaults", classes="section_header")
                        yield Checkbox(
                            "Case-sensitive search by default",
                            value=bool(cfg.get("casesensitive", False)),
                            id="casesensitive",
                        )
                        yield Checkbox(
                            "Use regular expressions by default",
                            value=bool(cfg.get("useregex", False)),
                            id="useregex",
                        )
                        yield Checkbox(
                            "Highlight all matches",
                            value=bool(cfg.get("highlightmatches", True)),
                            id="highlightmatches",
                        )
                        
                with TabPane("Files", id="tab_files"):
                    with VerticalScroll(classes="tab_body"):

                        yield SectionHeader("File Handling", classes="section_header")
                        yield Checkbox(
                            "Trim trailing whitespace on save",
                            value=bool(cfg.get("trimwhitespace", True)),
                            id="trimwhitespace",
                        )

                        with SettingRow(classes="setting_row"):
                            yield Label("Backup file extension", classes="setting_label")
                            yield Input(
                                value=str(cfg.get("backupextension", ".bak") or ".bak"),
                                id="backupextension",
                                placeholder=".bak",
                                classes="setting_input_short",
                            )

            with Horizontal(id="settings_actions"):
                yield Button("Save", variant="primary", id="btn_save")
                yield Button("Cancel", variant="default", id="btn_cancel")

        yield Footer()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "btn_save":
            self.action_save()
        elif event.button.id == "btn_cancel":
            self.dismiss() 

    def action_save(self) -> None:
        """
        Collects all widget values defensively and persists them via ConfigManager.

        - If a widget cannot be read, the error is reported and the save is aborted.
        - If config.set() fails for some keys, the user is warned with the
          specific failing keys (never a silent "saved successfully" lie).
        """
        collected: dict = {}
        read_errors: list[str] = []

        checkbox_ids = [
            "restoresession",
            "configwatcher",
            "debug",
            "backup",
            "sidebar",
            "casesensitive",
            "useregex",
            "highlightmatches",
            "trimwhitespace",
        ]
        for widget_id in checkbox_ids:
            try:
                collected[widget_id] = self.query_one(f"#{widget_id}", Checkbox).value
            except Exception as exc:
                read_errors.append(f"{widget_id}: {exc}")

        str_inputs = [
            ("tabsize",          int,   4),
            ("backupdir",        str,   ""),
            ("sidebarwidth",     int,   35),
            ("operatingdir",     str,   "~/"),
            ("backupextension",  str,   ".bak"),
        ]
        for widget_id, cast, fallback in str_inputs:
            try:
                raw = self.query_one(f"#{widget_id}", Input).value.strip()
                try:
                    collected[widget_id] = cast(raw) if raw else fallback
                except (ValueError, TypeError):
                    collected[widget_id] = fallback
            except Exception as exc:
                read_errors.append(f"{widget_id}: {exc}")

        select_ids = ["indenttype", "tabbehavior", "pathdisplay"]
        for widget_id in select_ids:
            try:
                sel = self.query_one(f"#{widget_id}", Select)
                if sel.value is not Select.BLANK:
                    collected[widget_id] = sel.value
            except Exception as exc:
                read_errors.append(f"{widget_id}: {exc}")

        if read_errors:
            self.notify(
                f"Could not read some settings widgets:\n{'; '.join(read_errors)}",
                title="Settings Read Error",
                severity="error",
                timeout=8,
            )
            return

        failed_keys: list[str] = []

        for key, value in collected.items():
            ok = self.config.set(key, value)
            if not ok:
                failed_keys.append(key)
 
        if failed_keys:
            self.notify(
                f"Settings were updated in memory but could NOT be written to disk.\n"
                f"Failed keys: {', '.join(failed_keys)}\n"
                f"Check file permissions on the config directory.",
                title="Settings Save Error",
                severity="warning",
                timeout=10,
            )
        else:
            self.notify(
                "Settings saved successfully.",
                severity="information",
                timeout=3,
            )

        self.dismiss()

    def action_dismiss(self) -> None:
        self.dismiss()