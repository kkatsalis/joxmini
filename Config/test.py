import json
import yaml
import sys
from Util import utilities

def yaml_to_json(filename):
    try:
        stream=open(filename, 'r') 
        data=yaml.load(stream)
        json_data=json.dumps(data)
        
        return json_data
    except IOError as err:
        print("IO error: {0}".format(err))
    
        
# import pickle
# import redis

json_object=yaml_to_json("jorch_config.yaml")
print json_object

utilities.set_json_to_redis("jorch-config", json_object)

json_object=utilities.get_json_from_redis("jorch-config")
print json_object

# r = redis.StrictRedis(host='localhost', port=6379, db=0)
# obj = yaml_to_json("test.yaml")
# pickled_object = pickle.dumps(obj)
# r.set('some_key', pickled_object)
# unpacked_object = pickle.loads(r.get('some_key'))
# print "kostas"+unpacked_object 




