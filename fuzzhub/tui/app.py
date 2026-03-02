"""
File: fuzzhub/tui/app.py
"""

from textual.app import App, ComposeResult
from textual.binding import Binding

from fuzzhub.tui.screens.dashboard import Dashboard
from fuzzhub.tui.screens.confirm_quit import ConfirmQuitScreen


class FuzzHubApp(App):

    CSS_PATH = "theme.css"

    BINDINGS = [
        Binding("q", "confirm_quit", "Quit"),
    ]

    def compose(self) -> ComposeResult:
        yield Dashboard()

    def action_confirm_quit(self):
        self.push_screen(ConfirmQuitScreen())
