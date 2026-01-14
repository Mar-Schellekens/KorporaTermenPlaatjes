from enum import StrEnum, Enum, auto


class Validations(Enum):
    TEXT = auto()
    NUMBER = auto()
    COLOR = auto()
    EXCEL_COLUMN = auto()
    COLOR_CELL_TYPE = auto()
    DICT = auto()
    FONT = auto()

class StateMachines(Enum):
    MAIN_MENU = 0
    CONFIG = 1,
    CFG_TYPE = 2

class TypesMenu(StrEnum):
    ADD = "Nieuw type toevoegen"
    CONT = "Doorgaan naar volgende stap"

class TypesMethod(StrEnum):
    CEL_KLEUR = "celkleur"
    CEL_INHOUD = "celinhoud"

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
    TYPES_MATCH_STRING = "match_string"
    WIDTH = "width"
    HEIGHT = "height"
    BACKGROUND_COLOR = "background_color"
    FONT = "font"
    FONT_SIZE = "font_size"
    MARGIN = "margin"
    COLUMN_LETTER = "column_letter"


TYPE_FIELDS = [CfgFields.TYPES_NAME,
               CfgFields.TYPES_GENERATED_IMAGE_TEXT_COLOR,
               CfgFields.TYPES_METHOD,
               CfgFields.TYPES_COLUMN,
               CfgFields.TYPES_EXCEL_FILE_COLOR_TYPE,
               CfgFields.TYPES_EXCEL_FILE_CELL_COLOR,
               CfgFields.TYPES_MATCH_STRING,]

class Acties(StrEnum):
    MAAK_NIEUWE_CONFIG = "Maak een compleet nieuwe configuratie."
    LAAD_BESTAANDE_CONFIG = "Laad bestaande configuratie in als actieve configuratie."
    GENEREER_PLAATJES = "Genereer plaatjes van de termen, op basis van actieve configuratie."
    EXIT = "Sluit programma af."


CONFIG_FOLDER = "configuraties"
OUTPUT_FOLDER = "images"


class ViewState(Enum):
    EMPTY = auto()
    MESSAGE = auto()
    TEXT_INPUT = auto()
    TYPE_OVERVIEW = auto()
    NUMBER_INPUT = auto()
    LIST = auto()
    BUTTON = auto()
    PROGRESS = auto()
