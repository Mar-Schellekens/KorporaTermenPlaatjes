import glob
import json
import os
from collections import defaultdict
import copy

import pandas
from openpyxl.utils import get_column_letter

import Constants
from tkinter import Tk, filedialog

import re

from ColorConfig import edit_colors
from Singleton import app
from Utils import let_user_choose_actie, add_base_path


# defaultConfig = defaultdict(lambda: None, {
#     "input_file_name": None,
#     "file_has_header": None,
#     "column_name": None,
#     "width": None,
#     "height": None,
#     "background_color": None,
#     "font": None,
#     "font_size": None,
#     "margin": None
# })

def print_config(config_name):
    return config_name.replace(Constants.CONFIG_FOLDER + "\\", "")





    # while True:
    #     choice = input("Typ het nummer van uw keuze: ").strip()
    #     if choice.isdigit():
    #         index = int(choice) - 1
    #         if 0 <= index < len(cfg_files):
    #             cfg= cfg_files[index]
    #             break
    #     print("Invalide keuze, probeer opnieuw.")

    # return cfg

# Replace by new UI
def create_new_config():
    cfg = {}
    print()
    config_name = input(f"Typ de nieuwe naam van de configuratie: ").strip()
    if not config_name.lower().endswith(".json"):
        config_name += ".json"
    config_name = os.path.join(Constants.CONFIG_FOLDER, config_name)
    save_config(cfg, config_name)
    modify_config(config_name)
    return config_name


def ask_modify_config():
    while True:
        answer = input("Wil je deze configuratie aanpassen? (ja/nee)").strip().lower()
        if answer in ("ja", "nee"):
            break
        print("Invalide antwoord. Type \"ja\" of \"nee\"")

    if answer == "ja":
        return True
    else:
        return False

def load_config(cfg):
    if os.path.exists(cfg):
        with open(cfg, "r") as f:
            return json.load(f)
    else:
        print("Configuratie bestand bestaat niet")

def save_config(config, config_name):
    config_dir = add_base_path(Constants.CONFIG_FOLDER)
    config_name = os.path.join(config_dir, config_name)
    with open(config_name, "w") as f:
        json.dump(config, f, indent=2)
    print(f"Configuratie opgeslagen onder {config_name}")

def prompt_input(prompt, default=None):
    if default is not None:
        value = input(f"{prompt} [huidig: {default}]: ").strip()
        return value if value else default
    else:
        return input(f"{prompt}: ").strip()

def prompt_input_input_file(default=None):
    value = "blub"

    if default is not None:
        while value not in ["wijzig", '']:
            value = input(f"{"De bestandsnaam van het excel bestand om de plaatjes te genereren. Typ \"wijzig\" om te veranderen, of druk op Enter om huidige te behouden"} [huidig: {default}]: ").strip()
    else:
        input("Kies het excel bestand om de plaatjes te genereren. Druk op Enter om de verkenner te openen.")
        value = "wijzig"

    if value == "wijzig":
        # Hide the root window
        Tk().withdraw()

        # Open file picker dialog
        file_path = filedialog.askopenfilename(
            title="Kies een bestand",
            filetypes=(("Excel files", "*.xlsx *.xls"), ("All files", "*.*"))
        )

        print(f"Geselecteerd bestand: {file_path}")
        return file_path
    else:
        return default

def prompt_input_header(default=None):
    value = "blub"
    if default is not None:
        while value not in ["ja", "nee", '']:
            value = input(f"{"Is de eerste rij van het bestand de koptekst/header?. Type \"ja\" of \"nee\" om de waarde te veranderen of druk op Enter om huidige te behouden."} [huidig: {default}]: ").strip()
    else:
        while value not in ["ja", "nee"]:
            value = input(f"{"Is de eerste rij van het bestand de koptekst/header? Type \"ja\" of \"nee\""}: ").strip()

    if not value:
        value = default
    return value


def prompt_input_termen(input_file_name, default=None):
    value = "blub"

    if default is not None:
        while value not in ["wijzig", '']:
            value = input(f"{"Kolom naam van termen. Typ \"wijzig\" om te veranderen, of druk op Enter om huidige te behouden"} [huidig: {default}]: ").strip()
    else:
        value = "wijzig"

    if value == "wijzig":
        df = pandas.read_excel(input_file_name)

        print("Het opgegeven bestand bevat de volgende kolommen:")
        return let_user_choose_actie(df.columns)
        # for i, column_name in enumerate(df.columns, start=1):
        #     print(f"{i}. {column_name}", "")
        #
        # while True:
        #     choice = input("Typ het nummer van de kolom die de termen bevat: ").strip()
        #     if choice.isdigit():
        #         index = int(choice) - 1
        #         if 0 <= index < len(df.columns):
        #             kolom_termen = df.columns[index]
        #             break
        #     print("Invalide keuze. Probeer opnieuw. ")

        return kolom_termen
    else:
        return default

def prompt_input_integer(prompt, default=None):
    while True:
        if default is not None:
            user_input = input(f"{prompt} Druk op Enter om huidige waarde te behouden. [huidig: {default}]: ").strip()
            if not user_input:
                user_input = default
        else:
            user_input = input(prompt).strip()
        try:
            number = int(user_input)  # or int(user_input) if you only want integers
            return number
        except ValueError:
            print("Dat is geen nummer, probeer opnieuw.")

def is_valid_hex_color(s):
    return bool(re.fullmatch(r"#?[0-9A-Fa-f]{6}|#?[0-9A-Fa-f]{3}", s))

def prompt_input_hex_color(prompt, default=None):
    while True:
        if default is not None:
            user_input = input(f"{prompt} Druk op Enter om huidige waarde te behouden. [huidig: {default}]: ").strip()
            if not user_input:
                user_input = default
        else:
            user_input = input(prompt).strip()
        try:
            if not is_valid_hex_color(user_input):
                raise Exception
            return user_input
        except ValueError:
            print("Dat is geen hex kleur formaat, probeer opnieuw.")

def modify_config(config_name):
    config = load_config(config_name)

    config["input_file_name"] = prompt_input_input_file(config.get("input_file_name"))
    config["file_has_header"] = prompt_input_header(config.get("file_has_header"))
    config["column_name"] = prompt_input_termen(config["input_file_name"], config.get("column_name"))

    config["width"] = prompt_input_integer("Type de gewenste breedte van het gegenereerde plaatje in pixels.", config.get("width"))
    config["height"] = prompt_input_integer("Type de gewenste hoogte van het gegenereerde plaatje in pixels.", config.get("height"))
    config["background_color"] = prompt_input_hex_color("Type de gewenste kleur van de achtergrond van het plaatje als hexstring (bijv: \"#673489\").", config.get("background_color"))
    config["font"] = prompt_input("Type de naam van het font dat je wil gebruiken. ", config.get("font"))
    config["font_size"] = prompt_input_integer("Type de gewenst tekstgrootte. ", config.get("font_size"))
    config["margin"] = prompt_input_integer("Type de gewenst marge in pixels. ", config.get("margin"))
    config["types"] = edit_colors(config.get("types"), config["input_file_name"])

    df = pandas.read_excel(config["input_file_name"])
    col_idx = df.columns.get_loc(config["column_name"]) + 1  # openpyxl is 1-based
    config["column_letter"] = get_column_letter(col_idx)

    save_config(config, config_name)
