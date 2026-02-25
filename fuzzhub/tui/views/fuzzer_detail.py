"""
File: fuzzhub/tui/screens/fuzzer_detail.py
"""

from textual.screen import Widget
from textual.widgets import Header, Footer, Static
from textual.containers import Vertical

from fuzzhub.tui.api_client import APIClient


class FuzzerDetailView(Widget):

    BINDINGS = [
        ("escape", "back", "Back"),
    ]

    def __init__(self, fuzzer_id: str):
        super().__init__()
        self.fuzzer_id = fuzzer_id
        self.api = APIClient()
        self.content = Static()

    def compose(self):
        yield Header(show_clock=True)

        with Vertical():
            yield Static(f"[bold cyan]Fuzzer Detail[/bold cyan]\n")
            yield Static(f"ID: {self.fuzzer_id}\n")
            yield self.content

    def on_mount(self):
        self.set_interval(2, self.update_data)
        self.update_data()

    def update_data(self):
        fuzzers = self.api.list_fuzzers()

        for f in fuzzers:
            if f.get("id") == self.fuzzer_id:
                self.content.update(
                    f"""
State: {f.get('state')}
Executions: {f.get('executions')}
Crashes: {f.get('crashes')}
"""
                )
                return

        self.content.update("[red]Fuzzer not found[/red]")

    def action_back(self):
        self.app.pop_screen()

    def action_refresh(self):
        self.update_data()
