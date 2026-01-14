import copy

import Utils
from Constants import StateMachines, TYPE_FIELDS, CfgFields
from Singleton import Singleton

@Singleton
class Model:
   def __init__(self):
       self.current_state_machine = StateMachines.MAIN_MENU
       self.active_config_path = None
       self.active_config = None
       self.new_config_type = {}
       self.config_state_machine = {}
       self.type_state_machine = {}

   def get_active_cfg_name(self):
       if self.active_config_path is not None:
        return Utils.get_file_name_from_path(self.active_config_path)
       return None

   def set_active_cfg_path(self, path):
        self.active_config_path = path

   def set_active_cfg(self, config):
       self.active_config = config

   def get_active_cfg(self):
       return self.active_config

   def get_new_config_type(self):
       return self.new_config_type

   def check_types_not_empty(self):
       if "types" not in self.active_config:
           self.active_config["types"] = []

   def set_config_type(self):
       self.check_types_not_empty()
       self.active_config["types"].append(copy.deepcopy(self.new_config_type))

   def set_done_adding_types(self):
       self.check_types_not_empty()
       Model.get().config_state_machine[CfgFields.TYPES] = True

   def set_active_cfg_field(self, field_name, value=None):
       if value is not None:
           if field_name in TYPE_FIELDS:
               self.new_config_type[field_name] = value
           else:
            self.active_config[field_name] = value

       if field_name in TYPE_FIELDS:
            self.type_state_machine[field_name] = True
       else:
            Model.get().config_state_machine[field_name] = True



   def setConfigStateMachine(self, name):
       # Could we make this private, and let all cals go through setActiveConfigField?
       self.config_state_machine[name] = True

   def get_config_state_machine(self):
       return self.config_state_machine

   def get_type_state_machine(self):
       return self.type_state_machine

f = () # Error, this isn't how you get the instance of a singleton

