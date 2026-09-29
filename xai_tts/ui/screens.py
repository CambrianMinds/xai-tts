from textual.app import ComposeResult
from textual.screen import ModalScreen
from textual.containers import Vertical, Horizontal
from textual.widgets import Label, Button, Input, OptionList
from textual.widgets.option_list import Option
import json
import os

from xai_tts.config import get_history, clear_history, PROJECTS_DIR
from datetime import datetime

class HistoryScreen(ModalScreen):
    CSS = """
    HistoryScreen {
        align: center middle;
    }
    #history-dialog {
        width: 80%;
        height: 80%;
        background: $panel;
        border: thick $primary;
        padding: 1;
    }
    """
    
    def compose(self) -> ComposeResult:
        with Vertical(id="history-dialog"):
            yield Label("Synthesis History", classes="field")
            self.history_list = OptionList(id="history-list")
            yield self.history_list
            with Horizontal():
                yield Button("Load Selected", id="btn-load-hist", variant="primary")
                yield Button("Clear History", id="btn-clear-hist", variant="warning")
                yield Button("Cancel", id="btn-cancel-hist", variant="error")

    def on_mount(self) -> None:
        self.history = get_history()
        self.history.reverse() # newest first
        for idx, item in enumerate(self.history):
            text_preview = item.text[:40].replace('\n', ' ') + ("..." if len(item.text) > 40 else "")
            ts = item.timestamp[:16].replace('T', ' ')
            chars = len(item.text)
            cost_str = f"${item.cost:.5f}" if hasattr(item, 'cost') else "$0.00000"
            label = f"[{ts}] {item.voice} · {item.speed}x · {chars} chars · {cost_str} | {text_preview}"
            self.history_list.add_option(Option(label, id=str(idx)))

    def on_option_list_option_selected(self, event: OptionList.OptionSelected) -> None:
        idx = int(event.option.id)
        self.dismiss(self.history[idx])

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "btn-load-hist":
            if self.history_list.highlighted is not None:
                idx = int(self.history_list.get_option_at_index(self.history_list.highlighted).id)
                self.dismiss(self.history[idx])
            else:
                self.dismiss(None)
        elif event.button.id == "btn-clear-hist":
            clear_history()
            self.history_list.clear_options()
            self.history = []
        elif event.button.id == "btn-cancel-hist":
            self.dismiss(None)


class SaveProjectScreen(ModalScreen):
    CSS = """
    SaveProjectScreen {
        align: center middle;
    }
    #save-dialog {
        width: 60;
        height: 15;
        background: $panel;
        border: thick $primary;
        padding: 1;
    }
    """

    def compose(self) -> ComposeResult:
        with Vertical(id="save-dialog"):
            yield Label("Save Project (JSON)")
            default_name = f"project-{datetime.now().strftime('%Y%m%d-%H%M')}.json"
            default_path = str(PROJECTS_DIR / default_name)
            self.path_input = Input(placeholder="project.json", value=default_path)
            yield self.path_input
            yield Label(f"Will save to: {default_path}", classes="field")
            with Horizontal():
                yield Button("Save", id="btn-save", variant="primary")
                yield Button("Cancel", id="btn-cancel", variant="error")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "btn-save":
            self.dismiss(self.path_input.value)
        elif event.button.id == "btn-cancel":
            self.dismiss(None)

class LoadProjectScreen(ModalScreen):
    CSS = """
    LoadProjectScreen {
        align: center middle;
    }
    #load-dialog {
        width: 60;
        height: 15;
        background: $panel;
        border: thick $primary;
        padding: 1;
    }
    """

    def compose(self) -> ComposeResult:
        with Vertical(id="load-dialog"):
            yield Label("Load Project (JSON)")
            default_path = str(PROJECTS_DIR) + os.sep
            self.path_input = Input(placeholder="path/to/project.json", value=default_path)
            yield self.path_input
            with Horizontal():
                yield Button("Load", id="btn-load", variant="primary")
                yield Button("Cancel", id="btn-cancel", variant="error")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "btn-load":
            self.dismiss(self.path_input.value)
        elif event.button.id == "btn-cancel":
            self.dismiss(None)
