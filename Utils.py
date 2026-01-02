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