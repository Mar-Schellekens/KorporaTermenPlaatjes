import asyncio
from random import random

from textual.app import App, ComposeResult
from textual.reactive import reactive
from textual.widgets import Static, ListView, ListItem, Label, ProgressBar, RichLog, Input
from textual.screen import Screen
from textual import events


class NumberInput(Input):
    """Allow only digits."""
    def on_input_changed(self, event: Input.Changed) -> None:
        cleaned = "".join(ch for ch in self.value if ch.isdigit())
        if cleaned != self.value:
            self.value = cleaned  # enforce numeric characters only

class MessageScreen(Screen):
    """Simple confirmation screen."""

    def __init__(self, message: str) -> None:
        super().__init__(f"{message}\n\nPress Q to quit.", id="message")

    async def on_key(self, event: events.Key) -> None:
        self.query_one(RichLog).write(event)
        if event.key.lower() == "q":
            await self.app.action_quit()





class MenuApp(App):
    progress_value = reactive(0)
    """A simple Textual app with 4 selectable options."""
    def __init__(self):
        super().__init__()
        self.progress = ProgressBar(total=100, show_eta=False)
        self.prompt = None
        self.inputPrompt = None
        self.numberInputPrompt = None
        self.inputCallback = None
        self.list = None
        self.message = None
        self.activeConfigName = None
        self.activeConfig = None
        self.configStateMachine = {}
        self.callback = None
        self.percentage = None
        self.ShowProgressBar = False

    def setActiveConfigName(self, config):
        self.activeConfigName = config

    def setActiveConfig(self, config):
        self.activeConfig = config

    def getActiveConfig(self):
        return self.activeConfig

    def setActiveConfigField(self, field_name, value):
        self.activeConfig[field_name] = value
        self.configStateMachine[field_name] = True

    def setConfigStateMachine(self, name):
        #Could we make this private, and let all cals go through setActiveConfigField?
        self.configStateMachine[name] = True

    def getConfigStateMachine(self):
        return self.configStateMachine

    def setInput(self, prompt, callback):
        self.inputPrompt = prompt
        self.inputCallback = callback

    def setNumberInput(self, prompt, callback):
        self.numberInputPrompt = prompt
        self.inputCallback = callback

    def setList(self, prompt, list, callback):
        self.prompt = prompt
        self.list = list
        self.callback = callback

    def setMessage(self, message):
        self.message = message

    def setShowProgressBar(self, show):
        self.ShowProgressBar = show

    async def on_input_submitted(self, event:Input.Submitted):
        user_text = event.value
        if self.inputCallback is not None:
            await self.inputCallback(user_text)

    async def EmptyScreen(self):
        self.prompt = None
        self.list = None
        self.message = None
        self.inputPrompt = None
        self.numberInputPrompt = None
        self.inputCallback = None
        await self.recompose()

    async def refreshScreen(self):
        await self.recompose()
        try:
            view = self.query_one(ListView)
            if view is not None:
                view.focus()
        except:
            pass

    CSS = """
 /* Root screen styling */

    """


    def compose(self) -> ComposeResult:
        #yield Static("Result:", id="result")
        if self.ShowProgressBar:
            yield self.progress
        if self.activeConfigName is not None:
            yield Static (f"Actieve configuratie: " + self.activeConfigName, id="config")
        if self.message is not None:
            yield Static(self.message, id="result")
        if self.list is not None:
            yield Static(self.prompt, id="prompt")
            yield ListView(
                *[ListItem(Label(opt), name=opt) for opt in self.list],
                id="menu"
            )
        if self.inputPrompt is not None:
            yield Label(self.inputPrompt)
            yield Input(placeholder="type here...", id="input")
            yield Label("", id="output")
        if self.numberInputPrompt is not None:
            yield Label(self.numberInputPrompt)
            yield NumberInput(placeholder="0", id="input")
            yield Label("", id="output")

    async def increment(self, value) -> None:
        self.query_one(ProgressBar).advance(value)

    async def on_mount(self) -> None:
        # Focus the ListView so keyboard navigation works
        self.query_one(ListView).focus()

    async def on_list_view_selected(self, event: ListView.Selected) -> None:
        selected = event.item.query_one(Label).content
        await self.callback(selected)

