from dataclasses import dataclass
from dataclass.BaseConfig import BaseConfig
from enums.StageEnum import Stage

@dataclass
class TouchConfig(BaseConfig):
    level_steps: int = 100
    level_steps_max: int = 100
    level_steps_min: int = 100
    level_steps_interval = 0
    restoration_duration: int = 1
    restoration_duration_max: int = 1
    restoration_duration_min: int = 1
    restoration_duration_interval: int = 1
    stage: Stage = Stage.BLACK_WHITE
    sleep: bool = False