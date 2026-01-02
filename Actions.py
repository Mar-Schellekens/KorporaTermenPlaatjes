import asyncio
import glob
import json
import os
from random import random
from time import sleep
from tkinter import filedialog

import pandas

import Constants
from Constants import Acties
from CreateInputConfig import modify_config, create_new_config, save_config
from CreatePicture import create_picture, create_picture_test
from LoadTerms import load_terms
from Singleton import app
from openpyxl.utils import get_column_letter


async def listActions():
    actions = [Acties.MAAK_NIEUWE_CONFIG, Acties.LAAD_BESTAANDE_CONFIG]

    if app.get().input_config_file_name is not None:
        actions.extend([Acties.VERANDER_CONFIG, Acties.GENEREER_PLAATJES])

    actions.append(Acties.EXIT)

    app.get().ui.setList("Kies een actie: ", actions, callbackActies)
    app.get().ui.setActiveConfigName(app.get().input_config_file_name)
    await app.get().ui.refreshScreen()

async def callback_let_user_choose_config(config_name):
    app.get().input_config_file_name = config_name
    await listActions()

async def test_create_config_file():
    await app.get().ui.EmptyScreen()
    app.get().ui.setInput("Wat is de nieuwe naam van de configuratie?", test_create_config_file_name_found_cb)

    await app.get().ui.refreshScreen()

async def test_create_config_file_name_found_cb(config_name):
    cfg = {}
    if not config_name.lower().endswith(".json"):
        config_name += ".json"
    config_name = os.path.join(Constants.CONFIG_FOLDER, config_name)
    save_config(cfg, config_name)
    app.get().ui.setActiveConfigName(config_name)
    app.get().ui.setActiveConfig(cfg)
    await prompt_input_input_file_new()
    #input file name

async def config_state_machine():
    state_machine = app.get().ui.getConfigStateMachine()
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
        await prompt_input_background_color("Type de geweneste kleur van de achtergrond van het plaatje als hexstring (bijv: \"#673489\"")
    elif "font" not in state_machine:
        await prompt_input_font()
    elif "font_size" not in state_machine:
        await prompt_input_font_size()
    elif "margin" not in state_machine:
        await prompt_input_margin()
    elif "types" not in state_machine:
        await prompt_input_types()
    else:
        df = pandas.read_excel(app.get().ui.activeConfig["input_file_name"])
        col_idx = df.columns.get_loc(app.get().ui.activeConfig["column_name"]) + 1  # openpyxl is 1-based
        app.get().ui.activeConfig["column_letter"] = get_column_letter(col_idx)

        save_config(app.get().ui.activeConfig, app.get().ui.activeConfigName)
        await listActions()

async def prompt_input_type_name():
    print("blub")


async def prompt_input_types():
    await app.get().ui.EmptyScreen()
    list_options = ["Nieuw type toevoegen", "Doorgaan naar volgende stap"]
    app.get().ui.setList("Een type zorgt ervoor dat bepaalde groepen, bepaalde tekstkleuren krijgen", list_options, prompt_input_types_cb)

    await app.get().ui.refreshScreen()

async def prompt_input_types_cb(user_input):
    if user_input == "Nieuw type toevoegen":
        await prompt_input_type_name()
    elif user_input == "Doorgaan naar volgende stap":
        app.get().ui.setActiveConfigField("types", [])
        await config_state_machine()

async def prompt_input_margin():
    await app.get().ui.EmptyScreen()
    app.get().ui.setNumberInput("Type de gewenste marge in pixels", prompt_input_margin_cb)
    await app.get().ui.refreshScreen()

async def prompt_input_font_size():
    await app.get().ui.EmptyScreen()
    app.get().ui.setNumberInput("Type de gewenste tekstgrootte", prompt_input_font_size_cb)
    await app.get().ui.refreshScreen()

async def prompt_input_font():
    await app.get().ui.EmptyScreen()
    app.get().ui.setInput("Type de naam van het font dat je wil gebruiken.", prompt_input_font_cb)
    await app.get().ui.refreshScreen()

async def prompt_input_background_color(prompt):
    await app.get().ui.EmptyScreen()
    app.get().ui.setInput(prompt, prompt_input_background_color_cb)
    await app.get().ui.refreshScreen()

async def prompt_input_width_new(prompt):
    await app.get().ui.EmptyScreen()
    app.get().ui.setNumberInput(prompt, prompt_input_width_new_cb)
    await app.get().ui.refreshScreen()

async def prompt_input_height_new(prompt):
    await app.get().ui.EmptyScreen()
    app.get().ui.setNumberInput(prompt, prompt_input_height_new_cb)
    await app.get().ui.refreshScreen()

async def prompt_input_margin_cb(user_input):
    app.get().ui.setActiveConfigField("margin", int(user_input))
    await config_state_machine()

async def prompt_input_font_size_cb(user_input):
    app.get().ui.setActiveConfigField("font_size", int(user_input))
    await config_state_machine()

async def prompt_input_font_cb(user_input):
    app.get().ui.setActiveConfigField("font", user_input)
    await config_state_machine()

async def prompt_input_background_color_cb(user_input):
    app.get().ui.setActiveConfigField("background_color", user_input)
    await config_state_machine()

async def prompt_input_width_new_cb(user_input):
    app.get().ui.setActiveConfigField("width", int(user_input))
    await config_state_machine()

async def prompt_input_height_new_cb(user_input):
    app.get().ui.setActiveConfigField("height", int(user_input))
    await config_state_machine()

async def prompt_input_termen_new():
    cfg = app.get().ui.getActiveConfig()
    df = pandas.read_excel(cfg["input_file_name"])

    await app.get().ui.EmptyScreen()
    app.get().ui.setList("Selecteer de kolom die de termen bevat. Het opgegeven bestand bevat de volgende kolommen:", df.columns, prompt_input_termen_new_cb)
    await app.get().ui.refreshScreen()


async def prompt_input_termen_new_cb(user_input):
    app.get().ui.setActiveConfigField("column_name", user_input)
    await config_state_machine()


async def prompt_input_input_file_new(default = None):
    await app.get().ui.EmptyScreen()

    if default is not None:
        app.get().ui.setInput(f"{"De bestandsnaam van het excel bestand om de plaatjes te genereren. Type \"wijzig\" om te veranderen, of druk op Enter om huidige te behouden"} [huidig: {default}]: ", prompt_input_file_new_cb)
    else:
        app.get().ui.setInput("Kies het excel bestand om de plaatjes te genereren. Druk op Enter om de verkenner te openen", prompt_input_file_new_cb)
        value = "wijzig"

    await app.get().ui.refreshScreen()

async def prompt_input_file_new_cb(user_input):
    # Open file picker dialog
    file_path = filedialog.askopenfilename(
        title="Kies een bestand",
        filetypes=(("Excel files", "*.xlsx *.xls"), ("All files", "*.*"))
    )
    app.get().ui.setActiveConfigField("input_file_name", file_path)
    await config_state_machine()

async def prompt_input_header_new():
    await app.get().ui.EmptyScreen()
    app.get().ui.setList("Is de eerste rij van het bestand de koptekst/header?", ["ja", "nee"], prompt_input_header_new_cb)
    await app.get().ui.refreshScreen()

async def prompt_input_header_new_cb(user_input):
    app.get().ui.setActiveConfigField("file_has_header", user_input)
    #app.get().ui.setConfigStateMachine("file_has_header")
    await config_state_machine()


async def let_user_choose_config():
    cfg_files = glob.glob(os.path.join(Constants.CONFIG_FOLDER, "*.json"))

    if len(cfg_files) == 0:
        app.get().ui.setMessage("Er bestaan nog geen configuratie bestanden.")
        await listActions()

    # for i, file_name in enumerate(cfg_files, start=1):
    #     print(f"{i}. {print_config(file_name)}", "")

    app.get().ui.setList("Kies een input configuratie bestand:", cfg_files, callback_let_user_choose_config)
    await app.get().ui.refreshScreen()


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
            await app.get().ui.action_quit()
        case Acties.LAAD_BESTAANDE_CONFIG:
            await let_user_choose_config()
        case Acties.VERANDER_CONFIG:
            modify_config(callbackActies.input_config_file_name)
        case Acties.MAAK_NIEUWE_CONFIG:
            await test_create_config_file()
            #input_config_file_name = create_new_config()
        case Acties.GENEREER_PLAATJES:
            with open(app.get().input_config_file_name) as f:
                cfg = json.load(f)
            termen = load_terms(cfg)
            #for term in termen:
                #await create_picture(term, cfg, app.get())
                #asyncio.create_task(create_picture(term, cfg, app.get()))

            await app.get().ui.EmptyScreen()
            app.get().ui.setShowProgressBar(True)
            await app.get().ui.refreshScreen()
            percent = 1/len(termen) * 100
            asyncio.create_task(slowTask(app.get().ui, termen, cfg, percent))
            #for term in termen:
                #sleep(2)
                #await app.get().ui.increment()
                #app.get().ui.run_worker(create_picture(term, cfg, app.get().ui), process=True)
                #asyncio.create_task(create_picture(term, cfg, app.get().ui))
                #asyncio.create_task(slowTask(app.get().ui))

