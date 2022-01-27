#!/usr/bin/env python3
import numpy as np
from sensors.fake_camera import FakeCamera
from sensors.camera import CameraData

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
    sensors = [fake_camera]
    current_data = []

    # data collection loop

    # record the data
    for sensor in sensors:
        current_data.append(sensor.capture_data())

    serialised_data_pieces = [d.serialise() for d in current_data]
    # deserialised_data_pieces = [
    #     CameraData.deserialise(d) for d in serialised_data_pieces
    # ]
    test_camera_data_serialisation(current_data[0], serialised_data_pieces[0])

    # record the data into a file
    # TODO: maybe there is a more effecient way
    with open(file_dir, "ab") as out_file:
        # indicate the data "length" for each data piece
        out_data = bytes()

        for data_piece in serialised_data_pieces:
            length = np.uint32(len(data_piece))
            out_data += length.tobytes()
            out_data += data_piece

        out_file.write(out_data)
