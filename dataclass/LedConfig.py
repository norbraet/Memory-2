from dataclasses import dataclass
from dataclass.BaseConfig import BaseConfig

"""LED PIN Setup

GND Pin -> any free Ground Pin -> e.g. Pin 9
R Pin -> any free GPIO Pin -> e.g. Pin 15 (GPIO 22)
G Pin -> any free GPIO Pin -> e.g. Pin 13 (GPIO 27)
B Pin -> any free GPIO Pin -> e.g. Pin 11 (GPIO 17)
"""

@dataclass
class LedConfig(BaseConfig):
    r_pin: int = 22
    g_pin: int = 27
    b_pin: int = 17