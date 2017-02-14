################################################################################
#
# Copyright (c) 2016, EURECOM (www.eurecom.fr)
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
# 1. Redistributions of source code must retain the above copyright notice, this
#    list of conditions and the following disclaimer.
# 2. Redistributions in binary form must reproduce the above copyright notice,
#    this list of conditions and the following disclaimer in the documentation
#    and/or other materials provided with the distribution.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
# ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE LIABLE FOR
# ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
# (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
# ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
# SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
#
# The views and conclusions contained in the software and documentation are those
# of the authors and should not be interpreted as representing official policies,
# either expressed or implied, of the FreeBSD Project.
#
################################################################################
from jstack import Stack
from types import DictType
from json import JSONEncoder



log = None
console = None
       
        
class JSlice(JSONEncoder):
    
    def __init__(self, slice_config,clouds,jox_config):

        self.clouds=clouds # A slice can span multiple clouds. A stack is deployed over a single cloud
        self.stacks=[] #List with stack objects
        # LOGGING
        self.log_level = jox_config.get("log_level")
        self.log = None
        self.console = None
        # CONFIGURATION 
        if slice_config==None:
            print "Slice Configuration File is not provided"
                    
        if type(slice_config) is DictType:
            self.template_version=slice_config["jox-slice-template-version"]
            self.template_date=slice_config["jox-template-date"],
            self.juju_version=slice_config["juju-version"]  
            self.slice_name=slice_config["slice-name"]
            self.external_slice_name=slice_config["external-slice-name"]
            self.slice_owner=slice_config["slice-owner"]
            
            if (slice_config["stacks-list"]!=None):
                self.add_stacks(slice_config)            
     
        return 
    
            
    def add_stacks(self, config):
        for stack_config in config["stacks-list"]:
            if stack_config==None:
                self.log.warn('No Stack to add')
            else:
                self.add_stack(stack_config)
                return "Stack Added"
     
    def add_stack(self,stack_config):
            new_stack=Stack(stack_config,self.clouds, self.log_level) #item is a dict
            self.stacks.append(new_stack)     
            print 'Stack added with parameters: ' 
                 
    def check_slice_status(self):        
        print "checking JSlice Health"

    def find_stack_object(self,stack_name):
        stack_object=filter(lambda x: x.stack_name == stack_name,self.stacks)[0]
        return stack_object

