from types import DictType,ListType,StringType
from jujuclient import Environment
import json
import sys
import logging
import pprint
import time
from Util import utilities
import copy
from Config import global_variables

class Cloud(object):
    """Juju Cloud: Shared between Slices """

    def __init__(self,cloud_name):
        self.cloud_name = cloud_name    #e.g. manual
        self.cloud = Environment.connect(cloud_name)
        self.cloud_is_healthy=True
        self.watcher = None
        self.log = None
        self.console = None
        
         
    def get_facades(self):
        obj=self.cloud.facades
        return obj

    def get_users(self):
        obj=self.cloud.users.list()
        return obj
          
    def get_charms(self):
        obj=self.cloud.charms.list()
        return obj
        
    def get_config(self):
        obj=self.cloud.get_env_config()
        return obj
       
    def get_info(self):
        obj=self.cloud.info()
        return obj
    
            
    def check_cloud_health(self):
        print "environment health"    

    def get_service_status(self):
        status=self.cloud.status()['Services']
        return status    
    
    def get_machines(self):
        machines=self.cloud.status()['Machines']
        return machines    

    def add_machine(self,machine_config):
       
        if machine_config is None:
            self.log.warn('Failed to add machine: no machine is defined')
        else:
            
            
            # pre-conditions
            if machine_config["machine-type"]==global_variables.KVM:
                kvm_machines_num=self.cloud.status()['Machines'].keys().__len__()
            elif machine_config["machine-type"]==global_variables.LXC:    
                machine_name=machine_config["juju-machine-name"]
                containers_num=self.cloud.status()['Machines'][machine_name]["Containers"].keys().__len__()   
                 
            # add machine    
            self.cloud.add_machine(machine_config["series"], 
                                 machine_config["constraints"], 
                                 machine_config["machine-spec"], 
                                 machine_config["parent-machine-name"], 
                                 machine_config["container-type"])
            
            # post-conditions
            if machine_config["machine-type"]==global_variables.KVM:
                new_machine_id=-1
                time.sleep(5)
                timeout = time.time() + 60*0.2   #  0.2 minutes from now
                while(True):
                    if(self.cloud.status()['Machines'].__len__()>kvm_machines_num):
                        print self.cloud.status()['Machines'].keys()
                        results = map(int, self.cloud.status()['Machines'].keys())
                        new_machine_id=max(results)    
                        break
                    if time.time() > timeout:
                        new_machine_id=-1
                        break
                
                return new_machine_id
            elif machine_config["machine-type"]==global_variables.LXC:
                
                time.sleep(5)
                timeout = time.time() + 60*0.2   #  0.2 minutes from now
                while(True):
                    machine_name=machine_config["juju-machine-name"]
                    keys=self.cloud.status()['Machines'][machine_name]["Containers"].keys()
                    if keys>containers_num:
                        new_machine_id=max(keys)
                        break
                    if time.time() > timeout:
                        break
                return new_machine_id  
    
    def delete_machines(self,data):
        machine_ids=[]
        for key,value in data.items():
            machine_ids.append(str(value))
        
        # machine_ids=['2','3']             
        assert type(machine_ids) is ListType, "machine_ids is not a list"
        try: 
            self.cloud.destroy_machines(machine_ids, force=False) 
            x=', '.join(map(str, machine_ids))
            return "Machines deleted: %s"%x
        except :
            return str(sys.exc_info()[1])

    
    #add local charm to the env
    # TODO : make a list of charm dir
    def cloud_charm_dir(self,charm_dir='~/charmstore',charm_name='',series='trusty'):
        self.charm = self.cloud.add_local_charm_dir(charm_dir+'/'+series+'/'+charm_name,series)

    def close_cloud(self):
        self.log.info('closing juju env: ' + str(self.env_name))
        self.cloud.close()
    
    def cloud_watcher(self):
        for change_set in self.watcher:
            self.log.debug(pprint.pprint(change_set))        
 
    def find_service_name(self,service_name):
        print 'todo'
        return False
 
