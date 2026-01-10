import json
import os
import re
import sys
from pathlib import Path
from openpyxl.reader.excel import load_workbook
import Constants

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
    config_name = os.path.join(config_dir, config_name + ".json")
    with open(config_name, "w") as f:
        json.dump(config, f, indent=2)
    print(f"Configuratie opgeslagen onder {config_name}")

def is_valid_hex_color(s: str) -> bool:
    return bool(re.fullmatch(r"#([0-9a-fA-F]{6}|[0-9a-fA-F]{3})", s))

def get_file_name_from_path(path: Path):
    return os.path.splitext(os.path.basename(path))[0]