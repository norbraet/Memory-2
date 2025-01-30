from dataclasses import dataclass

@dataclass
class BaseConfig:
    level_steps: int = 0.5
    level_steps_max: int = 2
    level_steps_min: int = 0.1
    level_steps_interval = 0.1
    restoration_duration: int = 2
    restoration_duration_max: int = 5
    restoration_duration_min: int = 0.1
    restoration_duration_interval: int = 0.1