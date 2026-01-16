import pandas
from openpyxl import load_workbook
from Constants import CfgFields, TypesMethod
from Term import Term

def classify_by_color(typ, cell, column_index):
    if typ[CfgFields.TYPES_EXCEL_FILE_COLOR_TYPE] == "theme":
        if str(cell[column_index].fill.start_color.theme) == typ[CfgFields.TYPES_EXCEL_FILE_CELL_COLOR]:
            return True
    elif typ[CfgFields.TYPES_EXCEL_FILE_COLOR_TYPE] == "rgb":
        if typ[CfgFields.TYPES_EXCEL_FILE_CELL_COLOR] == "geen kleur":
            if cell[column_index].fill.patternType is None:
                return True
        elif cell[column_index].fill.start_color.rgb == typ[CfgFields.TYPES_EXCEL_FILE_CELL_COLOR]:
            return True
    return False

def classify_by_value(typ, cell, column_index):
    if cell[column_index].value == typ[CfgFields.TYPES_MATCH_STRING]:
        return True
    return False

def classify_cell(cell, types):
    for typ in types:
        column_index = typ[CfgFields.TYPES_COLUMN]
        if typ[CfgFields.TYPES_METHOD] == "celkleur":
            if classify_by_color(typ, cell, column_index):
                return typ[CfgFields.TYPES_GENERATED_IMAGE_TEXT_COLOR]
        elif typ[CfgFields.TYPES_METHOD] == TypesMethod.CEL_INHOUD:
            if classify_by_value(typ, cell, column_index):
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