#!/usr/bin/env python3
from abc import ABC, abstractmethod


class Data(ABC):
    @abstractmethod
    def get_raw(self):
        pass

    @abstractmethod
    def serialise(self) -> bytes:
        pass

    @abstractmethod
    def deserialise(self, b: bytes):
        pass


class Sensor(ABC):
    @abstractmethod
    def capture_data(self):
        pass
