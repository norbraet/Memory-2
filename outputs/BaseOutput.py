from abc import ABC, abstractmethod
from utils.MessagingService import MessagingService
from utils.ThreadedService import ThreadedService

class BaseOutput(ThreadedService, MessagingService, ABC):
    def __init__(self, service_name, outgoing_queue, incoming_queue, config = None, debug = False):
        ThreadedService.__init__(self, service_name, debug)
        MessagingService.__init__(self, outgoing_queue, incoming_queue)
        self.config = config or {}

    @abstractmethod
    def setup(self):
        pass

    @abstractmethod
    def trigger_action(self, data):
        pass

    @abstractmethod
    def cleanup(self):
        pass