from dataclasses import dataclass, field
from typing import Tuple
from dataclass.BaseConfig import BaseConfig

@dataclass
class FaceRecognitionConfig(BaseConfig):
    scale_factor: float = 1.2
    downscale_factor: float = 0.5
    min_neighbors: int = 8 
    min_size: Tuple[int, int] = field(default_factory=lambda: (50, 50))
    level_steps: int = 80
    level_steps_max: int = 100
    level_steps_min: int = 10
    level_steps_interval = 10
    restoration_duration: int = 10
    restoration_duration_max: int = 30
    restoration_duration_min: int = 1
    restoration_duration_interval: int = 2
