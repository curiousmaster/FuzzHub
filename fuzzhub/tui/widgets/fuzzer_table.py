"""
File: fuzzhub/tui/widgets/fuzzer_table.py
"""

from textual.widgets import DataTable
from textual import events


class FuzzerTable(DataTable):

    def on_mount(self):
        self.add_columns("ID", "State", "Execs", "Crashes")
        self.cursor_type = "row"
        self.zebra_stripes = True

    def update_data(self, fuzzers):
        self.clear()

        for f in fuzzers:
            state = f.get("state", "")

            if state == "running":
                state = "[green]running[/green]"
            elif state == "stopped":
                state = "[yellow]stopped[/yellow]"
            elif state == "crashed":
                state = "[red]crashed[/red]"

            self.add_row(
                f.get("id", ""),
                state,
                str(f.get("executions", 0)),
                str(f.get("crashes", 0)),
            )

    async def on_key(self, event: events.Key):
        if event.key == "enter":
            if self.cursor_row is not None:
                row = self.get_row_at(self.cursor_row)
                fuzzer_id = row[0]

                self.app.show_fuzzer_detail(fuzzer_id)
