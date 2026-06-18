from dataclasses import dataclass


@dataclass
class Params:
    f1: float = 220.0
    fs: int = 44100
    duration: float = 3.0
    L: float = 1.0
    pluck_pos: float = 0.2
    pickup_pos: float = 0.82
    amplitude: float = 0.5
    sigma0: float = 0.7
    sigma1: float = 8e-5
