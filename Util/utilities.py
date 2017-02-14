import logging
import time
import yaml
import json
import pickle
import redis
import sys
import libvirt
from Config import global_variables


    
def init_logger(self, console,log,logger_name):
      
        # define a Handler which writes INFO messages or higher to the sys.stderr
        self.console = logging.StreamHandler()
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        self.console.setFormatter(formatter)
        # add the handler to the root logger

        logging.getLogger('').addHandler(self.console)
        self.log = logging.getLogger('main')

        if self.log_level == 'debug':
            self.console.setLevel(logging.DEBUG)
            self.log.setLevel(logging.DEBUG)
        elif self.log_level == 'info':
            self.console.setLevel(logging.INFO)
            self.log.setLevel(logging.INFO)
        elif self.log_level == 'warn':
            self.console.setLevel(logging.WARNING)
            self.log.setLevel(logging.WARNING)
        elif self.log_level == 'error':
            self.console.setLevel(logging.ERROR)
            self.log.setLevel(logging.ERROR)
        elif self.log_level == 'critic':
            self.console.setLevel(logging.CRITICAL)
            self.log.setLevel(logging.CRITICAL)
        else:
            self.console.setLevel(logging.INFO)
            self.log.setLevel(logging.INFO)

     
def logger(self, message, level='info'):
 
    log_color = [{'level':' error',  'color': '\033[91m'}, # debug level 0
             {'level': 'warn' ,  'color': '\033[93m'},  # debug level 1
             {'level': 'notice', 'color': '\033[92m'},  # debug level 2
             {'level': 'info',   'color': '\033[0m'},   # debug level 3
             {'level': 'debug',  'color': '\033[0m'}]   # debug level 4
        
    index = self.find_index(log_color, 'level', level)
    if self.debug < index:
        return
    ts = time.strftime('%d %b %Y %H:%M')
    message = ts + ' [' + level + '] ' + message
    print log_color[index]['color']+ message
    
# tested:ok    
def find_index(dicts, key, value):
    for i, d in enumerate(dicts):
        if d.get(key, None) == value:
            return i
    else:
        return None
    
    

# tested:ok
def yaml_to_json(filename):
    try:
        stream=open(filename, 'r') 
        data=yaml.load(stream)
        json_data=json.dumps(data)
        print(json_data)
        return json_data
    except IOError as err:
        print("IO error: {0}".format(err))
        
        
# tested:ok
def set_json_to_redis(key,json_object):
    try:
        message=""
        if(get_json_from_redis(key) is None):
            host=global_variables.REDIS_SERVER
            port=global_variables.REDIS_PORT
            r = redis.StrictRedis(host, port, db=0)
            pickled_object = pickle.dumps(json_object)
            r.set(key, pickled_object)
            print "Key %s added to REDIS " %key
            message="KEY added"
        else:
            message="KEY already exists"    
        return message 
    except:
        print "Unexpected error in SET KEY from Redis:", sys.exc_info()[0]
        raise

def get_json_from_redis(key):

    try:
        r = redis.StrictRedis(global_variables.REDIS_SERVER, global_variables.REDIS_PORT, db=0)
        if(r.get(key) is not None):
            unpacked_object = pickle.loads(r.get(key))        
            return unpacked_object    
        else:
            return None # kEY does not exists
    except:
        print "Unexpected error in GET KEY from Redis:", sys.exc_info()[0]
        raise

def del_json_from_redis(key):
    try:
        host=global_variables.REDIS_SERVER
        port=global_variables.REDIS_PORT
        r = redis.StrictRedis(host, port, db=0)
        if(r.get(key) is not None):
            r.delete(key)        
            print "Key %s deleted from REDIS " %key
            return True # kEY does not exists
    except:
        print "Unexpected error in DEL KEY from Redis:", sys.exc_info()[0]
        raise

        
def get_machine_type(constraints):
    if(constraints==1):
        machine_type="small.1"
        return machine_type   

    
def create_json():    
    data = {}
    data['user'] = "a223"
    data['slice-id'] = "adsf"
    json_data = json.dumps(data)
    
    return json_data    

def filter_json(obj,field_name):
    json_data  = json.loads(obj)
    #check if fie
    field=json_data.pop(field_name) 
    return field   


def get_qemu_kvm_info(self,qemu_machine_name="ALL"):
    
    conn=libvirt.open(global_variables.QEMU_PATH)       
    domainIDs=conn.listDomainsID()
    dict={}            
    for kvm_id in domainIDs:
        dom = conn.lookupByID(kvm_id)
        infos = dom.info()
        if qemu_machine_name!="ALL" and dom.name()!=qemu_machine_name:
            continue
        else:
            data={}
            
            data['ID'] = kvm_id
            data['Name'] = dom.name()
            data['State'] = infos[0]
            data['Max Memory'] = infos[1]
            data['Number of virt CPUs'] = infos[3]
            data['CPU Time (in ns)'] = infos[2]
            
            dict[kvm_id]=data
            
    return dict         
            
            
                