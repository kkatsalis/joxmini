import copy
import json
from Util import utilities
import sys
from Config import global_variables



class Machine(object):   
  
  
    def __init__(self,stack_machine_id,machine_config):
        
        self.juju_machine_name=""  # value assigned by juju 
        
        
        try:
            self.stack_machine_id=stack_machine_id
            self.machine_type=machine_config["machine-type"]
            self.machine_template=machine_config["machine-template"]
            self.stack_machine_name=machine_config["machine-name"]  #local to stack
            self.series=machine_config["series"]
            self.container_type=machine_config["container-type"]
            self.parent_id=machine_config["parent-machine-name"]
            self.machine_spec=machine_config["machine-spec"]
            self.constraints=machine_config["constraints"]
        except ValueError:
            print 'Decoding JSON machine config has failed'
         
class KvmMachine(Machine):
    
    def __init__(self,stack_machine_id,machine_config):
        Machine.__init__(self, stack_machine_id,machine_config)
        
        self.qemu_machine_name=""
        
        if machine_config["machine-type"]==global_variables.KVM and machine_config["machine-template"]!="":
            key=global_variables.config_key
            jox_config=utilities.get_json_from_redis(key)
            for x in range (0,len(jox_config["kvm-machines-types"])):
                if jox_config["kvm-machines-types"][x].get("machine-type")== self.machine_template:
                    self.constraints=copy.deepcopy(jox_config["kvm-machines-types"][x].get("constraints"))
                    print self.constraints
    

   
    
class LxcMachine(Machine):
    
    def __init__(self,stack_machine_id,machine_config):
        Machine.__init__(self, stack_machine_id,machine_config)
        
        if machine_config["machine-type"]==global_variables.LXC and machine_config["machine-template"]!="":
            key=global_variables.config_key
            jox_config=utilities.get_json_from_redis(key)
            for x in range (0,len(jox_config["lxc-machines-types"])):
                if jox_config["lxc-machines-types"][x].get("machine-type")== self.machine_template:
                    self.constraints=copy.deepcopy(jox_config["lxc-machines-types"][x].get("constraints"))
                    print self.constraints   