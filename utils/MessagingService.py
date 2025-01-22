from queue import Queue, Empty, Full
from dataclass.Message import Message

class MessagingService:
    def __init__(self):
        """
        Initialize the MessagingService with separate incoming and outgoing queues.
        """
        self.outgoing_queue = Queue()
        self.incoming_queue = Queue()
        self.internal_queue = Queue()

    def send_message(self, service_name, data, metadata = None, queue: Queue = None, block = True, timeout = None):
        """
        Send a message to the specified queue.
        """
        target_queue = queue or self.outgoing_queue
        if target_queue:
            message = Message(service = service_name, data = data, metadata = metadata)
            try:
                if block:
                    target_queue.put(message, timeout = timeout)
                else:
                    target_queue.put_nowait(message)
            except Full:
                print(f"Que is full. Message {message} was not sent")

    def receive_message(self, queue: Queue = None, block = True, timeout = 1):
        """
        Receive a message from the specified queue, if available.
        """
        source_queue = queue or self.incoming_queue
        if source_queue:
            message = source_queue.get(timeout = timeout) if block else source_queue.get_nowait()
            if not isinstance(message, Message):
                raise ValueError("Received an invalid message type")
            return message
            