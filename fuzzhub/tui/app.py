"""
File: fuzzhub/tui/app.py
"""

from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import Horizontal, Vertical, Container
from textual.widgets import Footer

from fuzzhub.tui.widgets.sidebar import Sidebar
from fuzzhub.tui.views.dashboard import DashboardScreen
from fuzzhub.tui.views.fuzzer_detail import FuzzerDetailView
from fuzzhub.tui.screens.confirm_quit import ConfirmQuitScreen

class FuzzHubApp(App):

    CSS_PATH = "theme.css"

    BINDINGS = [
        Binding("q", "confirm_quit", "Quit"),
    ]

    def compose(self) -> ComposeResult:
        with Horizontal():
            yield Sidebar(id="sidebar")

            with Vertical(id="main"):
                yield Container(id="content")
                yield Footer()

    # -----------------------------------------
    # Lifecycle
    # -----------------------------------------

    def on_mount(self):
        self.show_dashboard()

    # -----------------------------------------
    # Navigation
    # -----------------------------------------
    #

    def show_fuzzer_detail(self, fuzzer_id):
        content = self.query_one("#content")
        content.remove_children()
        content.mount(FuzzerDetailView(fuzzer_id))

    def show_dashboard(self):
        content = self.query_one("#content")
        content.remove_children()
        content.mount(DashboardScreen())

    # -----------------------------------------
    # Actions
    # -----------------------------------------

    def action_confirm_quit(self):
        self.push_screen(ConfirmQuitScreen())
