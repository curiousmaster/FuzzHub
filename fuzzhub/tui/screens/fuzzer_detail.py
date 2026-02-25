"""
File: fuzzhub/tui/screens/fuzzer_detail.py
"""

from textual.screen import Screen
from textual.binding import Binding
from textual.containers import Horizontal, Vertical
from textual.widgets import Static, Footer

from fuzzhub.tui.widgets.sidebar import Sidebar


class FuzzerDetailScreen(Screen):

    BINDINGS = [
        Binding("escape", "go_back", "Back"),
        Binding("q", "app.confirm_quit", "Quit"),
    ]

    def __init__(self, fuzzer_id: str):
        super().__init__()
        self.fuzzer_id = fuzzer_id

    def compose(self):

        with Horizontal():

            # Sidebar (same as main layout)
            yield Sidebar(id="sidebar")

            # Main detail content
            with Vertical(id="detail-main"):
                yield Static("[b]Fuzzer Detail[/b]")
                yield Static(f"ID: {self.fuzzer_id}")
                yield Footer()

    def action_go_back(self):
        self.app.pop_screen()
