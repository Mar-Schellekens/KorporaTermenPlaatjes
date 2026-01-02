from time import sleep

from textual import  events
from textual.app import App, ComposeResult
from textual.widgets import RichLog, ListView, ListItem, Label, Input

class NumberInput(Input):
    """Allow only digits."""
    def on_input_changed(self, event: Input.Changed) -> None:
        cleaned = "".join(ch for ch in self.value if ch.isdigit())
        if cleaned != self.value:
            self.value = cleaned  # enforce numeric characters only

class InputApp(App):
    CSS = """
    /* Root screen styling */

       """

    def __init__(self, title: str) -> None:
        super().__init__()
        self.toggleInput = False
        self.list = ["apple", "pear", "banana"]
        self.query = "What is the new name?"

    def compose(self) -> ComposeResult:
        if self.toggleInput:
            yield Label(self.query)
            #yield Input(placeholder="type here...", id="input")
            yield NumberInput(id="num", placeholder="0")
            yield Label("", id="output")
        else:
            yield ListView(
                *[ListItem(Label(opt), name=opt) for opt in self.list],
                id="menu"
            )

    async def on_list_view_selected(self, event: ListView.Selected) -> None:
        selected = event.item.query_one(Label).content
        self.toggleInput = True
        await self.recompose()

    async def on_input_submitted(self, event:Input.Submitted):
        user_text = event.value
        output = self.query_one('#output', Label)
        output.update(f"You typed: {user_text}")


if __name__ == '__main__':
    app = InputApp("blub")
    app.run()
