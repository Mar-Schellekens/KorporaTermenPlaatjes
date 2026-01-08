#This is an interface between control and view, part of the control layer, and should never import ViewInputPrompter to prevent circular import.
from tkinter import filedialog

import numpy as np
import pandas
from openpyxl.reader.excel import load_workbook
from CreateInputConfig import save_config
from Model import Model
from RulesConfig import get_all_colors_in_column
from Utils import convert_excel_colors_to_string

class ControlInputHandler:
    def __init__(self, controller):
        self.controller = controller

    async def callback_let_user_choose_config(self, config_name):
        Model.get().input_config_file_name = config_name
        await self.controller.listActions()

    async def test_create_config_file_name_found_cb(self, config_name):
        cfg = {}
        if not config_name.lower().endswith(".json"):
            config_name += ".json"
        save_config(cfg, config_name)
        Model.get().setActiveConfigName(config_name)
        Model.get().setActiveConfig(cfg)
        await self.controller.config_state_machine()

    async def prompt_input_type_column_cb(self, user_input):
        config = Model.get().getActiveConfig()
        df = pandas.read_excel(config["input_file_name"])
        columnIndex = int(np.where(df.columns.values == user_input)[0][0])
        Model.get().setConfigTypeField("column", columnIndex)
        await self.controller.config_type_state_machine()

    async def prompt_input_type_cell_color_cb(self, user_input):
        config = Model.get().getActiveConfig()
        configType = Model.get().getNewConfigType()
        wb = load_workbook(config["input_file_name"])
        ws = wb.active

        column = configType["column"]  # column to scan
        all_colors = get_all_colors_in_column(ws, column, wb, config["input_file_name"])
        all_colors_string = convert_excel_colors_to_string(all_colors)
        idx = all_colors_string.index(user_input)

        Model.get().setConfigTypeField("excel_file_cell_color", all_colors[idx][1])
        Model.get().setConfigTypeField("excel_file_color_type", all_colors[idx][0])
        await self.controller.config_type_state_machine()

    async def prompt_input_type_method_cb(self, user_input):
        Model.get().setConfigTypeField("method", user_input)
        await self.controller.config_type_state_machine()

    async def prompt_input_type_name_cb(self, user_input):
        Model.get().setConfigTypeField("name", user_input)
        await self.controller.config_type_state_machine()

    async def prompt_input_type_text_color_cb(self, user_input):
        Model.get().setConfigTypeField("generated_image_text_color", user_input)
        await self.controller.config_type_state_machine()

    async def prompt_input_types_cb(self, user_input):
        if user_input == "Nieuw type toevoegen":
            await self.controller.config_type_state_machine()
        elif user_input == "Doorgaan naar volgende stap":
            Model.get().setActiveConfigField("types")
            await self.controller.config_state_machine()

    async def prompt_input_margin_cb(self, user_input):
        Model.get().setActiveConfigField("margin", int(user_input))
        await self.controller.config_state_machine()

    async def prompt_input_font_size_cb(self, user_input):
        Model.get().setActiveConfigField("font_size", int(user_input))
        await self.controller.config_state_machine()

    async def prompt_input_font_cb(self, user_input):
        Model.get().setActiveConfigField("font", user_input)
        await self.controller.config_state_machine()

    async def prompt_input_background_color_cb(self, user_input):
        Model.get().setActiveConfigField("background_color", user_input)
        await self.controller.config_state_machine()

    async def prompt_input_width_new_cb(self, user_input):
        Model.get().setActiveConfigField("width", int(user_input))
        await self.controller.config_state_machine()

    async def prompt_input_height_new_cb(self, user_input):
        Model.get().setActiveConfigField("height", int(user_input))
        await self.controller.config_state_machine()

    async def prompt_input_termen_new_cb(self, user_input):
        Model.get().setActiveConfigField("column_name", user_input)
        await self.controller.config_state_machine()

    async def prompt_input_file_new_cb(self):
        # Open file picker dialog
        file_path = filedialog.askopenfilename(
            title="Kies een bestand",
            filetypes=(("Excel files", "*.xlsx *.xls"), ("All files", "*.*"))
        )
        Model.get().setActiveConfigField("input_file_name", file_path)
        await self.controller.config_state_machine()

    async def prompt_input_header_new_cb(self, user_input):
        Model.get().setActiveConfigField("file_has_header", user_input)
        await self.controller.config_state_machine()

