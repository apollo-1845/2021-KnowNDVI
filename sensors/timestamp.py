#!/usr/bin/env python3
from time import time

from project_types import Data, Sensor

import numpy as np


class TimeStampData(Data):
    """A Data subclass that represents a timestamp."""

    data = None

    def is_invalid(self):
        """See if the data should not be recorded."""
        return self.data is None

    def __init__(self, _data):
        """Create a new instance."""
        self.data = _data

    def get_raw(self):
        """Get the raw data value stored in this wrapper."""
        return self.data

    def serialise(self) -> bytes:
        """Return bytes that can be stored to represent the value."""
        return self.data.tobytes()

    @staticmethod
    def deserialise(b):
        """Reverse the serialisation process."""
        return TimeStampData(np.frombuffer(b, dtype=np.uint64))

    def __repr__(self):
        return f"Timestamp data: {self.data}"


class TimeStampVirtualSensor(Sensor):
    """A virtual "sensor" that provides the current timestamp."""

    def capture_data(self):
        """Return a TimeStampData representing the current timestamp."""
        return TimeStampData(np.uint64(time()))
