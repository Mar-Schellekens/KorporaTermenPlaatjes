from enum import Enum
from aenum import Enum as CoolEnum
from enum import StrEnum

class Config(StrEnum):
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

class Acties(StrEnum):
    MAAK_NIEUWE_CONFIG = "Maak een nieuwe configuratie."
    LAAD_BESTAANDE_CONFIG = "Laad bestaande configuratie in."
    EXIT = "Sluit programma af."
    VERANDER_CONFIG = "Verander de actieve configuratie."
    GENEREER_PLAATJES = "Genereer plaatjes van de termen, op basis van actieve configuratie."


CONFIG_FOLDER = "configuraties"

# class TextColor(Enum):
#     Brandweer = (214, 29, 44)
#     Politie = (0, 85, 255)
#     Standaard = (0, 29, 63)

