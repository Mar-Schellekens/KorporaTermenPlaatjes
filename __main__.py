import glob
import json
import os

import Constants
from Actions import callbackActies
from Constants import Acties
from CreateInputConfig import modify_config, ask_modify_config, print_config, create_new_config, \
    let_user_choose_actie
from CreatePicture import create_picture
from LoadTerms import load_terms
from Singleton import app
from View import MenuApp



actions = [Acties.MAAK_NIEUWE_CONFIG, Acties.LAAD_BESTAANDE_CONFIG, Acties.EXIT]

app.get().ui.setList("Kies een actie: ", actions, callbackActies)
app.get().ui.run()



