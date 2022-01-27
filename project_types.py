#!/usr/bin/env python3
import numpy as np
from abc import ABC, abstractmethod


class Data(ABC):
    @abstractmethod
    def get_raw(self):
        pass

    @abstractmethod
    def serialise(self) -> bytes:
        """returns a resource locator if it is saved in a separate file
        otherwise returns the value as a byte stream"""
        pass

    @staticmethod
    @abstractmethod
    def deserialise(b: bytes):
        """Returns the value represented by the bytes"""
        pass


class Sensor(ABC):
    @abstractmethod
    def capture_data(self):
        pass

def get_len_bytes(data):
    return np.uint32(len(data)).tobytes()
