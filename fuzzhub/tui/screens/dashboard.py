"""
File: fuzzhub/tui/screens/dashboard.py
"""

import asyncio
from textual.screen import Screen
from textual.containers import Horizontal, Vertical
from textual.widgets import Footer

from fuzzhub.tui.widgets.sidebar import Sidebar
from fuzzhub.tui.widgets.stats_panel import StatsPanel
from fuzzhub.tui.widgets.fuzzer_table import FuzzerTable
from fuzzhub.tui.api_client import APIClient


class DashboardScreen(Screen):

    def __init__(self):
        super().__init__()
        self.api = APIClient()
        self.stats = StatsPanel()
        self.table = FuzzerTable()

    def compose(self):
        with Horizontal():
            yield Sidebar(id="sidebar")

            with Vertical(id="main"):
                yield self.stats
                yield self.table

        yield Footer()

    async def on_mount(self):
        fuzzers = await asyncio.to_thread(self.api.list_fuzzers)
        self.table.update_data(fuzzers)
        self.stats.update_stats(fuzzers)

        self.set_focus(self.table)

        if self.table.row_count > 0:
            self.table.cursor_coordinate = (0, 0)
