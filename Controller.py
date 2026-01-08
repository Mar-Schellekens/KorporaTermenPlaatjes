import json
import pandas
from openpyxl.utils import get_column_letter
from Constants import Acties, StateMachines
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

    async def state_machine(self):
        match Model.get().current_state_machine:
            case StateMachines.MAIN_MENU:
                await self.list_actions()
            case StateMachines.CONFIG:
                await self.new_config_state_machine()
            case StateMachines.CFG_TYPE:
                await self.config_type_state_machine()

    async def list_actions(self):
        actions = [Acties.MAAK_NIEUWE_CONFIG, Acties.LAAD_BESTAANDE_CONFIG]

        if Model.get().active_config_name is not None:
            actions.append(Acties.GENEREER_PLAATJES)

        actions.append(Acties.EXIT)

        View.get().setList("Kies een actie: ", actions, self.callbackActies)
        await View.get().refreshScreen()

    async def callbackActies(self, actie):
        match actie:
            case Acties.EXIT:
                await View.get().action_quit()
            case Acties.LAAD_BESTAANDE_CONFIG:
                await self.prompts.let_user_choose_config(self.cbs.set_active_cfg, self.list_actions)
            case Acties.MAAK_NIEUWE_CONFIG:
                Model.get().current_state_machine = StateMachines.CONFIG
                await self.prompts.test_create_config_file(self.cbs.create_empty_cfg)
            case Acties.GENEREER_PLAATJES:
                with open(Model.get().active_config_name) as f:
                    cfg = json.load(f)
                termen = load_terms(cfg)
                await View.get().EmptyScreen()
                View.get().setShowProgressBar(True, self.list_actions)
                await View.get().refreshScreen()
                await self.generating_pictures_state_machine(termen)

    async def generating_pictures_state_machine(self, termen):
        percent = 1 / len(termen) * 100
        with open(Model.get().active_config_name) as f:
            cfg = json.load(f)
        if len(termen) > 1:
            await self.prompts.slowTaskPrompt(termen, cfg, percent, self.generating_pictures_state_machine)
        else:
            await self.list_actions()

    async def new_config_state_machine(self):
        state_machine = Model.get().getConfigStateMachine()
        if "input_file_name" not in state_machine:
            await self.prompts.prompt_input_input_file_new(self.cbs.let_user_pick_excel_input)
        elif "file_has_header" not in state_machine:
            await self.prompts.prompt_input_header_new(self.cbs.set_header_in_cfg)
        elif "column_name" not in state_machine:
            await self.prompts.prompt_input_termen_new(self.cbs.set_column_name_in_cfg)
        elif "width" not in state_machine:
            await self.prompts.prompt_input_width_new(self.cbs.set_width_in_cfg)
        elif "height" not in state_machine:
            await self.prompts.prompt_input_height_new(self.cbs.set_height_in_cfg)
        elif "background_color" not in state_machine:
            await self.prompts.prompt_input_background_color(self.cbs.set_bg_color_in_cfg)
        elif "font" not in state_machine:
            await self.prompts.prompt_input_font(self.cbs.set_font_in_cfg)
        elif "font_size" not in state_machine:
            await self.prompts.prompt_input_font_size(self.cbs.set_font_size_in_cfg)
        elif "margin" not in state_machine:
            await self.prompts.prompt_input_margin(self.cbs.set_margin_in_cfg)
        elif "types" not in state_machine:
            await self.prompts.prompt_input_types(self.cbs.handle_new_cfg_type_input)
        else:
            df = pandas.read_excel(Model.get().activeConfig["input_file_name"])
            col_idx = df.columns.get_loc(Model.get().activeConfig["column_name"]) + 1  # openpyxl is 1-based
            Model.get().activeConfig["column_letter"] = get_column_letter(col_idx)
            save_config(Model.get().activeConfig, Model.get().active_config_name)

            Model.get().current_state_machine = StateMachines.MAIN_MENU
            await self.state_machine()

    async def config_type_state_machine(self):
        state_machine = Model.get().getTypeStateMachine()
        if "name" not in state_machine:
            await self.prompts.prompt_input_type_name(self.cbs.set_type_name_in_cfg)
        elif "generated_image_text_color" not in state_machine:
            await self.prompts.prompt_input_type_text_color(self.cbs.set_type_text_color_in_cfg)
        elif "method" not in state_machine:
            await self.prompts.prompt_input_type_method(self.cbs.set_type_method_in_cfg)
        elif "column" not in state_machine:
            await self.prompts.prompt_input_type_column(self.cbs.set_type_column_field_in_cfg)
        elif "excel_file_cell_color" not in state_machine:
            await self.prompts.prompt_input_type_cell_color(self.cbs.set_type_cell_color_type_in_cfg)
        else:
            Model.get().setConfigType()
            Model.get().current_state_machine = StateMachines.CONFIG
            await self.state_machine()
