import json

import pandas
from openpyxl import load_workbook
from openpyxl.utils import column_index_from_string

from Constants import Config
from Term import Term

def classify_cell(cell, types):
    for type in types:
        column_index = type[Config.TYPES_COLUMN]
        if type[Config.TYPES_METHOD] == "celkleur":
            if type[Config.TYPES_EXCEL_FILE_COLOR_TYPE] == "theme":
                if str(cell[column_index].fill.start_color.theme) == type[Config.TYPES_EXCEL_FILE_CELL_COLOR]:
                    return type[Config.TYPES_GENERATED_IMAGE_TEXT_COLOR]
            elif type[Config.TYPES_EXCEL_FILE_COLOR_TYPE] == "rgb":
                if cell[column_index].fill.start_color.rgb == type[Config.TYPES_EXCEL_FILE_CELL_COLOR]:
                    return type[Config.TYPES_GENERATED_IMAGE_TEXT_COLOR]
        # elif type["method"] == "string":
        #     if type["contains"].lower() in str(cell.value).lower():
        #         return type["type"]
    return "#000000"

def load_terms(cfg):
    df = pandas.read_excel(cfg[Config.INPUT_FILE_NAME])
    termen = df[cfg[Config.COLUMN_NAME]].values

    # Load the workbook with openpyxl
    wb = load_workbook(cfg[Config.INPUT_FILE_NAME])
    ws = wb.active

    colors = [classify_cell(row, cfg[Config.TYPES]) for row in ws.iter_rows()]

    if cfg[Config.FILE_HAS_HEADER]:
        colors = colors[1:] #Remove header row

    # Assign values from lists
    # color_map = {item[Config.TYPES_NAME]: item[Config.TYPES_GENERATED_IMAGE_TEXT_COLOR] for item in cfg[Config.TYPES]}
    termObjects = []
    for term, color in zip(termen, colors):
        termObjects.append(Term(term, color))

    return termObjects