# watchdog.observer: Python API and shell utilities to monitor file system events.
from Core.jcloud import Cloud
from Core.jslice import JSlice
from Util import utilities
import jsonpickle



class Controller(object):
    
    def __init__(self,jox_config):
        
        self.jox_config=jox_config
        self.slices=[]           # List with Slices
        self.clouds=[]    # List with JClouds
    
    
    def add_cloud(self,cloud_name):
        new_cloud=Cloud(cloud_name)
        self.clouds.append(new_cloud)
        print "Cloud added to JOX:",new_cloud 
    
    def find_cloud_object(self, cloud_name):
        cloud=filter(lambda x: x.cloud_name == cloud_name,self.clouds)[0] #find correct cloud object
        return cloud
    
    def find_slice_object(self,slice_name):
        my_slice=filter(lambda x: x.slice_name == slice_name,self.slices)[0] #find correct cloud object                 
        return my_slice
    
    def find_stack_object(self,slice_name,stack_name):
        jslice=self.find_slice_object(slice_name)
        stack=jslice.find_stack_object(stack_name)
        return stack
    
    def get_slice_data(self,slice_name):
        my_slice=self.find_slice_object(slice_name)
        data_str=jsonpickle.encode(my_slice)# returns str
        return data_str
     
    def get_stack_data(self,slice_name,stack_name): 
        jslice=self.find_slice_object(slice_name)
        stack=jslice.find_stack_object(stack_name)
        data_str=jsonpickle.encode(stack)# returns str
        return data_str
        
        
        
    def add_slice(self,slice_config):
        response=utilities.set_json_to_redis(slice_config["slice-name"],slice_config) 
        if(response=="KEY added"):
            new_slice=JSlice(slice_config,self.clouds,self.jox_config)
            self.slices.append(new_slice)
            return new_slice.slice_name
        else:
            print "Slice name already exists"
            return 0    
        
        
    def delete_slice(self,slice_id):
        print "toDO" 