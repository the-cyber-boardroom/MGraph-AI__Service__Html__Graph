from enum import Enum

class Enum__Service_Status(str, Enum):
    operational = 'operational'
    degraded    = 'degraded'