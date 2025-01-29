from dataclasses import dataclass
from dataclass.BaseConfig import BaseConfig

"""Vibration Motor PIN Setup

VCC Pin -> any free 5V Power Pin -> e.g. Pin 4
GND Pin -> any free Ground Pin -> e.g. Pin 20
IN Pin -> any free GPIO Pin -> e.g. Pin 22 (GPIO 25)
"""

@dataclass
class VibrationMotorConfig(BaseConfig):
    in_pin: int = 25
    vibration_time: int = 2
    restoration_duration: int = 1