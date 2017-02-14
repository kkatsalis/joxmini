import logging
import puka
import time
import json

class Hurtle(object):
    def __init__(self, message_bus='local', log_level='debug'):
        
        """Hurtle Communication Interface"""
        
        self.log_level = log_level
        self.log = None
        
        if message_bus == 'hurtle':
                self.msgbus = 'amqp://goqtukir:2O2ATnF0kiCsFdYafrLUpjCkKeFdE0ee@spotted-monkey.rmq.cloudamqp.com/goqtukir'
        else:
            self.msgbus = None
  
    
    def setup_channels(self):
        self.log.info('connecting to message bus at: ' + self.msgbus)
        self.msgbus_client = puka.Client(self.msgbus)

        while not self.connected and self.attempts > 0:
            try:
                self.msgbus_client.wait(self.msgbus_client.connect())
                self.connected = True
            except:
                self.log.warn('cannot connect - attempting to reconnect in ' + str(self.sleepy) + ' seconds...')
                self.attempts -= 1
                time.sleep(self.sleepy)

        if not self.connected:
            self.log.warn('could not connect, exiting.')
            # XXX shouldn't do this
            exit()

        self.log.debug('setting up message bus channels...')
        # comms channel to listen for SO commands
        self.msgbus_client.wait(self.msgbus_client.exchange_declare(exchange='hurtle', type='topic', durable=True))
        self.msgbus_client.wait(self.msgbus_client.queue_declare('hurtle-orch-events', durable=True))
        self.msgbus_client.wait(self.msgbus_client.queue_bind(queue='hurtle-orch-events', exchange='hurtle',
                                                              routing_key='events'))

        # comms channel to issue responses to SO
        self.msgbus_client.wait(self.msgbus_client.exchange_declare(exchange='hurtle', type='topic', durable=True))
        self.msgbus_client.wait(self.msgbus_client.queue_declare('hurtle-orch-events-resp', durable=True))
        self.msgbus_client.wait(self.msgbus_client.queue_bind(queue='hurtle-orch-events-resp', exchange='hurtle',
                                                              routing_key='events-resp'))

    def listen(self):
        self.log.info("listening for SO commands on message bus")
        receive_promise = self.msgbus_client.basic_consume(queue='hurtle-orch-events', no_ack=True)

        while True:
            received_message = self.msgbus_client.wait(receive_promise)
            message = json.loads(received_message['body'])
            self.log.debug("Received: %r" % (message,))
            if message['phase'] == 'deploy':
                self.deploy()
            elif message['phase'] == 'configure':
                self.configure()
            elif message['phase'] == 'chain':
                self.chain()
            elif message['phase'] == 'provision':
                self.provision()
            elif message['phase'] == 'detail':
                self.details()
            elif message['phase'] == 'dispose':
                # Issue a destroy/delete command to Juju with supplied ID
                self.dispose()
            elif message['phase'] == 'upgrade':
                self.upgrade()
            else:
                self.log.warn("unknown phase %r " % message['phase'])
