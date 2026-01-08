import json
import pandas
from openpyxl.utils import get_column_letter
from Constants import Acties
from CreateInputConfig import save_config
from ViewInputPrompter import ViewInputPrompter
from ControlInputHandler import ControlInputHandler
from LoadTerms import load_terms
from Model import Model
from View import View

class Controller:
    def __init__(self):
        self.cbs = ControlInputHandler(self)
        self.prompts = ViewInputPrompter()

    async def listActions(self):
        actions = [Acties.MAAK_NIEUWE_CONFIG]

        if Model.get().input_config_file_name is not None:
            actions.append(Acties.VERANDER_CONFIG)

        actions.append(Acties.LAAD_BESTAANDE_CONFIG)

        if Model.get().input_config_file_name is not None:
            actions.append(Acties.GENEREER_PLAATJES)

        actions.append(Acties.EXIT)

        View.get().setList("Kies een actie: ", actions, self.callbackActies)
        Model.get().setActiveConfigName(Model.get().input_config_file_name)
        await View.get().refreshScreen()

    async def callbackActies(self, actie):
        match actie:
            case Acties.EXIT:
                await View.get().action_quit()
            case Acties.LAAD_BESTAANDE_CONFIG:
                await self.prompts.let_user_choose_config(self.cbs.callback_let_user_choose_config, self.listActions)
            case Acties.VERANDER_CONFIG:
                print("): no workie")
            case Acties.MAAK_NIEUWE_CONFIG:
                await self.prompts.test_create_config_file(self.cbs.test_create_config_file_name_found_cb)
            case Acties.GENEREER_PLAATJES:
                with open(Model.get().input_config_file_name) as f:
                    cfg = json.load(f)
                termen = load_terms(cfg)
                await View.get().EmptyScreen()
                View.get().setShowProgressBar(True, self.listActions)
                await View.get().refreshScreen()
                await self.generating_pictures_state_machine(termen)

    async def generating_pictures_state_machine(self, termen):
        percent = 1 / len(termen) * 100
        with open(Model.get().input_config_file_name) as f:
            cfg = json.load(f)
        if len(termen) > 1:
            await self.prompts.slowTaskPrompt(termen, cfg, percent, self.generating_pictures_state_machine)
        else:
            await self.listActions()

    async def config_state_machine(self):
        state_machine = Model.get().getConfigStateMachine()
        if "input_file_name" not in state_machine:
            await self.prompts.prompt_input_input_file_new(self.cbs.prompt_input_file_new_cb)
        elif "file_has_header" not in state_machine:
            await self.prompts.prompt_input_header_new(self.cbs.prompt_input_header_new_cb)
        elif "column_name" not in state_machine:
            await self.prompts.prompt_input_termen_new(self.cbs.prompt_input_termen_new_cb)
        elif "width" not in state_machine:
            await self.prompts.prompt_input_width_new(self.cbs.prompt_input_width_new_cb)
        elif "height" not in state_machine:
            await self.prompts.prompt_input_height_new(self.cbs.prompt_input_height_new_cb)
        elif "background_color" not in state_machine:
            await self.prompts.prompt_input_background_color(self.cbs.prompt_input_background_color_cb)
        elif "font" not in state_machine:
            await self.prompts.prompt_input_font(self.cbs.prompt_input_font_cb)
        elif "font_size" not in state_machine:
            await self.prompts.prompt_input_font_size(self.cbs.prompt_input_font_size_cb)
        elif "margin" not in state_machine:
            await self.prompts.prompt_input_margin(self.cbs.prompt_input_margin_cb)
        elif "types" not in state_machine:
            await self.prompts.prompt_input_types(self.cbs.prompt_input_types_cb)
        else:
            df = pandas.read_excel(Model.get().activeConfig["input_file_name"])
            col_idx = df.columns.get_loc(Model.get().activeConfig["column_name"]) + 1  # openpyxl is 1-based
            Model.get().activeConfig["column_letter"] = get_column_letter(col_idx)
            save_config(Model.get().activeConfig, Model.get().activeConfigName)
            await self.listActions()

    async def config_type_state_machine(self):
        state_machine = Model.get().getTypeStateMachine()
        if "name" not in state_machine:
            await self.prompts.prompt_input_type_name(self.cbs.prompt_input_type_name_cb)
        elif "generated_image_text_color" not in state_machine:
            await self.prompts.prompt_input_type_text_color(self.cbs.prompt_input_type_text_color_cb)
        elif "method" not in state_machine:
            await self.prompts.prompt_input_type_method(self.cbs.prompt_input_type_method_cb)
        elif "column" not in state_machine:
            await self.prompts.prompt_input_type_column(self.cbs.prompt_input_type_column_cb)
        elif "excel_file_cell_color" not in state_machine:
            await self.prompts.prompt_input_type_cell_color(self.cbs.prompt_input_type_cell_color_cb)
        else:
            Model.get().setConfigType()
            await self.config_state_machine()
