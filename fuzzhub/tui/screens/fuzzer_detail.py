"""
File: fuzzhub/tui/screens/fuzzer_detail.py
"""

import asyncio
import json
import websockets

from textual.screen import Screen
from textual.binding import Binding
from textual.containers import Vertical
from textual.widgets import Static, Footer

from fuzzhub.tui.api_client import APIClient


class FuzzerDetailScreen(Screen):

    BINDINGS = [
        Binding("escape", "back", "Back"),
        Binding("s", "start", "Start"),
        Binding("t", "stop", "Stop"),
        Binding("r", "restart", "Restart"),
    ]

    def __init__(self, fuzzer_id: str):
        super().__init__()
        self.fuzzer_id = fuzzer_id
        self.api = APIClient()
        self.detail_text = Static("Loading...", id="detail_text")
        self._ws_task = None

    def compose(self):
        with Vertical(id="detail-main"):
            yield self.detail_text

        yield Footer()

    async def on_mount(self):
        await self.refresh_data()
        self._ws_task = asyncio.create_task(self.listen_ws())

    async def on_unmount(self):
        if self._ws_task:
            self._ws_task.cancel()

    # --------------------------------------------------
    # Live Updates
    # --------------------------------------------------

    async def listen_ws(self):
        uri = "ws://127.0.0.1:8000/ws"

        while True:
            try:
                async with websockets.connect(uri) as websocket:
                    while True:
                        message = await websocket.recv()
                        event = json.loads(message)

                        if event.get("type") == "fuzzer_update":
                            if event.get("id") == self.fuzzer_id:
                                await self.refresh_data()

            except Exception:
                await asyncio.sleep(2)

    # --------------------------------------------------
    # Data Refresh
    # --------------------------------------------------

    async def refresh_data(self):
        fuzzer = await asyncio.to_thread(
            self.api.get_fuzzer,
            self.fuzzer_id
        )

        if not fuzzer:
            self.detail_text.update("[red]Fuzzer not found[/red]")
            return

        text = f"""
[bold cyan]Fuzzer Details[/bold cyan]
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

[bold]ID:[/bold] {fuzzer.get("id")}
[bold]State:[/bold] {fuzzer.get("state")}
[bold]PID:[/bold] {fuzzer.get("pid")}
[bold]Uptime:[/bold] {fuzzer.get("uptime_seconds")}
[bold]Exec/s:[/bold] {fuzzer.get("exec_per_sec")}
[bold]Corpus:[/bold] {fuzzer.get("corpus_size")}
[bold]Coverage:[/bold] {fuzzer.get("coverage")}
[bold]Crashes:[/bold] {fuzzer.get("crash_count")}

Controls:
  [S] Start   [T] Stop   [R] Restart   [Esc] Back
"""

        self.detail_text.update(text)

    # --------------------------------------------------
    # Actions
    # --------------------------------------------------

    def action_back(self):
        self.app.pop_screen()

    async def action_start(self):
        await asyncio.to_thread(self.api.start_dummy)
        await self.refresh_data()

    async def action_stop(self):
        await asyncio.to_thread(
            self.api.stop_fuzzer,
            self.fuzzer_id
        )
        await self.refresh_data()

    async def action_restart(self):
        await asyncio.to_thread(
            self.api.restart_fuzzer,
            self.fuzzer_id
        )
        await self.refresh_data()
