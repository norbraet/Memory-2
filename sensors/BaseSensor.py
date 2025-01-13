from abc import ABC, abstractmethod
from utils.MessagingService import MessagingService
from utils.ThreadedService import ThreadedService

class BaseSensor(ThreadedService, MessagingService):
    def __init__(self, service_name, message_queue = None, config = None, debug = False):
        ThreadedService.__init__(self, service_name, debug)
        MessagingService.__init__(self, message_queue)
        self.config = config or {}

    @abstractmethod
    def setup(self):
        pass

    @abstractmethod
    def loop(self):
        pass

    @abstractmethod
    def cleanup(self):
        pass