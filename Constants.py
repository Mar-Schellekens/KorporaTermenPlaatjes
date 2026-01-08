from enum import StrEnum, Enum

class Validations(Enum):
    TEXT = 0
    NUMBER = 1
    COLOR = 2
    EXCEL_COLUMN = 3
    COLOR_CELL_TYPE = 4
    DICT = 5

class StateMachines(Enum):
    MAIN_MENU = 0
    CONFIG = 1,
    CFG_TYPE = 2

class TypesMenu(StrEnum):
    ADD = "Nieuw type toevoegen"
    CONT = "Doorgaan naar volgende stap"

class CfgFields(StrEnum):
    INPUT_FILE_NAME = "input_file_name"
    FILE_HAS_HEADER = "file_has_header"
    COLUMN_NAME = "column_name"
    TYPES = "types"
    TYPES_NAME = "name"
    TYPES_GENERATED_IMAGE_TEXT_COLOR = "generated_image_text_color"
    TYPES_METHOD = "method"
    TYPES_COLUMN = "column"
    TYPES_EXCEL_FILE_COLOR_TYPE = "excel_file_color_type"
    TYPES_EXCEL_FILE_CELL_COLOR = "excel_file_cell_color"
    WIDTH = "width"
    HEIGHT = "height"
    BACKGROUND_COLOR = "background_color"
    FONT = "font"
    FONT_SIZE = "font_size"
    MARGIN = "margin"

TYPE_FIELDS = [CfgFields.TYPES_NAME,
               CfgFields.TYPES_GENERATED_IMAGE_TEXT_COLOR,
               CfgFields.TYPES_METHOD,
               CfgFields.TYPES_COLUMN,
               CfgFields.TYPES_EXCEL_FILE_COLOR_TYPE,
               CfgFields.TYPES_EXCEL_FILE_CELL_COLOR]

class Acties(StrEnum):
    MAAK_NIEUWE_CONFIG = "Maak een compleet nieuwe configuratie."
    LAAD_BESTAANDE_CONFIG = "Laad bestaande configuratie in als actieve configuratie."
    GENEREER_PLAATJES = "Genereer plaatjes van de termen, op basis van actieve configuratie."
    EXIT = "Sluit programma af."


CONFIG_FOLDER = "configuraties"

