import uuid
import pprint
import time
from Util import utilities
from types import DictType,StringType
from Config import global_variables

class Service(object):
        
    def __init__(self,service_config,stack_object):
        
        self.stack=stack_object
        self.service_state="NOT DEPLOYED"
        self.deployed_units=0 # Units list
        self.initial_deployment={}
        
        if service_config!=None: 
            self.service_id = uuid.uuid4()
            self.stack_service_name=service_config["stack-service-name"]
            self.description=service_config["description"]
            self.charm_url=service_config["charm"]
            self.max_units=service_config["max-units"]
            
            self.initial_deployment["config"]=service_config["initial-deployment"]["config"]
            self.initial_deployment["units_number"]=service_config["initial-deployment"]["units-number"]
            self.initial_deployment["machine_type"]=service_config["initial-deployment"]["machine-type"]
            self.initial_deployment["stack_machine_name"]=service_config["initial-deployment"]["stack-machine-name"]
            self.initial_deployment["constraints"]=service_config["initial-deployment"]["constraints"]
           
                
       
    def set_service_charm_url(self):  
        exists=self.stack.cloud_object.find_service_name(self.stack_service_name)
        if(exists):
            print  "Service name exists"
        else:
            self.stack.cloud_object.cloud.set_charm(self.stack_service_name, self.charm_url)
            print  "S"


    def get_service_status(self, field):
        """ field = ALL, STATUS or UNITS"""
        if self.stack_service_name is None:
            self.log.warn('No Service is defined')
        else:
            if(field=="ALL"):
                status=self.cloud.status()['Services'][self.service_name]
                pprint.pprint(status)  
            elif(field=="STATUS"):
                status= self.cloud.status()['Services'][self.service_name]['Status'].values()[0]
            elif(field=="UNITS"):
                status= self.cloud.status()['Services'][self.service_name]['Units'].keys()[0]
            
            return status


    def deploy_service(self):
        """" Initial Service Deployment"""

        # Check if Service name exists
        if self.stack_service_name in self.stack.cloud_object.cloud.status()['Services']:
            print "Service name already exists"
            return
        else:
            if self.initial_deployment["stack_machine_name"]=="":
                    print "A new machine will be used"
            elif (self.initial_deployment["machine_type"]==global_variables.KVM):
                print "Existing KVM machine will be used"
                machine=self.stack.get_kvm_machine(self.initial_deployment["stack_machine_name"])
                machine_spec=str(machine.juju_machine_name)
            elif (self.initial_deployment["machine_type"]==global_variables.LXC):
                print "Existing LXC machine will be used"
                machine=self.stack.get_lxc_machine(self.initial_deployment["stack_machine_name"])
                machine_spec=machine.juju_machine_name      
                        
                        
            self.stack.cloud_object.cloud.deploy(
                self.stack_service_name, 
                self.charm_url, 
                self.initial_deployment["units_number"],
                self.initial_deployment["config"], 
                self.initial_deployment["constraints"], 
                machine_spec
                )
        return
    
    def add_units_in_kvm_machines(self,units_in_kvm_machines_list):
        for units_in_kvm_machine in units_in_kvm_machines_list:
            self.add_units_in_machine(units_in_kvm_machine)
            
    
    def add_units_in_kvm_machine(self,units_in_kvm_machine):
        units_number=units_in_kvm_machine.get("units-number")
        
        units=self.deployed_units+ units_number
        if units>self.max_units:
            print "you want to add too many units"
        else:
            if units_in_kvm_machine.get("machine-to-deploy")=="new":
                machine_config=units_in_kvm_machine.get("machine")
                self.stack.add_kvm_machine(machine_config)
                stack_machine_name=machine_config["stack-machine-name"]
                machine_spec=self.stack.juju_machine_name(stack_machine_name)
                while units_number>0:
                    self.cloud.add_unit(self, self.service_name,machine_spec)
                    units_number-=1
            elif units_in_kvm_machine.get("machine-to-deploy")=="random":
                """Add n units of a given service.
                Machines will be allocated from the iaas provider
                or unused machines in the environment that
                match the service's constraints."""
                self.cloud.add_units(self, self.stack_service_name, units_number)
    
    

    # Delete Service - Examples of parametes tested  
    # service_name="mysql"
    # env_destroy_service(service_name)
    def cloud_destroy_service(self,service_name):
        assert type(service_name) is StringType, "service_name is not a String" 
        self.env.destroy_service(service_name)
        print "service deleted: ",service_name 
            

        
   