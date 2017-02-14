import uuid
import copy
import json
from jmachine import KvmMachine,LxcMachine
from jservice import Service
import jsonpickle
from json import JSONEncoder
from Util import utilities
from Config import global_variables 


class Stack(JSONEncoder):
    
    def __init__(self,stack_config, clouds,log_level):
         
        self.stack_id = uuid.uuid4()
        self.machine_ids=0
        self.kvm_machines=[] #List with Machines objects
        self.lxc_machines=[]
        self.services=[] #List with Services objects
    
        # LOGGING
        self.log_level = log_level
        self.log = None
        self.console = None
        # CLOUD
        self.clouds=clouds
        self.cloud_name=stack_config["stack-cloud"]#the name of the cloud e.g. "local"
        self.cloud_object=filter(lambda x: x.cloud_name == self.cloud_name,clouds)[0] #find correct cloud object
        

        if stack_config!=None:
            self.stack_name=stack_config["stack-name"]
                # PARSE MACHINES CONFIG
            self.machines_config=copy.copy(stack_config["machines-list"])
                # PARSE SERVICES  CONFIG      
            self.services_config=copy.copy(stack_config["services-list"])
            self.services_relations=copy.copy(stack_config["service-relations"]) 
            self.services_chains= copy.copy(stack_config["service-chains"]) 
                # ADD MACHINES
            self.add_machines(self.machines_config)
            
            utilities.get_qemu_kvm_info("ALL") # "ALL" or machine.qemu_machine_name
            
            # ADD SERVICES
            self.add_services(self.services_config)
                # ADD RELATIONS
                # self.add_service_relations(self.relations_config)
                # ADD CHAINS
                # self.add_service_chains(self.chains_config)
            print 'Stack added'

    ##    A. MACHINES METHODS    ##
    ##    A1. Get methods         ##
    def get_kvm_machines_status(self):
        data_str=jsonpickle.encode(self.kvm_machines)# returns str
        data=json.loads(data_str)        
        return data
    
    def get_lxc_machines_status(self):
        data_str=jsonpickle.encode(self.lxc_machines)# returns str
        data=json.loads(data_str)        
        return data
    
    def get_kvm_machine_status(self,stack_machine_name):
        for machine in self.kvm_machines:
            if machine.stack_machine_name==stack_machine_name:
                data_str=jsonpickle.encode(machine)# returns str
                data=json.loads(data_str)        
                return data
    
    def get_lxc_machine_status(self,stack_machine_name):
        for machine in self.lxc_machines:
            if machine.stack_machine_name==stack_machine_name:
                data_str=jsonpickle.encode(machine)# returns str
                data=json.loads(data_str)        
                return data
                
    def get_kvm_machine(self,stack_machine_name):
        for machine in self.kvm_machines:
            if machine.stack_machine_name==stack_machine_name:
                return machine
        
    def get_lxc_machine(self,stack_machine_name):
        for machine in self.lxc_machines:
            if machine.stack_machine_name==stack_machine_name:
                return machine
    
    # Find the juju machine name based on the stack machine name    
    def get_jujuName_from_kvmName(self,machine_name):
        #search in KVM machines
        kvm_machine=filter(lambda x: x.stack_machine_name == machine_name,self.kvm_machines)
        if kvm_machine[0]!=None:
            print "It is a KVM machine"
            return str(kvm_machine[0].juju_machine_name)
        return -1
    
    def get_jujuName_from_lxcName(self,machine_name):    
        #search in LXC machines
        lxc_machine=filter(lambda x: x.stack_machine_name == machine_name,self.lxc_machines)
        if lxc_machine[0]!=None:
            print "It is a LXC machine"
            return str(lxc_machine[0].juju_machine_name)
            
        return -1   
    
    # Check if stack machine name exists
    def kvm_machine_exists(self, machine_name):             
        kvm_machine=filter(lambda x: x.stack_machine_name == machine_name,self.kvm_machines)
        if not kvm_machine:
            return False
        else:
            return True
    
    def lxc_machine_exists(self, machine_name):             
        lxc_machine=filter(lambda x: x.stack_machine_name == machine_name,self.lxc_machines)
        if not lxc_machine:
            return False
        else:
            return True
   
    
    
    ##   A2. Add machines methods    ##    
    def add_machines(self, machines_config):     
        for machine_config in machines_config:
            if machine_config!=None:
                if self.kvm_machine_exists(machine_config["machine-name"]):
                    print "Machine name already in KVM machines"
                elif  self.lxc_machine_exists(machine_config["machine-name"]):
                    print "Machine name already in LXC machines"    
                else:  
                    if machine_config["machine-type"]==global_variables.KVM:
                        self.add_kvm_machine(machine_config)
                    elif machine_config["machine-type"]==global_variables.LXC:
                        self.add_lxc_machine(machine_config)
    
    
    def add_kvm_machine(self, machine_config):   
           
        machine_config["machine-spec"]=""
        new_machine=KvmMachine(self.machine_ids, machine_config)
        new_machine.juju_machine_name=self.cloud_object.add_machine(machine_config)
        new_machine.qemu_machine_name=global_variables.kvm_user+"-"+str(new_machine.juju_machine_name)
        self.kvm_machines.append(new_machine) 
        self.machine_ids+=1
        
        print "KVM machine added to Stack"
        return 
    

    #  "machine-spec": "3:lxc",   
    def add_lxc_machine(self, machine_config):   
        """ We temporarily switch the parent-machine-name from the Stack name to the Juju name"""
        
        parent_stack_name=machine_config["parent-machine-name"] 
        parent_juju_name=self.get_jujuName_from_kvmName(parent_stack_name)
        machine_config["machine-spec"]=parent_juju_name+":lxc" 
        machine_config["parent-machine-name"]=""          
        machine_config["juju-machine-name"]=parent_juju_name 
        
        new_machine=LxcMachine(self.machine_ids, machine_config)
        new_machine.juju_machine_name=self.cloud_object.add_machine(machine_config)
        new_machine.parent_id=parent_stack_name
        self.lxc_machines.append(new_machine) 
        self.machine_ids+=1
        print "LXC machine added to Stack"   

    
    def remove_machine(self,machine_id):    
        print 'Remove machine not implemented'
    
    
    
    
    
    ## B. SERVICES METHODS ##      
      
    def add_services(self,services_config):
        for service_config in self.services_config:
            if service_config!=None:
                self.add_service(service_config)
                

    def add_service(self, service_config):
        # Create Service Object
        new_service=Service(service_config,self)
        self.services.append(new_service) 
        
        # Deploy service
        new_service.deploy_service()
        # Add extra units
        units_in_kvm_machines_list=service_config["units-in-kvm-machines-list"]
        new_service.add_units_in_kvm_machines(units_in_kvm_machines_list)
        
        print 'Added new service'
    


       
    # Service Relations
    def add_service_relations(self, relations_config): 
        print "to do" 
        
     # Service Chains
    def add_service_chains(self, chains_config): 
        print "to do"    
    
    
    
            
    def dispose(self, service='all', unchain=True):
        self.log.debug('Dispose the stack ' + str(self.stack_id))
#         dispose_state = 0
#         self.stack_state = 'DISPOSING'
#         if service == 'all':
#             services = self.services
#         else:
#             services = service
# 
#         if unchain:
#             if self.state == 2:
#                 self.log.info('Unchain the stack ' + str(self.stack_id))
#                 for instance_p in services:
#                     index = self.find_index(service_relation, 'service_p', instance_p)
#                     instance_r = service_descriptor[index]['service_r']
#                     try:
#                         self.env.remove_relation(instance_p, instance_r)
#                         self.log.info('Unchained ' + instance_p +':'+instance_r)
#                         dispose_state += 1
#                     except:
#                         self.log.warn('relation ' + instance_p + ':' + instance_r + ' does not exist or already removed')
# 
#                 self.state = 1
#         else:
#             if self.state > 0 :
#                 self.log.info('Dispose the stack ' + str(self.stack_id))
#                 for instance in services:
#                     try:
#                         self.env.destroy_service(instance)
#                         self.log.info(instance + ' removed')
#                         dispose_state += 1
#                     except:
#                         self.log.warn('Service ' + instance + ' does not exist or already removed')
# 
#                 self.state = 0
# 
#         if dispose_state == len(services):
#             self.stack_state = 'DISPOSE_COMPLETE'
#             self.log.info('Stack state is : ' + self.stack_state)
# 
#         if self.msgbus:
#             message = {
#                 'phase': 'dispose',
#                 'stack_id': str(self.stack_id),
#                 'state': self.stack_state,
#                 'parameters': {
#                     'state': str(dispose_state)
#                 }
#             }
#             # respond to the SO with the ID of what juju creates
#             self.log.debug('responding back to the SO with: ' + str(message))
#             self.msgbus_client.wait(self.msgbus_client.basic_publish(exchange='hurtle', routing_key='events-resp',
#                                                                      body=json.dumps(message)))

    def upgrade(self, service='all'):
        self.log.debug('Upgrade the stack ' + str(self.stack_id))
#         upgrade_state = 0
#         self.stack_state = 'UPGRADING'
#         if service == 'all':
#             services = self.services
#         else:
#             services = service
# 
#         for instance in services:
#             index = self.find_index(service_descriptor, 'service', instance)
#             try:
#                 self.env.update_service(service_descriptor[index]['service'], service_descriptor[index]['charm'],
#                                     num_units=service_descriptor[index]['num_units'])
#                 upgrade_state += 1
#             except:
#                 self.log.warn('upgrade ' + instance + ' failed')
# 
#         if upgrade_state == len(services):
#             self.stack_state = 'UPGRADE_COMPLETE'
#             self.log.info('Stack state is : ' + self.stack_state)
# 
#         if self.msgbus:
#             message = {
#                 'phase': 'upgrade',
#                 'stack_id': str(self.stack_id),
#                 'state': self.stack_state,
#                 'parameters': {
#                     'state': str(upgrade_state)  # 0 : init, 1 : deploy, and 2 : chain
#                 }
#             }
#             # respond to the SO with the ID of what juju creates
#             self.log.debug('responding back to the SO with: ' + str(message))
#             self.msgbus_client.wait(self.msgbus_client.basic_publish(exchange='hurtle', routing_key='events-resp',
#                                                                      body=json.dumps(message)))

    def provision(self, service='all', scale='in', constraints={'cpu-cores': 2, 'mem': 8}):
        """provision the service given the scale, and constraint.
        scale = { 'in', 'out','up', 'down'} : in/out: add/remove resources, up/down: add/remove unit
        """
        self.log.debug('Provision the stack ' + str(self.stack_id))
#         provision_state = 0
#         self.stack_state = 'PROVISIONING'
#         if service == 'all':
#             services = self.services
#         else:
#             services = service
# 
#         if scale == 'in' or scale == 'out':
#             if constraints is None:
#                 self.log.warn('Failed to scale ' + scale +': undefined constraints')
#                         # now set the machine resources
#             # Too coarse: apply the same constraints to all service
#             for instance in services:
#                 try:
#                     self.env.set_constraints(instance, constraints)
#                     self.log.info('Scaled ' + scale + ' ' + service + 'with ' + str(self.env.get_constraints(instance)))
#                     provision_state += 1
#                 except:
#                     self.log.warn('Failed to scale ' + scale + ': undefined constraints')
# 
#         elif scale == 'up':
#             self.log.debug('Scaling up request')
#             for instance in services:
#                 index = self.find_index(service_descriptor, 'service', instance)
#                 unit_count = len(self.env.status(instance)['Units'])
#                 max_unit = service_descriptor[index]['max_unit']
#                 if (max_unit - unit_count - 1) >  0:
#                     self.env.add_units(instance, num_units=1)
#                     provision_state += 1
#                     self.log.info('Scaled ' + scale + ' ' + service + 'add 1 unit')
#                 else:
#                     self.log.warn('Failed to scale ' + scale + ': reached max number of unit ' + max_unit)
# 
#         elif scale == 'down':
#             self.log.debug('Scalng down request')
#             for instance in services:
#                 index = self.find_index(service_descriptor, 'service', instance)
#                 unit_count = len(self.env.status(instance)['Units'])
#                 unit_ids = sorted(self.env.status(instance)['Units'])[:-1]
#                 if (unit_count - MIN_UNIT - 1) > 0:
#                     self.env.remove_units(instance, unit_ids)
#                     provision_state += 1
#                     self.log.info('Scaled ' + scale + ' ' + service + 'removed 1 unit')
#                 else:
#                     self.log.warn('Failed to scale ' + scale + ': reached min number of unit ' + MIN_UNIT)
# 
#         else:
#             self.log.warn('Unknown scale ' + scale + 'request')
# 
#         if provision_state == len(services):
#             self.stack_state = 'PROVISION_COMPLETE'
#             self.log.info('Stack state is : ' + self.stack_state)
# 
#         if self.msgbus:
#             message = {
#                 'phase': 'provision',
#                 'state': self.stack_state,
#                 'stack_id': str(self.stack_id),
#                 'parameters': {
#                     'state': str(provision_state)
#                 }
#             }
#             # respond to the SO with the ID of what juju creates
#             self.log.debug('responding back to the SO with: ' + str(message))
#             self.msgbus_client.wait(self.msgbus_client.basic_publish(exchange='hurtle', routing_key='events-resp',
#                                                                      body=json.dumps(message)))

    def chain(self,service='all'):
        self.log.debug('Chaining the stack: ' + str(self.stack_id))

#         chain_state = 0
#         extra = {}
#         self.stack_state = 'CHAINING'
#         if service == 'all':
#             services = self.services
#         else:
#             services = service
# 
#         if self.state == 1:
#             for instance_p in services:
#                 index = self.find_index(service_relation, 'service_p', instance_p)
#                 #print str(index)
#                 if index is not None:
#                     instance_r = service_relation[index]['service_r']
#                     # we could also check if the instance_r is deployed
#                     if instance_r in services:
#                         try:
#                             self.env.add_relation(instance_p, instance_r)
#                             self.log.info(instance_p + ':' + instance_r + ' relation added')
#                             chain_state += 1
#                             extra.update({instance_p+instance_r: 'success'})
#                         except:
#                             self.log.warn('relation ' + instance_p + ':' + instance_r + ' does not exist or already exists')
#                             extra.update({instance_p+instance_r: 'failed'})
# 
#             self.state = 2
# 
#             if chain_state == len(services):
#                 self.stack_state = 'CHAIN_COMPLETE'
#                 self.log.info('Stack state is : ' + self.stack_state)
# 
#             if self.msgbus:
#                 message = {
#                     'phase': 'chain',
#                     'state': self.stack_state,
#                     'stack_id': str(self.stack_id),
#                     'parameters': extra
#                 }
#                 # respond to the SO with the ID of what juju creates
#                 self.log.debug('responding back to the SO with: ' + str(message))
#                 self.msgbus_client.wait(self.msgbus_client.basic_publish(exchange='hurtle', routing_key='events-resp',
#                                                                      body=json.dumps(message)))

    def configure(self,service='all'):
        self.log.info('Configuring the stack ' + str(self.stack_id))

#         configure_state = 0
#         self.stack_state = 'CONFIGURING'
#         if service == 'all':
#             services = self.services
#         else:
#             services = service
# 
#         # to improve : add a service_config dict
#         for instance in services:
#             configure_state += 1
#             if instance == 'oai-epc':
#                 self.env.set_config('oai-epc', {'eth': 'eth3', 'gummei_tai_mnc':'93'})
#             elif instance == 'oai-enb':
#                 self.env.set_config('oai-enb', {'eth': 'eth4'})
#                 self.env.set_config('oai-enb', {'rrh_active': 'yes'})
#                 self.env.set_config('oai-enb', {'rrh_if_name': 'eth0'})
#                 self.env.set_config('oai-enb', {'downlink_frequency': '2680000000L'})
#                 self.env.set_config('oai-enb', {'uplink_frequency_offset': '-120000000'})
#                 self.env.set_config('oai-enb', {'eutra_band': '7'})
#                 self.env.set_config('oai-enb', {'remote_monitoring': 'yes'})
# 
#         if configure_state == len(services):
#             self.stack_state = 'CONFIGURE_COMPLETE'
#             self.log.info('Stack state is : ' + self.stack_state)
# 
#         if self.msgbus:
#             message = {
#                 'phase': 'configure',
#                 'state': self.stack_state,
#                 'stack_id': str(self.stack_id),
#                 'parameters': {
#                     'state': str(configure_state)
#                 }
#             }
#             # respond to the SO with the ID of what juju creates
#             self.log.debug('responding back to the SO with: ' + str(message))
#             self.msgbus_client.wait(self.msgbus_client.basic_publish(exchange='hurtle', routing_key='events-resp',
#                                                                      body=json.dumps(message)))

    def deploy(self,service='all'):
        self.log.debug('Deploying the stack ' + str(self.stack_id))

#         deploy_state = 0
#         extra={}
#         self.stack_state = 'DEPLOYING'
#         if service == 'all':
#             services = self.services
#         else:
#             services = service
# 
#         # once the juju command to deploy/create stuff is issued
#         # a reference/handle/ID needs to be sent back to the SO via message bus
#         if self.state == 0:
#             self.stack_id = uuid.uuid4()
#             self.log.info('Deploying the stack: ' + str(self.stack_id))
#             # TODO make single tenant request to juju to create OAI stack
#             # XXX either return to the SO the ID of the stack that is created or create and mange one here
# 
#             for instance in services:
#                 index = self.find_index(service_descriptor,'service',instance)
#                 #print str(index)+'. ' + str(instance)
#                 try:
#                     self.env.deploy(service_descriptor[index]['service'], service_descriptor[index]['charm'], num_units=service_descriptor[index]['num_units'],
#                                     config=None, constraints=service_descriptor[index]['constraints'], machine_spec=service_descriptor[index]['machine_spec'])
#                     deploy_state += 1
#                     self.log.info('deployed: ' + instance)
#                     #time.sleep(10)
#                     extra.update({instance: 'success'})
#                 except:
#                     self.log.warn('deploy failed: ' + instance + ' does not exist or already exists')
#                     extra.update({instance: 'failed'})
#             # we may use the env uuid
#             self.state = 1
# 
#         else:
#             self.log.warn('service already deployed, to redeploy upgrade is needed')
#             # XXX can be implemented later
# 
#         if deploy_state == len(services):
#             self.stack_state = 'DEPLOY_COMPLETE'
#             self.log.info('Stack state is : ' + self.stack_state)
#         #else:
#         # note the failed service and send back to the higher level orch logic
# 
#         if self.msgbus and self.state == 1:
#                # manage the ID
#                message = {
#                    'phase': 'deploy',
#                    'state': self.stack_state,
#                    'stack_id': str(self.stack_id),
#                    'parameters': extra
#                }
#                # respond to the SO with the ID of what juju creates
#                self.log.debug('responding back to the SO with: ' + str(message))
#                self.msgbus_client.wait(self.msgbus_client.basic_publish(exchange='hurtle', routing_key='events-resp',
#                                                                         body=json.dumps(message)))
# 
#         return self.stack_id

    def resolver(self,service='all',retry=False):

        self.log.info('Trying to resolve failures for the stack ' + str(self.stack_id))

#         resolve_state = 0
#         extra = {}
#         self.stack_state = 'RESOLVING'
# 
#         if service == 'all':
#             services = self.services
#         else:
#             services = service
# 
#         for instance in services:
#             try:
#                 self.env.resolved(self.service_unit(service=instance), retry)
#                 self.log.info('resloved: ' + instance)
#                 resolve_state += 1
#                 extra.update({instance: 'success'})
#             except:
#                 self.log.warn('resolved failed: ' + instance )
#                 extra.update({instance: 'failed'})
# 
#         if resolve_state == len(services):
#             self.stack_state = 'RESOLVE_COMPLETE'
#             self.log.info('Stack state is : ' + self.stack_state)
# 
#         if self.msgbus and self.state > 0:
#             # manage the ID
#             message = {
#                 'phase': 'resolve',
#                 'state': self.stack_state,
#                 'stack_id': str(self.stack_id),
#                 'parameters': extra
#             }
#             # respond to the SO with the ID of what juju creates
#             self.log.debug('responding back to the SO with: ' + str(message))
#             self.msgbus_client.wait(self.msgbus_client.basic_publish(exchange='hurtle', routing_key='events-resp',
#                                                                      body=json.dumps(message)))


   