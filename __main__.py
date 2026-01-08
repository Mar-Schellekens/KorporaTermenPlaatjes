from Actions import callbackActies
from Constants import Acties
from Singleton import app

actions = [Acties.MAAK_NIEUWE_CONFIG, Acties.LAAD_BESTAANDE_CONFIG, Acties.EXIT]

app.get().ui.setList("Kies een actie: ", actions, callbackActies)
app.get().ui.run()



