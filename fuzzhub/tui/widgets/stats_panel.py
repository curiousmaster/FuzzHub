"""
File: fuzzhub/tui/widgets/stats_panel.py
"""

from textual.widgets import Static


class StatsPanel(Static):

    def update_stats(self, fuzzers):
        total = len(fuzzers)
        total_crashes = sum(f["crash_count"] for f in fuzzers)

        content = (
            f"[bold cyan]Active Fuzzers:[/bold cyan] {total}\n"
            f"[bold red]Total Crashes:[/bold red] {total_crashes}\n"
        )

        self.update(content)
