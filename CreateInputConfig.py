import json
import os
import Constants
from Utils import add_base_path



def save_config(config, config_name):
    config_dir = add_base_path(Constants.CONFIG_FOLDER)
    config_name = os.path.join(config_dir, config_name)
    with open(config_name, "w") as f:
        json.dump(config, f, indent=2)
    print(f"Configuratie opgeslagen onder {config_name}")

