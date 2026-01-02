import pandas
from colorist import hex
from openpyxl.utils import get_column_letter

from Constants import Config
from RulesConfig import prompt_input_cell_color
from Utils import let_user_choose_actie
import numpy as np


def prompt_input(prompt_text, default=None, cast=str, validator=None):
    """
    Prompt the user for input with optional default, type casting, and validation.
    """
    if default is not None:
        prompt_text = f"{prompt_text} [{default}]: "
    else:
        prompt_text = f"{prompt_text}: "

    while True:
        user_input = input(prompt_text).strip()
        if not user_input and default is not None:
            return default
        elif not user_input:
            return None  # allow empty input
        try:
            value = cast(user_input)
            if validator and not validator(value):
                print("Invalid value. Please try again.")
                continue
            return value
        except ValueError:
            print(f"Invalid input type. Expected {cast.__name__}.")

def prompt_input_column(prompt_text, default=None, input_file_name=None):
    value = "blub"

    if default is not None:
        while value not in ["wijzig", '']:
            value = input(
                f"{"Kolom op basis waarvan de tekstkleur bepaald word. Typ \"wijzig\" om te veranderen, of druk op Enter om huidige te behouden"} [huidig: {default}]: ").strip()
    else:
        value = "wijzig"

    if value == "wijzig":
        df = pandas.read_excel(input_file_name)

        print("Het opgegeven bestand bevat de volgende kolommen:")
        column = let_user_choose_actie(df.columns)
        columnIndex = int(np.where(df.columns.values == column)[0][0])
        return columnIndex
        #return column




def is_valid_hex_color(s):
    """Validate hex color like #FFF or #FF8040"""
    s = s.lstrip("#")
    return len(s) in (3, 6) and all(c in "0123456789abcdefABCDEF" for c in s)

def add_or_modify_type(type, excel_file_name):
    name = prompt_input("Type nieuwe naam of druk op \"Enter\" om huidige te behouden ", default=type.get(Config.TYPES_NAME))
    text_color = prompt_input(
        "Type nieuwe kleur als hex (bijv. #FF8040) voor tekstkleur in gegenereerd plaatje, of druk op \"Enter\" om huidige te behouden.",
        default=type.get(Config.TYPES_GENERATED_IMAGE_TEXT_COLOR), validator=is_valid_hex_color)
    method = prompt_input(
        "Wil je bepalen via \"celkleur\" of \"celinhoud\"? (celinhoud wordt nog niet ondersteund)",
        default=type.get(Config.TYPES_METHOD))
    column = prompt_input_column("Welke kolom?", type.get(Config.TYPES_COLUMN), excel_file_name)
    color_type, cell_color = prompt_input_cell_color(excel_file_name, column)

    return {Config.TYPES_NAME: name,
                        Config.TYPES_GENERATED_IMAGE_TEXT_COLOR: text_color,
                        Config.TYPES_METHOD: method,
                        Config.TYPES_COLUMN: column,
                        Config.TYPES_EXCEL_FILE_CELL_COLOR: cell_color,
                        Config.TYPES_EXCEL_FILE_COLOR_TYPE: color_type}


def edit_colors(types, excel_file_name):
    final_types = []

    # Edit existing defaults
    if types is not None:
        for type in types:
            print(f"\nType '{type[Config.TYPES_NAME]}' zal in de gegenereerde plaatjes de volgende tekst kleur hebben:", end="")
            hex(f"'{type[Config.TYPES_GENERATED_IMAGE_TEXT_COLOR]}'", type[Config.TYPES_GENERATED_IMAGE_TEXT_COLOR])
            print(f"\nOf iets type '{type[Config.TYPES_NAME]}' is wordt bepaald door de volgende methode: ")
            print(f"bepaald door: {type[Config.TYPES_METHOD]}")
            print(f"In kolom: {type[Config.TYPES_COLUMN]}")
            print(f"gelijk aan kleur: {type[Config.TYPES_EXCEL_FILE_COLOR_TYPE]} {type[Config.TYPES_EXCEL_FILE_CELL_COLOR]}")

            action = input("Type \"wijzig\" om te wijzigen, druk op \"Enter\" om te behouden, of type \"verwijder\" om het te verwijderen. ").strip().lower()
            if action == "verwijder":
                print(f"Heb '{type[Config.TYPES_NAME]}' Verwijderd")
                continue
            if action == "wijzig":
                final_types.append(add_or_modify_type(type, excel_file_name))
            if action == "":
                final_types.append(type)

    # Add new types
    while True:
        print("\nEen type zorgt ervoor dat bepaalde groepen, bepaalde tekstkleuren krijgen")
        answer = prompt_input("Type \"nieuw\" om een nieuw type toe te voegen, of druk op \"Enter\" om geen nieuwe types meer toe te voegen.")
        if answer == "nieuw":
            final_types.append(add_or_modify_type({}, excel_file_name))
        if answer is None:
            break

    return final_types
