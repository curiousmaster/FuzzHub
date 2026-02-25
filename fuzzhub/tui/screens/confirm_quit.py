"""
File: fuzzhub/tui/screens/confirm_quit.py
"""

from textual.screen import ModalScreen
from textual.widgets import Static
from textual.containers import Vertical, Horizontal
from textual.binding import Binding
from textual.reactive import reactive


class ConfirmQuitScreen(ModalScreen):

    BINDINGS = [
        Binding("left", "select_left", ""),
        Binding("right", "select_right", ""),
        Binding("enter", "activate", "Select"),
        Binding("y", "confirm", "Yes"),
        Binding("n", "cancel", "No"),
        Binding("escape", "cancel", "Cancel"),
    ]

    selected = reactive("yes")

    def compose(self):
        with Vertical(classes="confirm-box"):
            yield Static("Quit FuzzHub", classes="confirm-title")

            with Horizontal(classes="confirm-buttons"):
                self.btn_yes = Static("  Y  Confirm  ", classes="confirm-btn yes")
                self.btn_no = Static("  N  Cancel   ", classes="confirm-btn no")
                yield self.btn_yes
                yield self.btn_no

    def on_mount(self):
        self.update_selection()

    def update_selection(self):
        if self.selected == "yes":
            self.btn_yes.add_class("selected")
            self.btn_no.remove_class("selected")
        else:
            self.btn_no.add_class("selected")
            self.btn_yes.remove_class("selected")

    def action_select_left(self):
        self.selected = "yes"
        self.update_selection()

    def action_select_right(self):
        self.selected = "no"
        self.update_selection()

    def action_activate(self):
        if self.selected == "yes":
            self.action_confirm()
        else:
            self.action_cancel()

    def action_confirm(self):
        self.app.exit()

    def action_cancel(self):
        self.app.pop_screen()
