
from Constants import Acties
from Controller import Controller
from View import View

actions = [Acties.MAAK_NIEUWE_CONFIG, Acties.LAAD_BESTAANDE_CONFIG, Acties.EXIT]
controller = Controller()


View.get().setList("Kies een actie: ", actions, controller.callbackActies)
View.get().run()



