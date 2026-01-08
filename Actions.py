import asyncio
import glob
import json
import os
from tkinter import filedialog

import numpy as np
import pandas
from openpyxl.reader.excel import load_workbook

import Constants
from Constants import Acties
from CreateInputConfig import save_config
from CreatePicture import create_picture
from LoadTerms import load_terms
from Model import Model
from RulesConfig import get_all_colors_in_column
from View import View
from openpyxl.utils import get_column_letter
from Utils import add_base_path


async def listActions():
    actions = [Acties.MAAK_NIEUWE_CONFIG]

    if Model.get().input_config_file_name is not None:
        actions.append(Acties.VERANDER_CONFIG)

    actions.append(Acties.LAAD_BESTAANDE_CONFIG)

    if Model.get().input_config_file_name is not None:
        actions.append(Acties.GENEREER_PLAATJES)

    actions.append(Acties.EXIT)

    View.get().setList("Kies een actie: ", actions, callbackActies)
    Model.get().setActiveConfigName(Model.get().input_config_file_name)
    await View.get().refreshScreen()

async def callback_let_user_choose_config(config_name):
    Model.get().input_config_file_name = config_name
    await listActions()

async def test_create_config_file():
    await View.get().EmptyScreen()
    View.get().setInput("Wat is de nieuwe naam van de configuratie?", test_create_config_file_name_found_cb)

    await View.get().refreshScreen()

async def test_create_config_file_name_found_cb(config_name):
    cfg = {}
    if not config_name.lower().endswith(".json"):
        config_name += ".json"
    save_config(cfg, config_name)
    Model.get().setActiveConfigName(config_name)
    Model.get().setActiveConfig(cfg)
    await prompt_input_input_file_new()

async def config_state_machine():
    state_machine = Model.get().getConfigStateMachine()
    if "input_file_name" not in state_machine:
        await prompt_input_input_file_new()
    elif "file_has_header" not in state_machine:
        await prompt_input_header_new()
    elif "column_name" not in state_machine:
        await prompt_input_termen_new()
    elif "width" not in state_machine:
        await prompt_input_width_new("Type de gewenste breedte van het gegenereerde plaatje in pixels")
    elif "height" not in state_machine:
        await prompt_input_height_new("Type de gewenste hoogte van het gegenereerde plaatje in pixels")
    elif "background_color" not in state_machine:
        await prompt_input_background_color("Type de gewenste kleur van de achtergrond van het plaatje als hexstring (bijv: \"#673489\"")
    elif "font" not in state_machine:
        await prompt_input_font()
    elif "font_size" not in state_machine:
        await prompt_input_font_size()
    elif "margin" not in state_machine:
        await prompt_input_margin()
    elif "types" not in state_machine:
        await prompt_input_types()
    else:
        df = pandas.read_excel(Model.get().activeConfig["input_file_name"])
        col_idx = df.columns.get_loc(Model.get().activeConfig["column_name"]) + 1  # openpyxl is 1-based
        Model.get().activeConfig["column_letter"] = get_column_letter(col_idx)

        save_config(Model.get().activeConfig, Model.get().activeConfigName)
        await listActions()


async def config_type_state_machine():
    state_machine = Model.get().getTypeStateMachine()
    if "name" not in state_machine:
        await prompt_input_type_name()
    elif "generated_image_text_color" not in state_machine:
        await prompt_input_type_text_color()
    elif "method" not in state_machine:
        await prompt_input_type_method()
    elif "column" not in state_machine:
        await prompt_input_type_column()
    elif "excel_file_cell_color" not in state_machine:
        await prompt_input_type_cell_color()
    else:
        Model.get().setConfigType()
        await config_state_machine()

async def prompt_input_type_column():
    await View.get().EmptyScreen()
    config = Model.get().getActiveConfig()
    df = pandas.read_excel(config["input_file_name"])
    View.get().setList("Welke kolom bevat de kleur?", df.columns, prompt_input_type_column_cb)
    await View.get().refreshScreen()

async def prompt_input_type_cell_color():
    await View.get().EmptyScreen()
    config = Model.get().getActiveConfig()
    configType = Model.get().getNewConfigType()
    wb = load_workbook(config["input_file_name"])
    ws = wb.active

    column = configType["column"]  # column to scan
    all_colors = get_all_colors_in_column(ws, column, wb, config["input_file_name"])
    all_colors_string = convert_excel_colors_to_string(all_colors)
    View.get().setList("Welke kleur hoort bij dit type?", all_colors_string, prompt_input_type_cell_color_cb)
    await View.get().refreshScreen()

def convert_excel_colors_to_string(list_of_color_tuples):
    return [f"{value}. {ctype}" for value, ctype in list_of_color_tuples]

async def prompt_input_type_method():
    await View.get().EmptyScreen()
    View.get().setList("Wil je bepalen via celkleur of celinhoud, of iets bij dit type hoort?", ["celkleur", "celinhoud"], prompt_input_type_method_cb)
    await View.get().refreshScreen()

async def prompt_input_type_text_color():
    await View.get().EmptyScreen()
    View.get().setInput("Wat moet de tekstkleur zijn van dit type? Type de gewenste kleur als hexstring (bijv: \"#673489\")", prompt_input_type_text_color_cb)
    await View.get().refreshScreen()

async def prompt_input_type_name():
    await View.get().EmptyScreen()
    View.get().setInput("Wat is de naam van dit type?", prompt_input_type_name_cb)
    await View.get().refreshScreen()

async def prompt_input_type_column_cb(user_input):
    config = Model.get().getActiveConfig()
    df = pandas.read_excel(config["input_file_name"])
    columnIndex = int(np.where(df.columns.values == user_input)[0][0])
    Model.get().setConfigTypeField("column", columnIndex)
    await config_type_state_machine()

async def prompt_input_type_cell_color_cb(user_input):
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
    await config_type_state_machine()

async def prompt_input_type_method_cb(user_input):
    Model.get().setConfigTypeField("method", user_input)
    await config_type_state_machine()

async def prompt_input_type_name_cb(user_input):
    Model.get().setConfigTypeField("name", user_input)
    await config_type_state_machine()

async def prompt_input_type_text_color_cb(user_input):
    Model.get().setConfigTypeField("generated_image_text_color", user_input)
    await config_type_state_machine()


async def prompt_input_types():
    await View.get().EmptyScreen()
    list_options = ["Nieuw type toevoegen", "Doorgaan naar volgende stap"]
    View.get().setList("Een type zorgt ervoor dat bepaalde groepen, bepaalde tekstkleuren krijgen", list_options, prompt_input_types_cb)
    await View.get().refreshScreen()

async def prompt_input_types_cb(user_input):
    if user_input == "Nieuw type toevoegen":
        await prompt_input_type_name()
    elif user_input == "Doorgaan naar volgende stap":
        Model.get().setActiveConfigField("types")
        await config_state_machine()

async def prompt_input_margin():
    await View.get().EmptyScreen()
    View.get().setNumberInput("Type de gewenste marge in pixels", prompt_input_margin_cb)
    await View.get().refreshScreen()

async def prompt_input_font_size():
    await View.get().EmptyScreen()
    View.get().setNumberInput("Type de gewenste tekstgrootte", prompt_input_font_size_cb)
    await View.get().refreshScreen()

async def prompt_input_font():
    await View.get().EmptyScreen()
    View.get().setInput("Type de naam van het font dat je wil gebruiken.", prompt_input_font_cb)
    await View.get().refreshScreen()

async def prompt_input_background_color(prompt):
    await View.get().EmptyScreen()
    View.get().setInput(prompt, prompt_input_background_color_cb)
    await View.get().refreshScreen()

async def prompt_input_width_new(prompt):
    await View.get().EmptyScreen()
    View.get().setNumberInput(prompt, prompt_input_width_new_cb)
    await View.get().refreshScreen()

async def prompt_input_height_new(prompt):
    await View.get().EmptyScreen()
    View.get().setNumberInput(prompt, prompt_input_height_new_cb)
    await View.get().refreshScreen()

async def prompt_input_margin_cb(user_input):
    Model.get().setActiveConfigField("margin", int(user_input))
    await config_state_machine()

async def prompt_input_font_size_cb(user_input):
    Model.get().setActiveConfigField("font_size", int(user_input))
    await config_state_machine()

async def prompt_input_font_cb(user_input):
    Model.get().setActiveConfigField("font", user_input)
    await config_state_machine()

async def prompt_input_background_color_cb(user_input):
    Model.get().setActiveConfigField("background_color", user_input)
    await config_state_machine()

async def prompt_input_width_new_cb(user_input):
    Model.get().setActiveConfigField("width", int(user_input))
    await config_state_machine()

async def prompt_input_height_new_cb(user_input):
    Model.get().setActiveConfigField("height", int(user_input))
    await config_state_machine()

async def prompt_input_termen_new():
    cfg = Model.get().getActiveConfig()
    df = pandas.read_excel(cfg["input_file_name"])

    await View.get().EmptyScreen()
    View.get().setList("Selecteer de kolom die de termen bevat. Het opgegeven bestand bevat de volgende kolommen:", df.columns, prompt_input_termen_new_cb)
    await View.get().refreshScreen()


async def prompt_input_termen_new_cb(user_input):
    Model.get().setActiveConfigField("column_name", user_input)
    await config_state_machine()


async def prompt_input_input_file_new(default = None):
    await View.get().EmptyScreen()
    View.get().setButtonInput("Kies het excel bestand om de plaatjes te genereren.", "Klik hier om de verkenner te openen", prompt_input_file_new_cb)
    await View.get().refreshScreen()

async def prompt_input_file_new_cb():
    # Open file picker dialog
    file_path = filedialog.askopenfilename(
        title="Kies een bestand",
        filetypes=(("Excel files", "*.xlsx *.xls"), ("All files", "*.*"))
    )
    Model.get().setActiveConfigField("input_file_name", file_path)
    await config_state_machine()

async def prompt_input_header_new():
    await View.get().EmptyScreen()
    View.get().setList("Is de eerste rij van het bestand de koptekst/header?", ["ja", "nee"], prompt_input_header_new_cb)
    await View.get().refreshScreen()

async def prompt_input_header_new_cb(user_input):
    Model.get().setActiveConfigField("file_has_header", user_input)
    await config_state_machine()


async def let_user_choose_config():
    config_folder = add_base_path(Constants.CONFIG_FOLDER)
    cfg_files = glob.glob(os.path.join(config_folder, "*.json"))

    if len(cfg_files) == 0:
        View.get().setMessage("Er bestaan nog geen configuratie bestanden.")
        await listActions()

    View.get().setList("Kies een input configuratie bestand:", cfg_files, callback_let_user_choose_config)
    await View.get().refreshScreen()


async def slowTask(app, termen, file_name, percent):
    slowTask.total = len(termen)
    create_picture(termen[0], file_name, app)
    await app.increment(percent)
    await asyncio.sleep(0.01) #give time to UI thread to update.
    if len(termen) > 1:
        app.run_worker(slowTask(app, termen[1:], file_name, percent))
    else:
        app.setShowProgressBar(False)
        await listActions()

async def callbackActies(actie):
    match actie:
        case Acties.EXIT:
            await View.get().action_quit()
        case Acties.LAAD_BESTAANDE_CONFIG:
            await let_user_choose_config()
        case Acties.VERANDER_CONFIG:
            print("): no workie")
        case Acties.MAAK_NIEUWE_CONFIG:
            await test_create_config_file()
        case Acties.GENEREER_PLAATJES:
            with open(Model.get().input_config_file_name) as f:
                cfg = json.load(f)
            termen = load_terms(cfg)
            await View.get().EmptyScreen()
            View.get().setShowProgressBar(True)
            await View.get().refreshScreen()
            percent = 1/len(termen) * 100
            asyncio.create_task(slowTask(View.get(), termen, cfg, percent))


