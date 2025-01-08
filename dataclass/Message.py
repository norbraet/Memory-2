from dataclasses import dataclass, field
from typing import Any, Dict, Optional
import time

@dataclass
class Message:
    service: str
    data: any
    timestamp: float = field(default_factory=lambda: time.time())
    metadata: Optional[Dict[str, Any]] = None

    def validate(self):
        """
        Validate the message. Raise an exception if the message is invalid.
        """
        if not self.service or not isinstance(self.service, str):
            raise ValueError("Service name must be a non-empty string")
        if self.metadata and not isinstance(self.metadata, dict):
            raise ValueError("Metadata must be a dictonary")