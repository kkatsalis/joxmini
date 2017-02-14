################################################################################################
#   Configuration file for jorch v1.0
#   - Events Library:  https://github.com/nicolaiarocci/events: pip install events
#
# - Web-API: Python Flask : sudo pip install Flask
# - python pip: sudo apt install python-pip
# - commentjson : pip install commentjson
# - Serializer jsonpickle: sudo pip install jsonpickle
# - sudo apt-get install python-libvirt
#
#   REDIS key: jorch-config
################################################################################################

import sys
import logging
from types import *
import json
import commentjson
import time
from Util import utilities
from Core import jcontrol
from flask import Flask, request
from Com import webAPI
from Config import global_variables

import atexit

console=None
log=None

def main():
    atexit.register(goodbye)
    jox_config_data = ""
    
    # Load JOX Configuration    
    try:
        with open(global_variables.CONFIG_FILE) as data_file:    
            data=data_file.read()
            
            jox_config_data = commentjson.loads(data)
         
            global_variables.LOGFILE=jox_config_data["logfile"]
            global_variables.LOG_LEVEL=jox_config_data["log-level"]
            global_variables.DEFAULT_SLICE_CONFIG=jox_config_data["default-slice-config"]
            global_variables.QEMU_PATH=jox_config_data["qemu-path"]
            global_variables.KVM_USER=jox_config_data["kvm-user"]
            
            # REDIS Configuration
            global_variables.REDIS_SERVER=jox_config_data["redis-server"]
            global_variables.REDIS_PORT=jox_config_data["redis-port"]
            global_variables.JOX_CONFIG_KEY=jox_config_data["config-key"]
            
    except IOError as e:
        message = "Could not load JOX Configuration file.I/O error({0}): {1}".format(e.errno, e.strerror) 
        print message
        sys.exit("Could not load JOX Configuration file!")
    else:
        message = "JOX Configuration file Loaded"
        print message


    # Initiallize Loggers
    logfile=global_variables.LOGFILE
    logging.basicConfig(level=logging.DEBUG, format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s', 
                        datefmt='%m-%d %H:%M', filename=logfile, filemode='w')
    
    # Console Configuration
    console = logging.StreamHandler()
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    console.setFormatter(formatter)
    
    # add the handler to the root logger
    logging.getLogger('').addHandler(console)
    log = logging.getLogger(__name__)
# 
    if global_variables.LOG_LEVEL == 'debug':
        console.setLevel(logging.DEBUG)
        log.setLevel(logging.DEBUG)
    elif global_variables.LOG_LEVEL == 'info':
        console.setLevel(logging.INFO)
        log.setLevel(logging.INFO)
    elif global_variables.LOG_LEVEL == 'warn':
        console.setLevel(logging.WARNING)
        log.setLevel(logging.WARNING)
    elif global_variables.LOG_LEVEL == 'error':
        console.setLevel(logging.ERROR)
        log.setLevel(logging.ERROR)
    elif global_variables.LOG_LEVEL == 'critic':
        console.setLevel(logging.CRITICAL)
        log.setLevel(logging.CRITICAL)
    else:
        console.setLevel(logging.INFO)
        log.setLevel(logging.INFO)
    
    
    # Load jOX Configuration to REDIS
    try:
        utilities.del_json_from_redis(global_variables.JOX_CONFIG_KEY)
        utilities.set_json_to_redis(global_variables.JOX_CONFIG_KEY,jox_config_data)
    except IOError as e:
        message = "Could not load JOX Configuration file.I/O error({0}): {1}".format(e.errno, e.strerror) 
        print message
        logging.ERROR(message)
        sys.exit("Could not load JOX Configuration file!")
    else:
        message = "JOX Configuration file Loaded"
        print message
        logging.info(message)

    # Create JOX Controller
    try:
        controller=jcontrol.Controller(jox_config_data)       
    
        # Add JUJU Clouds to JOX Controller
        x=jox_config_data["clouds-list"]
        for item in x:
            name=item["juju-cloud"]
            controller.add_cloud(name)
    except Exception as e:
        message = "Could not load joX Controller!" 
        log.ERROR(message)
        sys.exit("Could not load jox Controller!")
    else:
        message = "JOX controller was successfully loaded"
        log.info(message)
    
    
        
    # Open Default Slice Configuration File and Create default slice 
    try:
        with open(global_variables.DEFAULT_SLICE_CONFIG) as slice_data_file:    
            slice_data=slice_data_file.read()
            slice_config = commentjson.loads(slice_data)
            controller.add_slice(slice_config)
         
    except IOError as e:
        message = "Could not load default slice configuration file.I/O error({0}): {1}".format(e.errno, e.strerror) 
        log.ERROR(message)
        sys.exit("Could not load default slice Configuration file!")
    else:
        message = "default slice Configuration file loaded"
        log.info(message)
       
    # Start WebAPI (Flask)
    try:
        webAPI.set_controller(controller)  
        webAPI.flaskApp.run(jox_config_data['flask-server'],jox_config_data['flask-port'],debug=False)
        print "JOX WebAPI loaded:" 
    except RuntimeError as e:
        logging.exception("message"+e ) # fix all logins
    except:
        logging.exception("Flask load error")
    




def goodbye():
    print "You are now leaving the Python sector."
        

if __name__ == "__main__":
    main()
    
    


  
    
