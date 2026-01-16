import json
import pandas
from openpyxl.utils import get_column_letter
import Constants
import Utils
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
        self.reset_config_state_machines()

        actions = [Acties.MAAK_NIEUWE_CONFIG, Acties.LAAD_BESTAANDE_CONFIG]
        if self.model.get_active_cfg_name() is not None:
            actions.append(Acties.GENEREER_PLAATJES)
            actions.append(Acties.WIJZIG_CONFIG)
        actions.append(Acties.EXIT)

        await self.prompts.show_main_menu(actions, self.handle_main_menu_choice)

    async def handle_main_menu_choice(self, actie):
        match actie:
            case Acties.EXIT:
                await self.prompts.exit()
            case Acties.LAAD_BESTAANDE_CONFIG:
                await self.prompts.user_choose_config(self.cbs.set_active_cfg, self.main_menu)
            case Acties.MAAK_NIEUWE_CONFIG:
                self.model.set_active_cfg_path(None)
                self.model.current_state_machine = StateMachines.CONFIG
                await self.prompts.name_new_config(self.cbs.create_cfg)
            case Acties.WIJZIG_CONFIG:
                self.model.current_state_machine = StateMachines.CONFIG
                await self.prompts.show_modify_config(self.cbs.start_modify_field)
            case Acties.GENEREER_PLAATJES:
                with open(self.model.active_config_path) as f:
                    cfg = json.load(f)
                termen = load_terms(cfg)
                await self.prompts.show_progress_bar(self.state_machine)
                await self.generate_images(termen)

    async def generate_images(self, termen):
        with open(self.model.active_config_path) as f:
            cfg = json.load(f)

        if not termen:
            await self.main_menu()
            return

        for counter, term in enumerate(termen, start=1):
            await create_picture_async(term, cfg)
            await View.get().set_loading_bar(counter / len(termen) * 100)

        output_folder = Utils.add_base_path(Constants.OUTPUT_FOLDER)
        View.get().set_success_message("De plaatjes zijn gegenereerd en aanwezig in folder " + str(output_folder))
        await View.get().set_loading_bar(0, finished=True)


    async def config_state_machine(self):
        state_machine = self.model.get_config_state_machine()

        steps = [
            (CfgFields.INPUT_FILE_NAME.value, self.prompts.input_excel_file, self.cbs.let_user_pick_excel_input),
            (CfgFields.FILE_HAS_HEADER.value, self.prompts.header, self.cbs.set_header_in_cfg),
            (CfgFields.COLUMN_NAME.value, self.prompts.column_name, self.cbs.set_column_name_in_cfg),
            (CfgFields.WIDTH.value, self.prompts.width, self.cbs.set_width_in_cfg),
            (CfgFields.HEIGHT.value, self.prompts.height, self.cbs.set_height_in_cfg),
            (CfgFields.BACKGROUND_COLOR.value, self.prompts.background_color, self.cbs.set_bg_color_in_cfg),
            (CfgFields.FONT.value, self.prompts.font, self.cbs.set_font_in_cfg),
            (CfgFields.FONT_SIZE.value, self.prompts.font_size, self.cbs.set_font_size_in_cfg),
            (CfgFields.MARGIN.value, self.prompts.margin, self.cbs.set_margin_in_cfg),
            (CfgFields.TYPES.value, self.prompts.types, self.cbs.handle_new_cfg_type_input),
        ]

        for field, prompt, cb in steps:
            if field not in state_machine:
                await prompt(cb)
                return

        await self.finalize_config()

    def reset_config_state_machines(self):
        Model.get().config_state_machine = {}
        Model.get().type_state_machine = {}

    def compute_column_letter(self):
        df = pandas.read_excel(self.model.active_config[CfgFields.INPUT_FILE_NAME.value])
        col_idx = df.columns.get_loc(self.model.active_config[CfgFields.COLUMN_NAME.value]) + 1
        return get_column_letter(col_idx)

    async def finalize_config(self):
        self.model.active_config[CfgFields.COLUMN_LETTER.value] = self.compute_column_letter()

        save_config(self.model.active_config, self.model.get_active_cfg_name())
        self.model.current_state_machine = StateMachines.MAIN_MENU
        await self.state_machine()

    async def config_type_state_machine(self):
        state_machine = self.model.get_type_state_machine()

        steps = [
            (CfgFields.TYPES_NAME.value, self.prompts.type_name, self.cbs.set_type_name_in_cfg),
            (CfgFields.TYPES_GENERATED_IMAGE_TEXT_COLOR.value, self.prompts.type_text_color, self.cbs.set_type_text_color_in_cfg),
            (CfgFields.TYPES_METHOD.value, self.prompts.type_method, self.cbs.set_type_method_in_cfg),
            (CfgFields.TYPES_COLUMN.value, self.prompts.type_column, self.cbs.set_type_column_field_in_cfg),
        ]

        if CfgFields.TYPES_METHOD.value in Model.get().new_config_type:
            if Model.get().new_config_type[CfgFields.TYPES_METHOD.value] == Constants.TypesMethod.CEL_KLEUR:
                cell_color = (CfgFields.TYPES_EXCEL_FILE_CELL_COLOR.value, self.prompts.cell_color_type, self.cbs.set_type_cell_color_type_in_cfg)
                steps.append(cell_color)
            elif Model.get().new_config_type[CfgFields.TYPES_METHOD.value] == Constants.TypesMethod.CEL_INHOUD:
                match_string = (CfgFields.TYPES_MATCH_STRING.value, self.prompts.cell_content_type, self.cbs.set_match_string_in_cfg)
                steps.append(match_string)
            else:
                raise Exception("Types method field in active config somehow has a non-supported value.")

        for key, prompt_fn, cb in steps:
            if key not in state_machine:
                await prompt_fn(cb)
                return

        self.model.set_config_type()
        self.model.current_state_machine = StateMachines.CONFIG
        await self.state_machine()
