from dataclasses import dataclass, field
from typing import Tuple

@dataclass
class FaceRecognitionConfig:
    scale_factor: float = 1.2
    downscale_factor: float = 0.5
    min_neighbors: int = 8 
    min_size: Tuple[int, int] = field(default_factory=lambda: (50, 50))
    level_steps: int = 80
    restoration_duration: int = 10
