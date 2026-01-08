import sys
from pathlib import Path


def let_user_choose_actie(acties):
    for i, actie in enumerate(acties, start=1):
        print(f"{i}. {str(actie)}", "")

    while True:
        choice = input("\nType het nummer van uw keuze: ").strip()
        if choice.isdigit():
            index = int(choice) - 1
            if 0 <= index < len(acties):
                actie = acties[index]
                break
        print("Invalide keuze. Probeer opnieuw.")

    return actie

def add_base_path(relative_path: str) -> Path:
    if getattr(sys, 'frozen', False):
        base_path = Path(sys._MEIPASS) #ignore warning
    else:
        base_path = Path(__file__).parent
    return base_path / relative_path

def convert_excel_colors_to_string(list_of_color_tuples):
    return [f"{value}. {ctype}" for value, ctype in list_of_color_tuples]