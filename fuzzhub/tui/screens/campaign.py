"""
File: fuzzhub/tui/screens/campaign.py
"""

from textual.screen import Screen
from textual.widgets import Header, Footer, Static


class CampaignScreen(Screen):

    def compose(self):
        yield Header(show_clock=True)
        yield Static("[bold cyan]Campaign View (next step)[/bold cyan]")
        yield Footer()
