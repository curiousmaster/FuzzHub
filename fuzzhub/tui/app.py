"""
File: fuzzhub/tui/app.py
"""

from textual.app import App
from textual.binding import Binding

from fuzzhub.tui.screens.dashboard import DashboardScreen
from fuzzhub.tui.screens.confirm_quit import ConfirmQuitScreen


class FuzzHubApp(App):

    CSS_PATH = "theme.css"

    BINDINGS = [
        Binding("q", "confirm_quit", "Quit"),
    ]

    def on_mount(self):
        # Set dashboard as root screen
        self.install_screen(DashboardScreen(), name="dashboard")
        self.push_screen("dashboard")

    def action_confirm_quit(self):
        self.push_screen(ConfirmQuitScreen())
