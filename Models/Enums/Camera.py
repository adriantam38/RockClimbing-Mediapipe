from enum import Enum

class CAMERA_STATE(Enum):
    NORMAL = 0
    PAUSE = 1
    RECORDING = 2
    UNAVAILABLE = 3
    
class CAMERA_ORIENTATION(Enum):
    LANDSCAPE = 0
    LEFT = 1
    RIGHT = 2
    INVERTED = 3