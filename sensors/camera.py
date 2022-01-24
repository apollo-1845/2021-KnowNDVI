from abc import ABC, abstractmethod
from project_types import Data, Sensor


class CameraData(Data):
    image = None

    def __init__(self, image):
        self.image = image

    def get_raw(self):
        return self.image

    def serialise(self) -> bytes:
        return self.image

    def deserialise(self, b: bytes):
        return None

    def __repr__(self):
        return f"{self.image}"


class Camera(Sensor):
    def capture_data(self):
        pass
    
