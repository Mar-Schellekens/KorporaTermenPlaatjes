import pandas
from openpyxl import load_workbook
from Constants import CfgFields
from Term import Term

def classify_cell(cell, types):
    for typ in types:
        column_index = typ[CfgFields.TYPES_COLUMN]
        if typ[CfgFields.TYPES_METHOD] == "celkleur":
            if typ[CfgFields.TYPES_EXCEL_FILE_COLOR_TYPE] == "theme":
                if str(cell[column_index].fill.start_color.theme) == typ[CfgFields.TYPES_EXCEL_FILE_CELL_COLOR]:
                    return typ[CfgFields.TYPES_GENERATED_IMAGE_TEXT_COLOR]
            elif typ[CfgFields.TYPES_EXCEL_FILE_COLOR_TYPE] == "rgb":
                if cell[column_index].fill.start_color.rgb == typ[CfgFields.TYPES_EXCEL_FILE_CELL_COLOR]:
                    return typ[CfgFields.TYPES_GENERATED_IMAGE_TEXT_COLOR]
    return "#000000"

def load_terms(cfg):
    df = pandas.read_excel(cfg[CfgFields.INPUT_FILE_NAME])
    termen = df[cfg[CfgFields.COLUMN_NAME]].values
    wb = load_workbook(cfg[CfgFields.INPUT_FILE_NAME])
    ws = wb.active
    colors = [classify_cell(row, cfg[CfgFields.TYPES]) for row in ws.iter_rows()]

    if cfg[CfgFields.FILE_HAS_HEADER]:
        colors = colors[1:] #Remove header row

    termObjects = []
    for term, color in zip(termen, colors):
        termObjects.append(Term(term, color))

    return termObjects