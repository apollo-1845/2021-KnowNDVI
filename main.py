from os.path import isfile, getsize
import time
from datetime import datetime, timedelta

import numpy as np

from sensors.camera.base_camera import CameraData
from settings import OUT_FILE, IS_PROD, EXPERIMENT_DURATION_MINUTES, SECONDS_PER_ITERATION

# Import sensors
from sensors.timestamp import TimeStampVirtualSensor
from sensors.camera.camera import Camera


def test_camera_data_serialisation(original, serialised):
    """
    Checks that deserialisation reverses serialisation.

    Only works in development!
    """
    if IS_PROD:
        return
    result_image = CameraData.deserialise(serialised).image
    if not (original.image == result_image).all():
        raise Exception(f"Unexpected camera data deserialisation result: {result_image}, expected {original.image}")


def poll_sensors_and_write(sensors, out_file):
    """
    Record and save the inputs in the output file.

    We are purposefully not processing this too much
    in case a bug corrupts the data before we can receive it
    """
    current_data = []

    # record the data
    for sensor in sensors:
        current_data.append(sensor.capture_data())

    # Don't have the data, e.g. if a photo has been discarded
    for d in current_data:
        if d.is_invalid():
            print("Warning: some data is invalid")
            return

    serialised_data_pieces = [d.serialise() for d in current_data]
    test_camera_data_serialisation(current_data[1], serialised_data_pieces[1])

    # append the data to the log file
    # indicate the data "length" for each data piece
    out_data = bytes()

    for i, data_piece in enumerate(serialised_data_pieces):
        # sensor id
        out_data += np.uint8(i).tobytes()
        # data length
        out_data += np.uint32(len(data_piece)).tobytes()

        # data itself
        out_data += data_piece

    out_file.write(out_data)


# Outputting data into the ./out/ folder for analysis on Earth
if __name__ == "__main__":
    start_time = datetime.now()  # Store start to keep track of time since start

    end_time = start_time + timedelta(minutes=EXPERIMENT_DURATION_MINUTES)

    if isfile(OUT_FILE) and getsize(OUT_FILE) > 0:
        print("Warning: the out file is not empty; appending to it...")

    # Set up sensors
    # NOTE: the order matters
    sensors = [TimeStampVirtualSensor(), Camera()]

    now_time = datetime.now()
    iteration_index = 1
    # repeat until we would overrun on the next iteration
    while now_time < end_time - timedelta(seconds=SECONDS_PER_ITERATION):
        """
        Open the file in every iteration so that if there is an exception
        (e.g. we have run out of space), the contents are synced into the file
        """
        with open(OUT_FILE, "ab") as out_file:
            # Main program
            poll_sensors_and_write(sensors, out_file)

            # Wait until the next time interval
            next_desired_time = start_time + timedelta(seconds=(SECONDS_PER_ITERATION * iteration_index))
            if next_desired_time > datetime.now():
                time.sleep(max(0, (next_desired_time - datetime.now()).seconds))
            # Get time now
            now_time = datetime.now()
            iteration_index += 1
    print(end_time, datetime.now())
