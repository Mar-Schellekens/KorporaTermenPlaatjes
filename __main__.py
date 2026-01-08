from Actions import callbackActies
from Constants import Acties
from View import View

actions = [Acties.MAAK_NIEUWE_CONFIG, Acties.LAAD_BESTAANDE_CONFIG, Acties.EXIT]

View.get().setList("Kies een actie: ", actions, callbackActies)
View.get().run()



