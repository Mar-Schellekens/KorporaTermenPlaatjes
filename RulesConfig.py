import xml.etree.ElementTree as ET

from Constants import CfgFields
from Model import Model


def apply_tint(rgb, tint):
    """
    Apply Excel tint to an RGB color.
    rgb: 'RRGGBB'
    tint: float in range [-1.0, 1.0]
    """
    r = int(rgb[0:2], 16)
    g = int(rgb[2:4], 16)
    b = int(rgb[4:6], 16)

    def tint_channel(c):
        if tint < 0:
            return int(c * (1 + tint))
        else:
            return int(c + (255 - c) * tint)

    r = tint_channel(r)
    g = tint_channel(g)
    b = tint_channel(b)

    return f"{r:02X}{g:02X}{b:02X}"

def get_theme_colors(wb):
    """
    Parse theme XML and return list of base theme colors as hex strings.
    """
    if not wb.loaded_theme:
        return []

    root = ET.fromstring(wb.loaded_theme)
    ns = {"a": "http://schemas.openxmlformats.org/drawingml/2006/main"}

    scheme = root.find(".//a:clrScheme", ns)
    if scheme is None:
        return []

    order = [
        "lt1", "dk1", "lt2", "dk2",
        "accent1", "accent2", "accent3",
        "accent4", "accent5", "accent6",
        "hlink", "folHlink"
    ]

    colors = []
    for key in order:
        el = scheme.find(f"a:{key}", ns)
        if el is None:
            colors.append(None)
            continue

        srgb = el.find("a:srgbClr", ns)
        if srgb is not None:
            colors.append(srgb.attrib["val"])
        else:
            colors.append(None)

    return colors

def get_cell_color(cell, workbook):
    """Returns the RGB hex color of a cell, handling RGB, theme, and indexed colors."""
    color = cell.fill.start_color
    if color is None:
        return None
    if cell.fill.patternType is None:
        return "rgb", "geen kleur", "#FFFFFF"

    if color.type == "rgb":
        return "rgb", color.rgb, f"#{color.rgb[-6:]}"
    elif color.type == "theme":
        theme_colors = get_theme_colors(workbook)
        if color.theme >= len(theme_colors):
            return None

        base = theme_colors[color.theme]
        if base is None:
            return None

        # apply tint if present
        if color.tint is not None:
            base = apply_tint(base, color.tint)

        hex_col = f"#{base}"

        return "theme", str(color.theme), hex_col
    return None

def get_all_colors_in_column(sheet, col_index, workbook):
    """Returns a set of all unique colors in a column."""
    colors = []
    min_row = 2

    for row in sheet.iter_rows(min_row = min_row):

        cell = row[col_index]
        type, value, hex_col = get_cell_color(cell, workbook)

        if (type, value, hex_col) not in colors:
            colors.append((type, value, hex_col))

    return colors

def is_valid_hex_color(s):
    """Validate hex color like #FFF or #FF8040"""
    s = s.lstrip("#")
    return len(s) in (3, 6) and all(c in "0123456789abcdefABCDEF" for c in s)
