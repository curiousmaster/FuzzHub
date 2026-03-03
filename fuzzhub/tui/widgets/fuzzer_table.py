"""
File: fuzzhub/tui/widgets/fuzzer_table.py
"""

from textual.widgets import DataTable
from textual.binding import Binding
from textual import events

from fuzzhub.utils.logging import get_logger

logger = get_logger(__name__)


class FuzzerTable(DataTable):

    can_focus: True

    BINDINGS = [
        Binding("enter", "open_selected", "Open"),
    ]

    def on_mount(self):
        self.add_columns("ID", "State", "Execs", "Crashes")
        self.cursor_type = "row"
        self.show_cursor = True
        self.zebra_stripes = True

    # --------------------------------------------------

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
                key=f.get("id"),
            )

    def action_open_selected(self):
        if self.cursor_row is None:
            return

        row = self.get_row_at(self.cursor_row)
        fuzzer_id = row[0]

        from fuzzhub.tui.screens.fuzzer_detail import FuzzerDetailScreen
        self.app.push_screen(FuzzerDetailScreen(fuzzer_id))


    # --------------------------------------------------
    # Manual Enter Handler (Reliable)
    # --------------------------------------------------
    def on_data_table_cell_selected(self, event):
        print("DEBUG: Cell selected event fired")

        if event.coordinate is None:
            return

        row_index = event.coordinate.row

        try:
            row = self.get_row_at(row_index)
        except Exception:
            return

        if not row:
            return

        fuzzer_id = row[0]
        print("DEBUG: Opening fuzzer:", fuzzer_id)

        from fuzzhub.tui.screens.fuzzer_detail import FuzzerDetailScreen

        self.app.push_screen(
            FuzzerDetailScreen(fuzzer_id)
        )
