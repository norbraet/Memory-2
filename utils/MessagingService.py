from queue import Empty
from dataclass.Message import Message

class MessagingService:
    def __init__(self, message_queue=None):
        self.message_queue = message_queue

    def send_message(self, service_name, data, metadata=None):
        """
        Send a message to the main application or other services via the queue.
        """
        if self.message_queue:
            message = Message(service=service_name, data=data, metadata=metadata)
            self.message_queue.put(message)

    def receive_message(self, timeout=1):
        """
        Receive a message from the queue, if available.
        """
        try:
            return self.message_queue.get(timeout=timeout)
        except Empty:
            return None