"""
File: fuzzhub/tui/screens/fuzzer_detail.py
"""

import asyncio
from textual.screen import Screen
from textual.binding import Binding
from textual.widgets import Static, Footer

from fuzzhub.tui.api_client import APIClient


class FuzzerDetailScreen(Screen):

    BINDINGS = [
        Binding("escape", "back", "Back"),
    ]

    def __init__(self, fuzzer_id: str):
        super().__init__()
        self.fuzzer_id = fuzzer_id
        self.api = APIClient()

    def compose(self):
        yield Static("Loading...", id="detail_text")
        yield Footer()

    async def on_mount(self):
        fuzzer = await asyncio.to_thread(
            self.api.get_fuzzer,
            self.fuzzer_id
        )

        if not fuzzer:
            self.app.pop_screen()
            return

        text = f"""
Fuzzer Details
==============

ID: {fuzzer.get("id")}
State: {fuzzer.get("state")}
Executions: {fuzzer.get("executions")}
Crashes: {fuzzer.get("crashes")}
"""

        self.query_one("#detail_text", Static).update(text)

    def action_back(self):
        self.app.pop_screen()
