import copy

from Constants import StateMachines, TYPE_FIELDS, CfgFields
from Singleton import Singleton

@Singleton
class Model:
   def __init__(self):
       self.current_state_machine = StateMachines.MAIN_MENU
       self.active_config_name = None
       self.activeConfig = None
       self.newConfigType = {}
       self.configStateMachine = {}
       self.typeStateMachine = {}

   def set_active_cfg_name(self, config):
       self.active_config_name = config

   def set_active_cfg(self, config):
       self.activeConfig = config

   def get_active_cfg(self):
       return self.activeConfig

   def get_new_config_type(self):
       return self.newConfigType

   def setConfigType(self):
       if "types" not in self.activeConfig:
           self.activeConfig["types"] = []
       self.activeConfig["types"].append(copy.deepcopy(self.newConfigType))

   def set_done_adding_types(self):
       Model.get().configStateMachine[CfgFields.TYPES] = True

   def set_active_cfg_field(self, field_name, value=None):
       if value is not None:
           if field_name in TYPE_FIELDS:
               self.newConfigType[field_name] = value
           else:
            self.activeConfig[field_name] = value

       if field_name in TYPE_FIELDS:
            self.typeStateMachine[field_name] = True
       else:
            Model.get().configStateMachine[field_name] = True



   def setConfigStateMachine(self, name):
       # Could we make this private, and let all cals go through setActiveConfigField?
       self.configStateMachine[name] = True

   def getConfigStateMachine(self):
       return self.configStateMachine

   def getTypeStateMachine(self):
       return self.typeStateMachine

f = () # Error, this isn't how you get the instance of a singleton

