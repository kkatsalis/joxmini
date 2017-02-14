import json
from flask import Flask
from flask import request
from Util import utilities
import commentjson
import jsonpickle


################################################################
#                 WEB API
################################################################
flaskApp = Flask(__name__)
controller=object

def set_controller(control):
    global controller
    controller=control
    
        
@flaskApp.route('/jox')
def welcome():
    return "Welcome to jox REST API for JUJU version 1.25"

@flaskApp.route('/jox/config')
def get_jox_config():
    obj=utilities.get_json_from_redis("jox_config") 
    return json.dumps(obj)

@flaskApp.route('/jox/cloud/facades')
def cloud_facades():
    cloud_name=request.args["cloud"]
    data=controller.find_cloud_object(cloud_name).get_facades()
   
    return json.dumps(data)

@flaskApp.route('/jox/cloud/users')
def cloud_users():
    cloud_name=request.args["cloud"]
    data=controller.find_cloud_object(cloud_name).get_users()
    return json.dumps(data)

@flaskApp.route('/jox/cloud/config')
def cloud_config():
    cloud_name=request.args["cloud"]
    data=controller.find_cloud_object(cloud_name).get_config()
    return json.dumps(data)

@flaskApp.route('/jox/cloud/info')
def cloud_info():
    cloud_name=request.args["cloud"]
    data=controller.find_cloud_object(cloud_name).get_info()
    return json.dumps(data)

@flaskApp.route('/jox/cloud/charms')
def cloud_charms():
    cloud_name=request.args["cloud"]
    data=controller.find_cloud_object(cloud_name).get_charms()
    return json.dumps(data)

@flaskApp.route('/jox/cloud/services')
def cloud_services():
    cloud_name=request.args["cloud"]
    data=controller.find_cloud_object(cloud_name).get_service_status()
    return json.dumps(data)

@flaskApp.route('/jox/cloud/machines',methods=['GET'])
def cloud_machines():
    cloud_name=request.args["cloud"]
    
    if request.method == 'GET':
        data=controller.find_cloud_object(cloud_name).get_machines()
        return json.dumps(data)
    
@flaskApp.route('/jox/cloud/machines/qemu',methods=['GET'])
def cloud_kvm_machines():
    qemu_machine_name=request.args["machine"]
    
    if request.method == 'GET':
        data=utilities.get_qemu_kvm_info(qemu_machine_name)
        return json.dumps(data)   
    
    
    
@flaskApp.route('/jox/slice', methods=['GET', 'POST','DELETE'])
def slice_method():

    if request.method == 'GET':
        slice_name=request.args['slice']
        if request.args['config']=='running':
            data_str=controller.get_slice_data(slice_name)
            data=json.loads(data_str) 
        elif request.args['config']=='initial':
            data=utilities.get_json_from_redis(slice_name) # returns dict
           
        if 'field' in request.args:
            filtered_response=utilities.filter_json(data,request.args['field'])
            return json.dumps(filtered_response) 
        else:                  
            return json.dumps(data) 
    
    if request.method == 'POST':
        data=request.data
        json_body = commentjson.loads(data)
        slice_name=controller.add_slice(json_body) 
        if slice_name==0:
            return "Slice Already Exists"    
        else:
            return "New slice created! New SliceID: %s" %slice_name
            
    if  request.method == 'DELETE':
        return "NOT IMPLEMENTED"

@flaskApp.route('/jox/slice/stack', methods=['GET', 'POST', 'DELETE'])
def slice_stack_method():

    slice_name=request.args["slice"]
    
    if request.method == 'GET':
        stack_name=request.args["stack"]
        if request.args['config']=='running':
            data_str=controller.get_stack_data(slice_name,stack_name)
            data=json.loads(data_str) 
        elif request.args['config']=='initial':
            data=utilities.get_json_from_redis(stack_name) # returns dict
           
        if 'field' in request.args:
            filtered_response=utilities.filter_json(data,request.args['field'])
            return json.dumps(filtered_response) 
        else:                  
            return json.dumps(data) 
    
    if request.method == 'POST':
        data=request.data
        json_body = commentjson.loads(data)
        _slice=controller.find_slice_object(slice_name)
        message=_slice.add_stacks(json_body)
        return json.dumps(message) 
    
@flaskApp.route('/jox/slice/stack/machines', methods=['GET', 'POST', 'DELETE'])
def stack_machine_method():

    slice_name=request.args["slice"]
    stack_name=request.args["stack"]
    
    if request.method == 'GET':
        listA=controller.find_stack_object(slice_name,stack_name).get_kvm_machines_status()
        listB=controller.find_stack_object(slice_name,stack_name).get_lxc_machines_status()
        response=listA+listB
        return json.dumps(response)
    
    if request.method == 'POST':
        json_body = commentjson.loads(request.data)
        machines_config=json_body["machines-list"]
        stack=controller.find_stack_object(slice_name,stack_name)
        stack.add_machines(machines_config)

        return json.dumps("done")
        
    if request.method == 'DELETE':
        data=request.data
        json_body = commentjson.loads(data)
    #    status=cloud.delete_machines(json_body)
        return json.dumps("done")  

@flaskApp.route('/jox/slice/stack/services', methods=['GET', 'POST', 'DELETE'])
def stack_service_method():
    slice_name=request.args["slice"]
    stack_name=request.args["stack"]
    
    my_slice=controller.find_slice_object(slice_name)
    stack=my_slice.find_stack_object(stack_name)
    
    if request.method == 'GET':
        return 1
    if request.method == 'POST':    
        json_body = commentjson.loads(request.data)
        stack.add_service(json_body)
        return 1
        
        
        
def validate_sender(args):
    # Check if in user list
    users_json=utilities.get_json_from_redis("users")

    # check if key ok
    
    # check if slice-id exists

    return 1
    