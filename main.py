#!/usr/bin/env python3
from sensors.fake_camera import FakeCamera
from sensors.camera import CameraData
from sensors.timestamp import VirtualTimeStampSensor

import numpy as np

from project_types import get_len_bytes

file_dir = "./out/out.blob"

def test_camera_data_serialisation(original, serialised):
    """Given unserialised and serialised camera data, checks that deserialisation reverses serialisation."""
    result_image = CameraData.deserialise(serialised).image
    if not(original.image == result_image).all():
        raise Exception(f"Unexpected camera data deserialisation result: {result_image}, expected {original.image}")


if __name__ == "__main__":
    # double-check the file - it should be empty
    try:
        # would raise an error if the file does not exist
        with open(file_dir, "r") as f:
            try:
                # if the file is not empty, would throw
                f.read(1)
            except:
                print("Warning: the out file is not empty; appending to it...")
    except:
        pass
    # setup
    fake_camera = FakeCamera()
    virtual_time_stamp_sensor = VirtualTimeStampSensor()
    # NOTE: the order matters
    sensors = [virtual_time_stamp_sensor, fake_camera]
    current_data = []

    # data collection loop

    # record the data
    for sensor in sensors:
        current_data.append(sensor.capture_data())

    serialised_data_pieces = [d.serialise() for d in current_data]
    # deserialised_data_pieces = [
    #     CameraData.deserialise(d) for d in serialised_data_pieces
    # ]
    test_camera_data_serialisation(current_data[1], serialised_data_pieces[1])

    # record the data into a file
    # TODO: maybe there is a more effecient way
    with open(file_dir, "ab") as out_file:
        # indicate the data "length" for each data piece
        out_data = bytes()

        for i, data_piece in enumerate(serialised_data_pieces):
            out_data += np.uint8(i).tobytes()
            out_data += get_len_bytes(data_piece)

            out_data += data_piece

        out_file.write(out_data)
