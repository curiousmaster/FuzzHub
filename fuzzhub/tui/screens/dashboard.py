"""
File: fuzzhub/tui/screens/dashboard.py
"""

import asyncio
from textual.widget import Widget
from textual.containers import Horizontal, Vertical
from textual.widgets import Footer

from fuzzhub.tui.widgets.sidebar import Sidebar
from fuzzhub.tui.widgets.stats_panel import StatsPanel
from fuzzhub.tui.widgets.fuzzer_table import FuzzerTable
from fuzzhub.tui.api_client import APIClient


class Dashboard(Widget):

    def __init__(self):
        super().__init__()
        self.api = APIClient()
        self.stats = StatsPanel()
        self.table = FuzzerTable()

    def compose(self):
        with Horizontal(id="layout"):
            yield Sidebar(id="sidebar")

            with Vertical(id="main"):
                yield self.stats
                yield self.table

    def on_mount(self):
        # Load data synchronously via worker
        self.run_worker(self._load_data, thread=True)

        # Focus table AFTER mount
        self.call_later(lambda: self.app.set_focus(self.table))

    def _load_data(self):
        fuzzers = self.api.list_fuzzers()

        def update():
            self.table.update_data(fuzzers)
            self.stats.update_stats(fuzzers)

            if self.table.row_count > 0:
                self.table.cursor_coordinate = (0, 0)

        self.app.call_from_thread(update)

