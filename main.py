#!/usr/bin/env python3
from sensors.fake_camera import FakeCamera

if __name__ == "__main__":
    fake_camera = FakeCamera()
    sensors = [fake_camera]
    current_data = []

    for sensor in sensors:
        current_data.append(sensor.capture_data())
    print(current_data)
