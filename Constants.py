from enum import StrEnum, Enum, auto
from aenum import Enum as BetterEnum


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
    DELETE_TYPE = 3

class TypesMenu(StrEnum):
    ADD = "Nieuw type toevoegen"
    DEL = "Een type verwijderen"
    CONT = "Doorgaan naar volgende stap"

class TypesMethod(StrEnum):
    CEL_KLEUR = "celkleur"
    CEL_INHOUD = "celinhoud"

class CfgFields(BetterEnum):
    INPUT_FILE_NAME = "input_file_name", "Naam van het excel bestand waar de termen in staan."
    FILE_HAS_HEADER = "file_has_header", "Of de eerste rij van het bestand de koptekst is"
    COLUMN_NAME = "column_name", "Welke kolom de termen bevat"
    TYPES = "types", "Een type verwijderen of toevoegen"
    TYPES_NAME = "name", "De naam van het type"
    TYPES_GENERATED_IMAGE_TEXT_COLOR = "generated_image_text_color", "Welke kleur tekst het gegenereerde plaatje moet hebben als het bij dit type hoort."
    TYPES_METHOD = "method", "Of de celkleur, of celinhoud bepaalt of een term bij dit type hoort"
    TYPES_COLUMN = "column", "Welke kolom de celkleur/tekst heeft die bepaalt of iets bij dit type hoort"
    TYPES_EXCEL_FILE_COLOR_TYPE = "excel_file_color_type", None
    TYPES_EXCEL_FILE_CELL_COLOR = "excel_file_cell_color", "De celkleur die aangeeft dat een term bij dit type hoort"
    TYPES_MATCH_STRING = "match_string", "De tekst die aangeeft dat een term bij dit type hoort"
    WIDTH = "width", "De breedte"
    HEIGHT = "height", "De hoogte"
    BACKGROUND_COLOR = "background_color", "De achtergrondkleur"
    FONT = "font", "Het font"
    FONT_SIZE = "font_size", "De tekstgrootte"
    MARGIN = "margin", "De tekstmarge"
    COLUMN_LETTER = "column_letter", None

    def __new__(cls, key, display):
        obj = object.__new__(cls)
        obj._value_ = key
        obj.display = display
        return obj

    @classmethod
    def from_any(cls, value):
        for m in cls:
            if value in (m.value, m.display):
                return m
        raise ValueError(f"{value!r} is not a valid Status")


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
    WIJZIG_CONFIG = "Wijzig de actieve configurate"


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
