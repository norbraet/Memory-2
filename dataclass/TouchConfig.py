from dataclasses import dataclass
from dataclass.BaseConfig import BaseConfig

@dataclass
class TouchConfig(BaseConfig):
    level_steps: int = 100
    level_steps_max: int = 100
    level_steps_min: int = 100
    level_steps_interval = 0
    restoration_duration: int = 24
    restoration_duration_max: int = 30
    restoration_duration_min: int = 20
    restoration_duration_interval: int = 2