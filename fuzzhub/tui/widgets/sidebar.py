"""
File: fuzzhub/tui/widgets/sidebar.py
"""

from textual.widget import Widget
from textual.containers import Vertical
from textual.widgets import Static
from textual.binding import Binding


class Sidebar(Widget):

    BINDINGS = [
        Binding("d", "dashboard", "Dashboard"),
    ]

    def compose(self):
        with Vertical(classes="sidebar-container"):
            yield Static("FuzzHub", classes="sidebar-title")
            yield Static("")
            yield Static("[D] Dashboard", classes="sidebar-item")

    def action_dashboard(self):
        from fuzzhub.tui.views.dashboard import DashboardScreen
        self.app.push_screen(DashboardScreen())
