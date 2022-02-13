import time
from datetime import datetime, timedelta

import numpy as np

from project_types import get_len_bytes
from sensors.camera.base_camera import CameraData
from settings import OUT_FILE, IS_PROD, EXPERIMENT_DURATION_MINUTES, SECONDS_PER_ITERATION

# Import sensors
from sensors.timestamp import VirtualTimeStampSensor

if IS_PROD:
    from sensors.camera.camera import Camera
else:
    # Use testing camera
    from sensors.camera.fake_camera import FakeCamera as Camera


def test_camera_data_serialisation(original, serialised):
    """Given original and serialised camera data, checks that deserialisation reverses serialisation."""
    result_image = CameraData.deserialise(serialised).image
    if not (original.image == result_image).all() and not IS_PROD:
        raise Exception(f"Unexpected camera data deserialisation result: {result_image}, expected {original.image}")


def collect_data(sensors, out_file):
    """Record and save the inputs in the output file
    - we are purposefully not processing this too much to prevent bugs from destroying the data."""
    # data collection loop
    current_data = []

    # record the data
    for sensor in sensors:
        current_data.append(sensor.capture_data())

    # Don't have the data
    for d in current_data:
        if d.is_invalid():
            print("Warning: some data is invalid")
            return

    serialised_data_pieces = [d.serialise() for d in current_data]
    test_camera_data_serialisation(current_data[1], serialised_data_pieces[1])

    # record the data into a file
    # TODO: maybe there is a more efficient way
    # indicate the data "length" for each data piece
    out_data = bytes()

    for i, data_piece in enumerate(serialised_data_pieces):
        out_data += np.uint8(i).tobytes()
        out_data += get_len_bytes(data_piece)

        out_data += data_piece

    out_file.write(out_data)


# Outputting data into the ./out/ folder for analysis on Earth
if __name__ == "__main__":
    start_time = datetime.now()  # Store start to keep track of time since start
    end_time = start_time + timedelta(minutes=EXPERIMENT_DURATION_MINUTES-(SECONDS_PER_ITERATION/60))  # We want to stop slightly prematurely so that we don't overrun

    try:
        # would raise an error if the file does not exist
        with open(OUT_FILE, "r") as f:
            try:
                # if the file is not empty, would throw
                f.read(1)
            except:
                print("Warning: the out file is not empty; appending to it...")
    except:
        pass
    # Set up sensors
    camera = Camera()
    virtual_time_stamp_sensor = VirtualTimeStampSensor()
    # NOTE: the order matters
    sensors = [virtual_time_stamp_sensor, camera]

    now_time = datetime.now()
    while now_time < end_time: # Until would overrun
        # open the file in every iteration so that if there is an exception (e.g. we have run out of space), the contents are synced into the file
        with open(OUT_FILE, "ab") as out_file:
            # Main program
            collect_data(sensors, out_file)
            # Wait interval
            time.sleep(SECONDS_PER_ITERATION)
            # Get time now
            now_time = datetime.now()
