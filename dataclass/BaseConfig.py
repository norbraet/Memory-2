from dataclasses import dataclass

@dataclass
class BaseConfig:
    level_steps: int = 0.5
    level_steps_max: int = 2
    level_steps_min: float = 0.1
    level_steps_interval: float = 0.1
    restoration_duration: int = 2
    restoration_duration_max: int = 5
    restoration_duration_min: float = 0.1
    restoration_duration_interval: float = 0.1