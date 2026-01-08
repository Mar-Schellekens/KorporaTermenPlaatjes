import json
import pandas
from openpyxl.utils import get_column_letter
from Constants import Acties, StateMachines, CfgFields
from CreatePicture import create_picture_async
from Utils import save_config
from View import View
from ViewInputPrompter import ViewInputPrompter
from ControlInputHandler import ControlInputHandler
from LoadTerms import load_terms
from Model import Model

class Controller:
    def __init__(self):
        self.cbs = ControlInputHandler(self)
        self.prompts = ViewInputPrompter()
        self.model = Model.get()

    async def state_machine(self):
        handlers = {
            StateMachines.MAIN_MENU: self.main_menu,
            StateMachines.CONFIG: self.config_state_machine,
            StateMachines.CFG_TYPE: self.config_type_state_machine
        }

        handler = handlers.get(self.model.current_state_machine)
        if not handler:
            raise RuntimeError(f"No handler for state {self.model.current_state_machine}")
        await handler()

    async def main_menu(self):

        actions = [Acties.MAAK_NIEUWE_CONFIG, Acties.LAAD_BESTAANDE_CONFIG]
        if self.model.active_config_name is not None:
            actions.append(Acties.GENEREER_PLAATJES)
        actions.append(Acties.EXIT)

        await self.prompts.show_main_menu(actions, self.handle_main_menu_choice)

    async def handle_main_menu_choice(self, actie):
        match actie:
            case Acties.EXIT:
                await self.prompts.exit()
            case Acties.LAAD_BESTAANDE_CONFIG:
                await self.prompts.user_choose_config(self.cbs.set_active_cfg, self.main_menu)
            case Acties.MAAK_NIEUWE_CONFIG:
                self.model.current_state_machine = StateMachines.CONFIG
                await self.prompts.name_new_config(self.cbs.create_empty_cfg)
            case Acties.GENEREER_PLAATJES:
                with open(self.model.active_config_name) as f:
                    cfg = json.load(f)
                termen = load_terms(cfg)
                await self.prompts.show_progress_bar(self.state_machine)
                await self.generate_images(termen)

    async def generate_images(self, termen):
        with open(self.model.active_config_name) as f:
            cfg = json.load(f)

        if not termen:
            await self.main_menu()
            return

        for counter, term in enumerate(termen, start=1):
            await create_picture_async(term, cfg)
            await View.get().set_loading_bar(counter / len(termen) * 100)

        await View.get().set_loading_bar(0, finished=True)

    async def config_state_machine(self):
        state_machine = self.model.get_config_state_machine()

        steps = [
            (CfgFields.INPUT_FILE_NAME, self.prompts.input_excel_file, self.cbs.let_user_pick_excel_input),
            (CfgFields.FILE_HAS_HEADER, self.prompts.header, self.cbs.set_header_in_cfg),
            (CfgFields.COLUMN_NAME, self.prompts.column_name, self.cbs.set_column_name_in_cfg),
            (CfgFields.WIDTH, self.prompts.width, self.cbs.set_width_in_cfg),
            (CfgFields.HEIGHT, self.prompts.height, self.cbs.set_height_in_cfg),
            (CfgFields.BACKGROUND_COLOR, self.prompts.background_color, self.cbs.set_bg_color_in_cfg),
            (CfgFields.FONT, self.prompts.font, self.cbs.set_font_in_cfg),
            (CfgFields.FONT_SIZE, self.prompts.font_size, self.cbs.set_font_size_in_cfg),
            (CfgFields.MARGIN, self.prompts.margin, self.cbs.set_margin_in_cfg),
            (CfgFields.TYPES, self.prompts.types, self.cbs.handle_new_cfg_type_input),
        ]

        for field, prompt, cb in steps:
            if field not in state_machine:
                await prompt(cb)
                return

        await self.finalize_config()

    def compute_column_letter(self):
        df = pandas.read_excel(self.model.active_config[CfgFields.INPUT_FILE_NAME])
        col_idx = df.columns.get_loc(self.model.active_config[CfgFields.COLUMN_NAME]) + 1
        return get_column_letter(col_idx)

    async def finalize_config(self):
        self.model.active_config[CfgFields.COLUMN_LETTER] = self.compute_column_letter()

        save_config(self.model.active_config, self.model.active_config_name)
        self.model.current_state_machine = StateMachines.MAIN_MENU
        await self.state_machine()

    async def config_type_state_machine(self):
        state_machine = self.model.get_type_state_machine()

        steps = [
            (CfgFields.TYPES_NAME, self.prompts.type_name, self.cbs.set_type_name_in_cfg),
            (CfgFields.TYPES_GENERATED_IMAGE_TEXT_COLOR, self.prompts.type_text_color, self.cbs.set_type_text_color_in_cfg),
            (CfgFields.TYPES_METHOD, self.prompts.type_method, self.cbs.set_type_method_in_cfg),
            (CfgFields.TYPES_COLUMN, self.prompts.type_column, self.cbs.set_type_column_field_in_cfg),
            (CfgFields.TYPES_EXCEL_FILE_CELL_COLOR, self.prompts.cell_color_type, self.cbs.set_type_cell_color_type_in_cfg),
        ]

        for key, prompt_fn, cb in steps:
            if key not in state_machine:
                await prompt_fn(cb)
                return

        self.model.set_config_type()
        self.model.current_state_machine = StateMachines.CONFIG
        await self.state_machine()
