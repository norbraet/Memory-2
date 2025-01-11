from dataclasses import dataclass, field
from typing import Tuple

@dataclass
class LedData:
    red: int = 1
    green: int = 0
    blue: int = 0
