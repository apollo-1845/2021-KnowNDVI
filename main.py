#!/usr/bin/env python3
from sensors.fake_camera import FakeCamera
from sensors.camera import CameraData

if __name__ == "__main__":
    fake_camera = FakeCamera()
    sensors = [fake_camera]
    current_data = []

    for sensor in sensors:
        current_data.append(sensor.capture_data())

    serialised_data_pieces = [d.serialise() for d in current_data]
    deserialised_data_pieces = [
        CameraData.deserialise(d) for d in serialised_data_pieces
    ]
    # print(type(current_data[0]))
    # print("-------------------")
    # print(type(deserialised_data_pieces[0]))
    # print((deserialised_data_pieces[0].image == current_data[0].image).all())
