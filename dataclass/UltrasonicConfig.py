from dataclasses import dataclass

@dataclass
class UltrasonicConfig:
    echo_pin: int = 24
    trigger_pin: int = 23
    max_distance: float = 5.0

    def validate(self):
        if not (0 <= self.echo_pin <= 40 and 0 <= self.trigger_pin <= 40):
            raise ValueError("Pin numbers must be between 0 and 40")
        if self.max_distance <= 0:
            raise ValueError("Max distance must be greater than 0")
