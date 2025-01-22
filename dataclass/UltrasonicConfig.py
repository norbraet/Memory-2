from dataclasses import dataclass
from dataclass.BaseConfig import BaseConfig

@dataclass
class UltrasonicConfig(BaseConfig):
    echo_pin: int = 24
    trigger_pin: int = 23
    max_distance: float = 5.0
    threshold: int = 100
    loop_refresh_rate: float = 0.1
