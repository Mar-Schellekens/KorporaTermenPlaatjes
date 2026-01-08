import json
import os
import sys
from pathlib import Path

from openpyxl.reader.excel import load_workbook

import Constants


def let_user_choose_actie(acties):
    for i, actie in enumerate(acties, start=1):
        print(f"{i}. {str(actie)}", "")

    while True:
        choice = input("\nType het nummer van uw keuze: ").strip()
        if choice.isdigit():
            index = int(choice) - 1
            if 0 <= index < len(acties):
                actie = acties[index]
                break
        print("Invalide keuze. Probeer opnieuw.")

    return actie

def add_base_path(relative_path: str) -> Path:
    if getattr(sys, 'frozen', False):
        base_path = Path(sys._MEIPASS) #ignore warning
    else:
        base_path = Path(__file__).parent
    return base_path / relative_path

def convert_excel_colors_to_string(list_of_color_tuples):
    return [f"{value}. {ctype}" for value, ctype in list_of_color_tuples]

def load_excel_file(file_name):
    workbook = load_workbook(file_name)
    worksheet = workbook.active
    return workbook, worksheet

def save_config(config, config_name):
    config_dir = add_base_path(Constants.CONFIG_FOLDER)
    config_name = os.path.join(config_dir, config_name)
    with open(config_name, "w") as f:
        json.dump(config, f, indent=2)
    print(f"Configuratie opgeslagen onder {config_name}")