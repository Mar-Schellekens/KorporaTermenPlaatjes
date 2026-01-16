import traceback

from textual.app import App, ComposeResult
from textual.reactive import reactive
from textual.widgets import Static, ListView, ListItem, Label, ProgressBar, RichLog, Input, Button

import Constants
from Constants import ViewState, StateMachines
from Exceptions import TooSmallException
from Model import Model
from Singleton import Singleton
from Utils import best_text_color


class NumberInput(Input):
    """Allow only digits."""
    def on_input_changed(self, event: Input.Changed) -> None:
        cleaned = "".join(ch for ch in self.value if ch.isdigit())
        if cleaned != self.value:
            self.value = cleaned  # enforce numeric characters only

@Singleton
class View(App):
    progress_value = reactive(0)
    """A simple Textual app with 4 selectable options."""
    def __init__(self):
        super().__init__()
        self.list_colors = None
        self.progress = ProgressBar(total=100, show_eta=False)

        self.callback = None

        self.prompt = None
        self.list = None
        self.buttonText = None
        self.type_names = None

        self.state: ViewState = ViewState.EMPTY

        self.controller = None

        self.success_message = None
        self.show_success_message = False

        self.error_message = None
        self.show_error_message = False


    def set_controller(self, controller):
        self.controller = controller

    def set_success_message(self, success_message):
        self.success_message = success_message
        self.show_success_message = True

    def set_error_message(self, error_message):
        self.error_message = error_message
        self.show_error_message = True

    def set_text_input(self, prompt, callback):
        self.prompt = prompt
        self.callback = callback
        self.state = ViewState.TEXT_INPUT



    def set_number_input(self, prompt, callback):
        self.prompt = prompt
        self.callback= callback
        self.state = ViewState.NUMBER_INPUT

    def set_button_input(self, prompt, button_text, callback):
        self.buttonText = button_text
        self.prompt = prompt
        self.callback = callback
        self.state = ViewState.BUTTON

    def set_type_overview(self, type_names: list[str], prompt: str, lst: list, callback):
        self.prompt = prompt
        self.list = lst
        self.callback = callback
        self.type_names = "\n".join(type_names)
        self.state = ViewState.TYPE_OVERVIEW


    def set_list(self, prompt, lst, callback, colors=None):
        self.prompt = prompt
        self.list = lst
        if colors is not None:
            if len(colors) == len(lst):
                self.list_colors = colors
        else:
            self.list_colors = None
        self.callback = callback
        self.state = ViewState.LIST

    def set_message(self, message):
        self.prompt = message
        self.state = ViewState.MESSAGE

    def set_show_progress_bar(self, show, cb):
        self.callback = cb
        self.state = ViewState.PROGRESS

    async def on_input_submitted(self, event:Input.Submitted):
        user_text = event.value
        if self.callback is not None:
            await self.callback(user_text)

    async def on_button_pressed(self, event: Button.Pressed):
        if self.callback is not None:
            await self.callback()

    async def empty_screen(self):
        self.state = ViewState.EMPTY

    async def refresh_screen(self):
        await self.recompose()
        if self.state == ViewState.TEXT_INPUT:
            view = self.query_one(Input)
            if view is not None:
                view.focus()

        if self.state == ViewState.LIST or self.state == ViewState.TYPE_OVERVIEW:
            view = self.query_one(ListView)
            if view is not None:
                view.focus()

        if self.state == ViewState.NUMBER_INPUT:
            view = self.query_one(NumberInput)
            if View is not None:
                view.focus()

    async def set_exception(self, error:Exception, trcbck):
        self.set_error_message("Onverwachte fout. Als dit probleem zich blijft voordoen, neem dan contact op met de ontwikkelaar en geef de volgende foutmelding door:  \n\n\n" + str(error) \
                               + "Traceback:" + trcbck)

    async def on_error(self, error:Exception) -> None:
        if error is TooSmallException:
            self.set_error_message(str(error))
        await self.set_exception(error, traceback.print_exc())

    def get_list_items(self):
        if self.list_colors is not None:
            if len(self.list_colors) == len(self.list):
                return [ListItem(Label(f"[{best_text_color(color)} on {color}]{opt}[/]"), name=opt) for opt, color in zip(self.list, self.list_colors)]

        return [ListItem(Label(opt), name=opt) for opt in self.list]

    def compose(self) -> ComposeResult:
        if self.show_success_message:
            yield Static("[green]" + self.success_message+ "[/green]")
            self.show_success_message = False

        if self.show_error_message:
            yield Static("[red]" + self.error_message+ "[/red]")
            self.show_error_message = False

        if Model.get().get_active_cfg_name() is not None:
            yield Static(f"Actieve configuratie: " + Model.get().get_active_cfg_name(), id="config")

        match self.state:
            case ViewState.PROGRESS:
                yield self.progress
            case ViewState.MESSAGE:
                yield Static(self.prompt)
            case ViewState.LIST:
                yield Static(self.prompt)
                list_items = self.get_list_items()
                yield ListView(*list_items)
            case ViewState.TYPE_OVERVIEW:
                if len(self.type_names)>0:
                    yield Static("De volgende types zijn al aanwezig: \n")
                    yield Static(self.type_names + "\n")
                yield Static(self.prompt)
                yield ListView(
                    *[ListItem(Label(opt), name=opt) for opt in self.list])
            case ViewState.TEXT_INPUT:
                yield Label(self.prompt)
                yield Input(placeholder="type here...")
            case ViewState.NUMBER_INPUT:
                yield Label(self.prompt)
                yield NumberInput(placeholder="0")
            case ViewState.BUTTON:
                yield Label(self.prompt)
                yield Button(self.buttonText)

    async def set_loading_bar(self, percentage, finished=False):
        if finished:
            self.progress.update(progress=0)
            await self.empty_screen()
            await self.callback()
        else:
            self.progress.update(progress = percentage)


    async def on_mount(self) -> None:
        await self.controller.state_machine()

    async def on_list_view_selected(self, event: ListView.Selected) -> None:
       try:
            selected = event.item.query_one(Label).content
            await self.callback(selected)
       except TooSmallException as e:
           self.set_error_message(str(e))
           Model.get().current_statemachine = Constants.StateMachines.MAIN_MENU
           await self.controller.state_machine()
       except Exception as e:
            await self.set_exception(e, traceback.format_exc())
            await self.refresh_screen()
