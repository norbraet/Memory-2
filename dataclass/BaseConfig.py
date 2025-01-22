from dataclasses import dataclass

@dataclass
class BaseConfig:
    level_steps: int = 2
    level_steps_max: int = 10
    level_steps_min: int = 1
    level_steps_interval = 1
    restoration_duration: int = 5
    restoration_duration_max: int = 30
    restoration_duration_min: int = 1
    restoration_duration_interval: int = 2