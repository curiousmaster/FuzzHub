"""
File: fuzzhub/tui/views/dashboard.py
"""

import asyncio
import json
import websockets

from textual.widget import Widget
from textual.containers import Vertical
from textual.binding import Binding

from fuzzhub.tui.widgets.stats_panel import StatsPanel
from fuzzhub.tui.widgets.fuzzer_table import FuzzerTable
from fuzzhub.tui.api_client import APIClient


class DashboardScreen(Widget):

    BINDINGS = [
        Binding("r", "refresh", "Refresh"),
    ]

    def __init__(self):
        super().__init__()
        self.api = APIClient()
        self.stats = StatsPanel()
        self.table = FuzzerTable()
        self._ws_task = None

    # --------------------------------------------------
    # Layout
    # --------------------------------------------------

    def compose(self):
        with Vertical():
            yield self.stats
            yield self.table

    # --------------------------------------------------
    # Lifecycle
    # --------------------------------------------------

    def on_mount(self):
        # Initial load
        self.refresh_data()

        # Start WebSocket listener
        self._ws_task = asyncio.create_task(self._listen_ws())

    def on_unmount(self):
        if self._ws_task:
            self._ws_task.cancel()

    # --------------------------------------------------
    # WebSocket Listener
    # --------------------------------------------------

    async def _listen_ws(self):
        uri = "ws://127.0.0.1:8000/ws"

        while True:
            try:
                async with websockets.connect(uri) as websocket:
                    while True:
                        message = await websocket.recv()
                        event = json.loads(message)
                        self._handle_event(event)
            except Exception:
                await asyncio.sleep(2)

    # --------------------------------------------------
    # Event Handling
    # --------------------------------------------------

    def _handle_event(self, event):
        event_type = event.get("type")

        if event_type in (
            "fuzzer_started",
            "fuzzer_stopped",
            "fuzzer_update",
        ):
            self.refresh_data()

    # --------------------------------------------------
    # Manual Refresh
    # --------------------------------------------------

    def action_refresh(self):
        self.refresh_data()

    def refresh_data(self):
        fuzzers = self.api.list_fuzzers()
        self.table.update_data(fuzzers)
        self.stats.update_stats(fuzzers)
