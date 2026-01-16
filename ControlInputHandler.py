#This is an interface between control and view, part of the control layer, and should never import ViewInputPrompter to prevent circular import.
import re
from pathlib import Path
from tkinter import filedialog
from typing import List

import numpy as np
import pandas
from PIL import ImageFont

import Constants
import Utils
from Constants import CfgFields, TypesMenu, StateMachines, Validations
from Model import Model
from RulesConfig import get_all_colors_in_column
from Utils import convert_excel_colors_to_string, load_excel_file, save_config, is_valid_hex_color
from View import View


class ControlInputHandler:
    def __init__(self, controller):
        self.controller = controller
        self.model = Model.get()

    def validation_excel_column(self, user_input):
        cfg = self.model.get_active_cfg()
        df = pandas.read_excel(cfg[CfgFields.INPUT_FILE_NAME])
        cfg_value = int(np.where(df.columns.values == user_input)[0][0])
        return True, None, cfg_value


    def validation_color_type(self, user_input):
        #remove color formatting
        user_input = re.sub(r"\[.*?\]", "", user_input)

        config = self.model.get_active_cfg()
        file_name = config[CfgFields.INPUT_FILE_NAME]
        workbook, worksheet = load_excel_file(file_name)

        # Find the right values using worksheet and user_input
        config_type = self.model.get_new_config_type()
        column = config_type[CfgFields.TYPES_COLUMN]  # column to scan
        all_colors = get_all_colors_in_column(worksheet, column, workbook)
        all_colors_string, _ = convert_excel_colors_to_string(all_colors)
        idx = all_colors_string.index(user_input)

        cfg_value_1 = all_colors[idx][0]
        cfg_value_2 = all_colors[idx][1]
        return True, None, [cfg_value_1, cfg_value_2]

    def validation_hex_color(self, user_input):
        if not is_valid_hex_color(user_input):
            error = "Dat is geen valide hex kleur"
            return False, error, user_input
        else:
            return True, None, user_input

    def validation_font(self, user_input):
        try:
            ImageFont.truetype(user_input, 12)
            return True, None, user_input
        except IOError:
            error = "Dat is geen valide font op dit systeem"
            return False, error, user_input



    async def set_field_in_cfg(self, field, user_input, validation):
        error = None
        valid = False

        match validation:
            case Validations.EXCEL_COLUMN:
                valid, error, cfg_value = self.validation_excel_column(user_input)
            case Validations.COLOR_CELL_TYPE:
                valid, error, cfg_value = self.validation_color_type(user_input)
            case Validations.TEXT:
                valid = True
                cfg_value = user_input
            case Validations.COLOR:
                valid, error, cfg_value = self.validation_hex_color(user_input)
            case Validations.DICT:
                if isinstance(user_input, dict):
                    valid = True
                    cfg_value = user_input
            case Validations.NUMBER:
                cfg_value = int(user_input)
                valid = True
            case Validations.FONT:
                valid, error, cfg_value = self.validation_font(user_input)
            case _:
                raise Exception("No validation defined.")

        if valid:
            if isinstance(cfg_value, list):
                for f, v in zip(field, cfg_value):
                    self.model.set_active_cfg_field(f, v)
            else:
                self.model.set_active_cfg_field(field, cfg_value)

        if error is not None:
            View.get().set_error_message(error)

        await self.controller.state_machine()


    async def set_active_cfg(self, config_name):
        config_folder_path = Utils.add_base_path(Constants.CONFIG_FOLDER)
        config_path = Path.joinpath(config_folder_path, config_name + ".json")
        self.model.set_active_cfg(config_name)
        self.model.set_active_cfg_path(config_path)
        await self.controller.state_machine()

    async def create_cfg(self, name):
        if not name.lower().endswith(".json"):
            name += ".json"
        config_folder = Utils.add_base_path(Constants.CONFIG_FOLDER)
        cfg_path = Path.joinpath(config_folder, name)
        Model.get().set_active_cfg_path(cfg_path)
        self.model.set_active_cfg({})
        await self.controller.state_machine()

    async def handle_new_cfg_type_input(self, user_input):
        if user_input == TypesMenu.ADD:
            self.model.current_state_machine = StateMachines.CFG_TYPE
        elif user_input == TypesMenu.CONT:
            self.model.set_done_adding_types()

        await self.controller.state_machine()

    #Secret little bit of View code going on here ;)
    async def let_user_pick_excel_input(self):
        # Open file picker dialog
        file_path = filedialog.askopenfilename(
            title="Kies een bestand",
            filetypes=(("Excel files", "*.xlsx *.xls"), ("All files", "*.*"))
        )
        await self.set_field_in_cfg(CfgFields.INPUT_FILE_NAME, file_path, Validations.TEXT)

    async def set_type_column_field_in_cfg(self, user_input):
        await self.set_field_in_cfg(CfgFields.TYPES_COLUMN, user_input, Validations.EXCEL_COLUMN)

    async def set_type_cell_color_type_in_cfg(self, user_input):
        await self.set_field_in_cfg([CfgFields.TYPES_EXCEL_FILE_COLOR_TYPE, CfgFields.TYPES_EXCEL_FILE_CELL_COLOR], user_input, Validations.COLOR_CELL_TYPE)

    async def set_match_string_in_cfg(self, user_input):
        await self.set_field_in_cfg(CfgFields.TYPES_MATCH_STRING, user_input, Validations.TEXT)

    async def set_type_method_in_cfg(self, user_input):
        await self.set_field_in_cfg(CfgFields.TYPES_METHOD, user_input, Validations.TEXT)

    async def set_type_name_in_cfg(self, user_input):
        await self.set_field_in_cfg(CfgFields.TYPES_NAME, user_input, Validations.TEXT)

    async def set_type_text_color_in_cfg(self, user_input):
        await self.set_field_in_cfg(CfgFields.TYPES_GENERATED_IMAGE_TEXT_COLOR, user_input, Validations.COLOR)

    async def set_margin_in_cfg(self, user_input):
        await self.set_field_in_cfg(CfgFields.MARGIN, user_input, Validations.NUMBER)

    async def set_font_size_in_cfg(self, user_input):
        await self.set_field_in_cfg(CfgFields.FONT_SIZE, user_input, Validations.NUMBER)

    async def set_font_in_cfg(self, user_input):
        await self.set_field_in_cfg(CfgFields.FONT, user_input, Validations.FONT)

    async def set_bg_color_in_cfg(self, user_input):
        await self.set_field_in_cfg(CfgFields.BACKGROUND_COLOR, user_input, Validations.COLOR)

    async def set_width_in_cfg(self, user_input):
        await self.set_field_in_cfg(CfgFields.WIDTH, user_input, Validations.NUMBER)

    async def set_height_in_cfg(self, user_input):
        await self.set_field_in_cfg(CfgFields.HEIGHT, user_input, Validations.NUMBER)

    async def set_column_name_in_cfg(self, user_input):
        await self.set_field_in_cfg(CfgFields.COLUMN_NAME, user_input, Validations.TEXT)

    async def set_header_in_cfg(self, user_input):
        await self.set_field_in_cfg(CfgFields.FILE_HAS_HEADER, user_input, Validations.TEXT)

