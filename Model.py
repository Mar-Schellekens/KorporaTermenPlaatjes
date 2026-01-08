import copy

from Singleton import Singleton

@Singleton
class Model:
   def __init__(self):
       self.input_config_file_name = None
       self.activeConfigName = None
       self.activeConfig = None
       self.newConfigType = {}
       self.configStateMachine = {}
       self.typeStateMachine = {}

   def setActiveConfigName(self, config):
       self.activeConfigName = config

   def setActiveConfig(self, config):
       self.activeConfig = config

   def getActiveConfig(self):
       return self.activeConfig

   def getNewConfigType(self):
       return self.newConfigType

   def setConfigType(self):
       if "types" not in self.activeConfig:
           self.activeConfig["types"] = []
       self.activeConfig["types"].append(copy.deepcopy(self.newConfigType))
       print("blub")

   def setActiveConfigField(self, field_name, value=None):
       if value is not None:
           self.activeConfig[field_name] = value
       Model.get().configStateMachine[field_name] = True

   def setConfigTypeField(self, field_name, value):
       self.newConfigType[field_name] = value
       self.typeStateMachine[field_name] = True

   def setConfigStateMachine(self, name):
       # Could we make this private, and let all cals go through setActiveConfigField?
       self.configStateMachine[name] = True

   def getConfigStateMachine(self):
       return self.configStateMachine

   def getTypeStateMachine(self):
       return self.typeStateMachine

f = () # Error, this isn't how you get the instance of a singleton

