from dataclasses import dataclass

@dataclass
class BaseConfig:
    level_steps: int = 2
    restoration_duration: int = 5