# ################################################################################
# #
# # Copyright (c) 2016, EURECOM (www.eurecom.fr)
# # All rights reserved.
# #
# # Redistribution and use in source and binary forms, with or without
# # modification, are permitted provided that the following conditions are met:
# #
# # 1. Redistributions of source code must retain the above copyright notice, this
# #    list of conditions and the following disclaimer.
# # 2. Redistributions in binary form must reproduce the above copyright notice,
# #    this list of conditions and the following disclaimer in the documentation
# #    and/or other materials provided with the distribution.
# #
# # THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
# # ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# # WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# # DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE LIABLE FOR
# # ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
# # (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# # LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
# # ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# # (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
# # SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
# #
# # The views and conclusions contained in the software and documentation are those
# # of the authors and should not be interpreted as representing official policies,
# # either expressed or implied, of the FreeBSD Project.
# #
# ################################################################################
# # file jorch.py
# # brief orchestrate juju charms
# # author  navid.nikaein@eurecom.fr
# 
# """
# Generic Juju Orchestrator
# -----------
# 
# A simple synchronous python orchestrator based on the python-based jujuclient that connects to the juju-core through the websocket api.
# 
# Supports python 2.7 & 3.4+.
# 
# See README for example usage.
# .. moduleauthor:: navid.nikaein@eurecom.fr
# """
# 
# import json
# import puka
# import time
# import uuid
# import logging
# 
# 
# import time
# from watchdog.observers import Observer
# 
# import pprint
# from types import *
# from jujuclient import Environment
# 
# """
# Minimum and maximum number of allowed service unit during the scaling
# """
# MIN_UNIT = 1
# MAX_UNIT = 2
# 
# """
# Service descriptor defining the service paramters, which might be overloaded during the init_service
# """
# 
# service_descriptor = [{'service': 'juju-gui','series': 'trusty', 'charm': 'cs:trusty/juju-gui-130',              'num_units': 1, 'max_unit': 2, 'constraints': {'cpu-cores': 1, 'mem': 1}, 'machine_spec': 'kvm:0', 'parent_id': '','container_type': 'kvm'},
#                       {'service': 'mysql',   'series': 'trusty', 'charm': 'cs:trusty/mysql-55',                  'num_units': 1, 'max_unit': 2, 'constraints': {'cpu-cores': 1, 'mem': 1}, 'machine_spec': 'kvm:0', 'parent_id': '','container_type': 'lxc'},
#                       {'service': 'oai-hss', 'series': 'trusty', 'charm': 'cs:~navid-nikaein/trusty/oai-hss-13', 'num_units': 1, 'max_unit': 2, 'constraints': {'cpu-cores': 1, 'mem': 1}, 'machine_spec': 'kvm:0', 'parent_id': '','container_type': 'kvm'},
#                       {'service': 'oai-epc', 'series': 'trusty', 'charm': 'cs:~navid-nikaein/trusty/oai-epc-25', 'num_units': 1, 'max_unit': 2, 'constraints': {'cpu-cores': 1, 'mem': 1}, 'machine_spec': 'kvm:0', 'parent_id': '','container_type': 'kvm'},
#                       {'service': 'oai-enb', 'series': 'trusty', 'charm': 'cs:~navid-nikaein/trusty/oai-enb-18', 'num_units': 1, 'max_unit': 2, 'constraints': {'cpu-cores': 4, 'mem': 8}, 'machine_spec': '1', 'parent_id': '','container_type': ''},
#                       {'service': 'oai-rrh', 'series': 'trusty', 'charm': 'cs:~navid-nikaein/trusty/oai-rrh-10',  'num_units': 1, 'max_unit': 2, 'constraints': {'cpu-cores': 4, 'mem': 8}, 'machine_spec': '2', 'parent_id': '','container_type': ''}]
# 
# 
# """
# Service specific configuration parameters
# """
# service_config = [{},{}]
# 
# """
# Service relationship
# """
# service_relation = [{'service_p': 'mysql',   'service_r': 'oai-hss'},
#                     {'service_p': 'oai-hss', 'service_r': 'oai-epc'},
#                     {'service_p': 'oai-epc', 'service_r': 'oai-enb'},
#                     {'service_p': 'oai-rrh', 'service_r': 'oai-enb'}]
# 
# """
# machine specification in terms of num cpu-cpres, memory, rootfs, architecture
# """
# machine_spec = [{},{}]
# 
# log_color = [{'level':' error',  'color': '\033[91m'}, # debug level 0
#              {'level': 'warn' ,  'color': '\033[93m'},  # debug level 1
#              {'level': 'notice', 'color': '\033[92m'},  # debug level 2
#              {'level': 'info',   'color': '\033[0m'},   # debug level 3
#              {'level': 'debug',  'color': '\033[0m'}]   # debug level 4
# 
# 
# 
# class JujuAgent(object):
#     """A juju agent in charge of service orchestration. It has two mode: standalone or slave
#        standalone: with full control on the lifecycle management
#        slave: under the control of a higher level orchestration receiving the lifecycle commands and sending back the results
#     """
# 
#     def __init__(self, jenv='manual', message_bus='local',test_mode=True, log_level='debug'):
#         super(JujuAgent, self).__init__()
#         if message_bus == 'hurtle':
#                 self.msgbus = 'amqp://goqtukir:2O2ATnF0kiCsFdYafrLUpjCkKeFdE0ee@spotted-monkey.rmq.cloudamqp.com/goqtukir'
#         else:
#             self.msgbus = None
#         self.attempts = 10
#         self.sleepy = 0
#         self.msgbus_client = None
#         self.connected = False
#         # XXX only supports one stack at one time!!!!
#         self.stack_id = ''
#         self.stack_state = ''
#         self.state = 0   # 0 : init, 1 : deploy, and 2 : chain
#         self.env_name = jenv
#         self.env = None
#         self.env_uuid = 0
#         self.watcher = None
#         self.charm = None
#         self.log_level = log_level
#         self.log = None
#         self.console = None
#         if test_mode == True:
#             self.services = ['mysql','oai-hss','oai-epc']
#         else:
#             self.services = ['juju-gui', 'mysql', 'oai-hss', 'oai-epc', 'oai-enb', 'oai-rrh']
# 
#     def init_logger(self):
#         """initializing the pythong logger """
#         logging.basicConfig(level=logging.DEBUG,
#                             format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s',
#                             datefmt='%m-%d %H:%M',
#                             filename='/tmp/jujuagent.log',
#                             filemode='w')
# 
#         # define a Handler which writes INFO messages or higher to the sys.stderr
#         self.console = logging.StreamHandler()
#         formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
#         self.console.setFormatter(formatter)
#         # add the handler to the root logger
# 
#         logging.getLogger('').addHandler(self.console)
#         self.log = logging.getLogger('jujuagent')
# 
#         if self.log_level == 'debug':
#             self.console.setLevel(logging.DEBUG)
#             self.log.setLevel(logging.DEBUG)
#         elif self.log_level == 'info':
#             self.console.setLevel(logging.INFO)
#             self.log.setLevel(logging.INFO)
#         elif self.log_level == 'warn':
#             self.console.setLevel(logging.WARNING)
#             self.log.setLevel(logging.WARNING)
#         elif self.log_level == 'error':
#             self.console.setLevel(logging.ERROR)
#             self.log.setLevel(logging.ERROR)
#         elif self.log_level == 'critic':
#             self.console.setLevel(logging.CRITICAL)
#             self.log.setLevel(logging.CRITICAL)
#         else:
#             self.console.setLevel(logging.INFO)
#             self.log.setLevel(logging.INFO)
# 
#     def init_service(self,template=None):
#         """
#         setting the service descriptor, service relation, and machines
#         """
# 
#     def find_index(self, dicts, key, value):
#         for i, d in enumerate(dicts):
#             if d.get(key, None) == value:
#                 return i
#         else:
#             return None
#             #raise ValueError('no dict with the key and value combination found')
# 
#     def logger(self, message, level='info'):
#         index = self.find_index(log_color, 'level', level)
#         if self.debug < index:
#             return
#         ts = time.strftime('%d %b %Y %H:%M')
#         message = ts + ' [' + level + '] ' + message
#         print log_color[index]['color']+ message
# 
#     def setup_jenv(self,constraints=None):
#         self.log.info('creating juju env: ' + str(self.env_name))
# 
#         if constraints is not None:
#             self.log.info('Constraints: ' + str(constraints))
#         # assumpton is that the juju is already bootstrapped and machines are addded to the juju env
#         self.env = Environment.connect(self.env_name)
#         self.watcher = self.env.get_watch(timeout=3)
#         #self.env_tag=self.env.uuid()
#         if constraints is not None:
#             self.env.set_env_constraints(constraints) #{'cpu-cores': 4, 'mem': 12}
# 
#     def close_jenv(self):
#         self.log.info('closing juju env: ' + str(self.env_name))
#         self.env.close()
# 
#     def env_info(self):
#         print json.dumps(self.env.info(), indent=2)  # same as before but beautiful
#         print json.dumps(self.env.get_env_config(), indent=2)  # same as before but beautiful
#         print json.dumps(self.env.get_env_constraints(), indent=2)  # same as before but beautiful
# 
#     def env_status(self, service='all'):
#         if service == 'all':
#             #print json.dumps(status, indent=2)  # same as before but beautiful
#             pprint.pprint(self.env.status())
#         elif service in self.services:
#             pprint.pprint(self.env.status()['Services'][service])
# 
#     def env_watcher(self):
#         for change_set in self.watcher:
#             self.log.debug(pprint.pprint(change_set))
#         #return self.watcher
# 
#     #add local charm to the env
#     # TODO : make a list of charm dir
#     def env_charm_dir(self,charm_dir='~/charmstore',charm_name='',series='trusty'):
#         self.charm = self.env.add_local_charm_dir(charm_dir+'/'+series+'/'+charm_name,series)
# 
#     def service_unit(self, service=None):
#         if service is None:
#             self.log.warn('No Service is defined')
#             return None
#         else:
#             return self.env.status()['Services'][service]['Units'].keys()[0]
# 
#     def service_status(self, service=None):
#         if service is None:
#             self.log.warn('No Service is defined')
#             return None
#         else:
#              return self.env.status()['Services'][service]['Status'].values()[0]
# 
#     def agent_status(self, service=None):
#         if service is None:
#             self.log.warn('No Service is defined')
#             return None
#         else:
#             return self.env.status()['Services'][service]['Units'][self.service_unit(service)].values()[6]
# 
#     # TODO: to be updated
#     def setup_machine(self, param=None):
#         if param is None:
#             self.log.warn('Failed to add machine: no params is defined')
#         else:
#             self.env.add_machine(series=param['series'], constraints=param['constraints'],
#                              machine_spec=param['machine_spec'], parent_id=param['parent_id'],
#                              container_type=param['container_type'])
# 
#             self.log.info('Machine added with parameters: ' + param)
# 
# 
#     def setup_channels(self):
#         self.log.info('connecting to message bus at: ' + self.msgbus)
#         self.msgbus_client = puka.Client(self.msgbus)
# 
#         while not self.connected and self.attempts > 0:
#             try:
#                 self.msgbus_client.wait(self.msgbus_client.connect())
#                 self.connected = True
#             except:
#                 self.log.warn('cannot connect - attempting to reconnect in ' + str(self.sleepy) + ' seconds...')
#                 self.attempts -= 1
#                 time.sleep(self.sleepy)
# 
#         if not self.connected:
#             self.log.warn('could not connect, exiting.')
#             # XXX shouldn't do this
#             exit()
# 
#         self.log.debug('setting up message bus channels...')
#         # comms channel to listen for SO commands
#         self.msgbus_client.wait(self.msgbus_client.exchange_declare(exchange='hurtle', type='topic', durable=True))
#         self.msgbus_client.wait(self.msgbus_client.queue_declare('hurtle-orch-events', durable=True))
#         self.msgbus_client.wait(self.msgbus_client.queue_bind(queue='hurtle-orch-events', exchange='hurtle',
#                                                               routing_key='events'))
# 
#         # comms channel to issue responses to SO
#         self.msgbus_client.wait(self.msgbus_client.exchange_declare(exchange='hurtle', type='topic', durable=True))
#         self.msgbus_client.wait(self.msgbus_client.queue_declare('hurtle-orch-events-resp', durable=True))
#         self.msgbus_client.wait(self.msgbus_client.queue_bind(queue='hurtle-orch-events-resp', exchange='hurtle',
#                                                               routing_key='events-resp'))
# 
#     def listen(self):
#         self.log.info("listening for SO commands on message bus")
#         receive_promise = self.msgbus_client.basic_consume(queue='hurtle-orch-events', no_ack=True)
# 
#         while True:
#             received_message = self.msgbus_client.wait(receive_promise)
#             message = json.loads(received_message['body'])
#             self.log.debug("Received: %r" % (message,))
#             if message['phase'] == 'deploy':
#                 self.deploy()
#             elif message['phase'] == 'configure':
#                 self.configure()
#             elif message['phase'] == 'chain':
#                 self.chain()
#             elif message['phase'] == 'provision':
#                 self.provision()
#             elif message['phase'] == 'detail':
#                 self.details()
#             elif message['phase'] == 'dispose':
#                 # Issue a destroy/delete command to Juju with supplied ID
#                 self.dispose()
#             elif message['phase'] == 'upgrade':
#                 self.upgrade()
#             else:
#                 self.log.warn("unknown phase %r " % message['phase'])
# 
#     def resolver(self,service='all',retry=False):
# 
#         self.log.info('Trying to resolve failures for the stack ' + str(self.stack_id))
# 
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
# 
# 
#     def deploy(self,service='all'):
#         self.log.debug('Deploying the stack ' + str(self.stack_id))
# 
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
# 
#     # does not change the state
#     def configure(self,service='all'):
#         self.log.info('Configuring the stack ' + str(self.stack_id))
# 
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
# 
#     def chain(self,service='all'):
#         self.log.debug('Chaining the stack: ' + str(self.stack_id))
# 
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
# 
#     def provision(self, service='all', scale='in', constraints={'cpu-cores': 2, 'mem': 8}):
#         """provision the service given the scale, and constraint.
#         scale = { 'in', 'out','up', 'down'} : in/out: add/remove resources, up/down: add/remove unit
#         """
#         self.log.debug('Provision the stack ' + str(self.stack_id))
# 
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
# 
#     def details(self,service='all'):
#         self.log.debug('Monitor the stack ' + str(self.stack_id))
# 
#         detail_state = 0
#         self.stack_state = 'CREATING'
#         if service == 'all':
#             services = self.services
#         else:
#             services = service
# 
#         # TODO need to send back a message containing details of the juju provisioned stack
#         # TODO need to send this back as a data structure - dict will do
# 
#         # stackname = self.stack_id
#         # juju.descibe(stackname)
# 
#         if self.state > 0:
# 
#             # TODO code to query the progress state of the juju stack
#             # XXX use:
#             # XXX      CREATE_COMPLETE - for the completion of the juju stack
#             # XXX      CREATE_FAILED - if the juju stack creation failed
#             # XXX
#             # XXX Any other value will be IGNORED
#             service_status={}
#             extra = {'APN': 'oai.ipv4'}
#             for instance in services:
# 
#                 status = self.service_status(service=instance)
#                 extra.update({instance: status})
# 
#                 unit_name=str(self.service_unit(instance))
#                 agent_status=str(self.agent_status(instance))
#                 # need to be refined
#                 if agent_status != 'error' : #and agent_status != 'None':
#                     try:
#                         ip = self.env.get_public_address(self.service_unit(service=instance))
#                     except:
#                         ip=None
#                 else:
#                     ip = None
#                 extra.update({instance: ip})
#                 service_status.update({instance: status})
#                 if status == 'error':
#                     #print instance + ' is in ' + status + ' state, trying to resolve ...'
#                     #self.env.resolved(self.service_unit(service=instance), retry=False)
#                     self.log.info('unit ' + unit_name + ': ' + status + ' with agent: ' + agent_status)
#                 elif status == 'unknown' or status == 'active':
#                     detail_state += 1
# 
#             # this does not work if we perform other lifecycle phases
#             if detail_state == len(services):
#                 self.stack_state = 'CREATE_COMPLETE'
#                 self.log.info('Stack state is : ' + self.stack_state)
# 
#             extra.update({'state': detail_state})
# 
#             self.log.info(json.dumps(extra, indent=2))
#             # need to return JSON that describes things understood by the SO
#             if self.msgbus:
#                 message = {
#                     'phase': 'detail',
#                     'stack_id': str(self.stack_id),
#                     'state': self.stack_state,
#                     'parameters': extra
#                 }
#                 # respond to the SO with the ID of what juju creates
#                 self.log.debug('responding back to the SO with: ' + str(message))
#                 self.msgbus_client.wait(self.msgbus_client.basic_publish(exchange='hurtle',
#                                                                          routing_key='events-resp',
#                                                                          body=json.dumps(message)))
#             return service_status
# 
#     def upgrade(self, service='all'):
#         self.log.debug('Upgrade the stack ' + str(self.stack_id))
# 
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
# 
#     def dispose(self, service='all', unchain=True):
#         self.log.debug('Dispose the stack ' + str(self.stack_id))
# 
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
# 
# class JujuAPI(object):
#     """Abstract out the details of juju api.
#     """
# 
# # very very basic - naive - test
# if __name__ == '__main__':
#     ja = JujuAgent()
#     ja.init_logger()
#     ja.setup_jenv()
#     ja.env_info()
#     if ja.msgbus:
#         ja.setup_channels()
#         ja.listen()
#     else:
#         # orchestrator logic when deployed in standalone mode
#         #ja.deploy(service={'mysql'})
#         ja.deploy()
#         ja.configure()
#         ja.provision()
#         ja.chain()
#         event_handler = ja.env_watcher()
#         observer = Observer()
#         observer.schedule(event_handler, path='.', recursive=False)
#         observer.start()
#         try:
#             while True:
#                 time.sleep(10)
#                 service_status= ja.details()
#                 ja.log.debug(service_status)
#                 # take actions: like resolve
#                 #ja.env_status()
#         except KeyboardInterrupt:
#             observer.stop()
#             ja.dispose(unchain=False)
#             ja.close_jenv()
#         observer.join()