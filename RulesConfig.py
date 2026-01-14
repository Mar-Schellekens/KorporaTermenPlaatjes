def get_cell_color(cell, workbook):
    """Returns the RGB hex color of a cell, handling RGB, theme, and indexed colors."""
    color = cell.fill.start_color
    if color is None:
        return None

    if color.type == "rgb":
        return "rgb", color.rgb  # Already in hex
    elif color.type == "theme":
        return "theme", str(color.theme)
    return None

def get_all_colors_in_column(sheet, col_index, workbook):
    """Returns a set of all unique colors in a column."""
    colors = []

    for row in sheet.iter_rows():
        cell = row[col_index]
        type, value = get_cell_color(cell, workbook)
        if (type, value) not in colors:
            colors.append((type, value))

    return colors

def is_valid_hex_color(s):
    """Validate hex color like #FFF or #FF8040"""
    s = s.lstrip("#")
    return len(s) in (3, 6) and all(c in "0123456789abcdefABCDEF" for c in s)
