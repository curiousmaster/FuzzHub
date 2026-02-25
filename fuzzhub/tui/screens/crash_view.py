"""
File: fuzzhub/tui/screens/crash_view.py
"""

from textual.screen import Screen
from textual.widgets import Header, Footer, Static


class CrashScreen(Screen):

    def compose(self):
        yield Header(show_clock=True)
        yield Static("[bold red]Crash Viewer (coming next)[/bold red]")
        yield Footer()
