from enum import Enum, auto

class Stage(Enum):
    START = auto()
    BLACK_WHITE = auto()
    BLURRY = auto()
    LIGHTNESS = auto()
    END = auto()
