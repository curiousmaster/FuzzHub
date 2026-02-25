"""
File: fuzzhub/tui/screens/fuzzer_detail.py
"""

import asyncio
import json
import websockets

from textual.screen import Screen
from textual.binding import Binding
from textual.containers import Horizontal, Vertical, Container
from textual.widgets import Static, Footer

from fuzzhub.tui.widgets.sidebar import Sidebar
from fuzzhub.tui.api_client import APIClient


class FuzzerDetailScreen(Screen):

    BINDINGS = [
        Binding("escape", "go_back", "Back"),
        Binding("q", "app.confirm_quit", "Quit"),
    ]

    def __init__(self, fuzzer_id: str):
        super().__init__()
        self.fuzzer_id = fuzzer_id
        self.api = APIClient()

        # Widgets updated dynamically
        self.header_widget = Static("")
        self.status_widget = Static("")
        self.metrics_widget = Static("")
        self.crash_widget = Static("")

        self._ws_task = None

    # --------------------------------------------------
    # Layout
    # --------------------------------------------------

    def compose(self):

        with Horizontal():

            yield Sidebar(id="sidebar")

            with Vertical(id="main"):

                yield Container(
                    self.header_widget,
                    self.status_widget,
                    self.metrics_widget,
                    self.crash_widget,
                    id="content"
                )

                yield Footer()

    # --------------------------------------------------
    # Lifecycle
    # --------------------------------------------------

    def on_mount(self):
        self.refresh_data()
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
        if event.get("type") == "fuzzer_update":
            fuzzer = event.get("fuzzer", {})
            if fuzzer.get("id") == self.fuzzer_id:
                self._update_from_payload(fuzzer)

    # --------------------------------------------------
    # Data Refresh
    # --------------------------------------------------

    def refresh_data(self):
        fuzzers = self.api.list_fuzzers()
        for f in fuzzers:
            if f["id"] == self.fuzzer_id:
                self._update_from_payload(f)
                break

    # --------------------------------------------------
    # UI Update Logic
    # --------------------------------------------------

    def _update_from_payload(self, data):

        state = data.get("state", "unknown")
        pid = data.get("pid", "n/a")
        campaign_id = data.get("campaign_id", "n/a")
        fuzzer_type = data.get("fuzzer_type", "n/a")
        started_at = data.get("started_at", "n/a")
        last_heartbeat = data.get("last_heartbeat", "n/a")

        exec_sec = data.get("exec_per_sec", 0)
        corpus = data.get("corpus_size", 0)
        coverage = data.get("coverage", 0)
        crashes = data.get("crash_count", 0)

        state_color = {
            "running": "green",
            "stopped": "yellow",
            "crashed": "red",
        }.get(state, "white")

        # ---------------- HEADER ----------------

        self.header_widget.update(
            f"[b]Fuzzer Detail[/b]\n"
            f"ID: {self.fuzzer_id}\n"
            f"Campaign: {campaign_id}\n"
            f"Type: {fuzzer_type}"
        )

        # ---------------- STATUS ----------------

        self.status_widget.update(
            f"\n[b]Status[/b]\n"
            f"State: [{state_color}]{state}[/{state_color}]\n"
            f"PID: {pid}\n"
            f"Started: {started_at}\n"
            f"Last heartbeat: {last_heartbeat}"
        )

        # ---------------- METRICS ----------------

        self.metrics_widget.update(
            f"\n[b]Metrics[/b]\n"
            f"Exec/sec: {exec_sec}\n"
            f"Corpus size: {corpus}\n"
            f"Coverage: {coverage}%"
        )

        # ---------------- CRASHES ----------------

        self.crash_widget.update(
            f"\n[b]Crashes[/b]\n"
            f"Total crashes: {crashes}"
        )

    # --------------------------------------------------
    # Navigation
    # --------------------------------------------------

    def action_go_back(self):
        self.app.pop_screen()
