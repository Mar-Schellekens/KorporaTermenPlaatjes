#This is an interface between control and view, part of the view layer, and should never import ControlInputHandler to prevent circular import.

import asyncio
import glob
import os
import pandas
from openpyxl.reader.excel import load_workbook
import Constants
from CreatePicture import create_picture, create_picture_async
from Model import Model
from RulesConfig import get_all_colors_in_column
from View import View
from Utils import add_base_path, convert_excel_colors_to_string

class ViewInputPrompter:
    async def test_create_config_file(self, cb):
        await View.get().EmptyScreen()
        View.get().setInput("Wat is de nieuwe naam van de configuratie?", cb)
        await View.get().refreshScreen()

    async def prompt_input_type_column(self, cb):
        await View.get().EmptyScreen()
        config = Model.get().getActiveConfig()
        df = pandas.read_excel(config["input_file_name"])
        View.get().setList("Welke kolom bevat de kleur?", df.columns, cb)
        await View.get().refreshScreen()

    async def prompt_input_type_cell_color(self, cb):
        await View.get().EmptyScreen()
        config = Model.get().getActiveConfig()
        configType = Model.get().getNewConfigType()
        wb = load_workbook(config["input_file_name"])
        ws = wb.active

        column = configType["column"]  # column to scan
        all_colors = get_all_colors_in_column(ws, column, wb, config["input_file_name"])
        all_colors_string = convert_excel_colors_to_string(all_colors)
        View.get().setList("Welke kleur hoort bij dit type?", all_colors_string, cb)
        await View.get().refreshScreen()

    async def prompt_input_type_method(self, cb):
        await View.get().EmptyScreen()
        View.get().setList("Wil je bepalen via celkleur of celinhoud, of iets bij dit type hoort?", ["celkleur", "celinhoud"], cb)
        await View.get().refreshScreen()

    async def prompt_input_type_text_color(self, cb):
        await View.get().EmptyScreen()
        View.get().setInput("Wat moet de tekstkleur zijn van dit type? Type de gewenste kleur als hexstring (bijv: \"#673489\")", cb)
        await View.get().refreshScreen()

    async def prompt_input_type_name(self, cb):
        await View.get().EmptyScreen()
        View.get().setInput("Wat is de naam van dit type?", cb)
        await View.get().refreshScreen()

    async def prompt_input_types(self, cb):
        await View.get().EmptyScreen()
        list_options = ["Nieuw type toevoegen", "Doorgaan naar volgende stap"]
        View.get().setList("Een type zorgt ervoor dat bepaalde groepen, bepaalde tekstkleuren krijgen", list_options, cb)
        await View.get().refreshScreen()

    async def prompt_input_margin(self, cb):
        await View.get().EmptyScreen()
        View.get().setNumberInput("Type de gewenste marge in pixels", cb)
        await View.get().refreshScreen()

    async def prompt_input_font_size(self, cb):
        await View.get().EmptyScreen()
        View.get().setNumberInput("Type de gewenste tekstgrootte", cb)
        await View.get().refreshScreen()

    async def prompt_input_font(self, cb):
        await View.get().EmptyScreen()
        View.get().setInput("Type de naam van het font dat je wil gebruiken.", cb)
        await View.get().refreshScreen()

    async def prompt_input_background_color(self, cb):
        await View.get().EmptyScreen()
        View.get().setInput("Type de gewenste kleur van de achtergrond van het plaatje als hexstring (bijv: \"#673489\"", cb)
        await View.get().refreshScreen()

    async def prompt_input_width_new(self, cb):
        await View.get().EmptyScreen()
        View.get().setNumberInput("Type de gewenste breedte van het gegenereerde plaatje in pixels", cb)
        await View.get().refreshScreen()

    async def prompt_input_height_new(self, cb):
        await View.get().EmptyScreen()
        View.get().setNumberInput("Type de gewenste hoogte van het gegenereerde plaatje in pixels", cb)
        await View.get().refreshScreen()

    async def prompt_input_termen_new(self, cb):
        cfg = Model.get().getActiveConfig()
        df = pandas.read_excel(cfg["input_file_name"])

        await View.get().EmptyScreen()
        View.get().setList("Selecteer de kolom die de termen bevat. Het opgegeven bestand bevat de volgende kolommen:", df.columns, cb)
        await View.get().refreshScreen()

    async def prompt_input_input_file_new(self, cb):
        await View.get().EmptyScreen()
        View.get().setButtonInput("Kies het excel bestand om de plaatjes te genereren.", "Klik hier om de verkenner te openen", cb)
        await View.get().refreshScreen()

    async def prompt_input_header_new(self, cb):
        await View.get().EmptyScreen()
        View.get().setList("Is de eerste rij van het bestand de koptekst/header?", ["ja", "nee"], cb)
        await View.get().refreshScreen()

    async def let_user_choose_config(self, cb, cb_no_configs):
        config_folder = add_base_path(Constants.CONFIG_FOLDER)
        cfg_files = glob.glob(os.path.join(config_folder, "*.json"))

        if len(cfg_files) == 0:
            View.get().setMessage("Er bestaan nog geen configuratie bestanden.")
            await cb_no_configs()

        View.get().setList("Kies een input configuratie bestand:", cfg_files, cb)
        await View.get().refreshScreen()

    async def slowTaskPrompt(self, termen, file_name, percent, cb):
        for counter, term in enumerate(termen):
            await create_picture_async(term, file_name)
            await View.get().increment_test(counter/len(termen)*100)
        await View.get().increment_test(0, finished=True)




