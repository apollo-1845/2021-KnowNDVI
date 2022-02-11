#!/usr/bin/env python3
from time import time

from abc import ABC, abstractmethod
from project_types import Data, Sensor

import numpy as np

class TimeStampData(Data):
    data = None

    def __init__(self, _data):
        self.data = _data

    def get_raw(self):
        return self.data

    def serialise(self) -> bytes:
        return self.data.tobytes()

    @staticmethod
    def deserialise(b):
        return TimeStampData(np.frombuffer(b, dtype=np.uint64))

    def __repr__(self):
        return f"Timestamp data: {self.data}"

class VirtualTimeStampSensor(Sensor):
    def capture_data(self):
        return TimeStampData(np.uint64(time()))
