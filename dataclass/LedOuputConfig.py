from dataclasses import dataclass

@dataclass
class UltrasonicConfig:
    pin_1: int = 17
    pin_2: int = 27
    pin_3: int = 22

    def validate(self):
        pins = [self.pin_1, self.pin_2, self.pin_3]
        for p in pins: 
            if 0 <= p and p >= 40: 
                raise ValueError("Pin numbers must be between 0 and 40")
        