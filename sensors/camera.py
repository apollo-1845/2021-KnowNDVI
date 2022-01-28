from abc import ABC, abstractmethod
from project_types import Data, Sensor
import numpy as np
from picamera.array import PiRGBArray
from picamera import PiCamera
import time
import cv2


def test_camera_data_dimensions(shape):
    if len(shape) != 3:
        raise Exception(
            f"Camera data image does not have 3 dimensions. The actual number is {len(shape)}"
        )


class CameraData(Data):
    image = None


    def __init__(self, image):
        self.image = image


    def get_raw(self):
        return self.image


    def serialise(self) -> bytes:
        shape = self.image.shape
        test_camera_data_dimensions(shape)
        # 3 numbers
        shape_bytes = np.array(shape, np.uint32).tobytes()

        data_bytes = self.image.tobytes()

        return shape_bytes + data_bytes

    @staticmethod
    def deserialise(b):
        # 3 numbers, 32 bits each
        shape_data_border = 3 * 32 // 8
        shape_bytes = b[0:shape_data_border]
        data_bytes = b[shape_data_border:]

        shape = np.frombuffer(shape_bytes, dtype=np.uint32)
        test_camera_data_dimensions(shape)
        # do not use the first shape number as it is the number of the sub-array units
        subarray_type = np.dtype((np.uint8, tuple(shape[1:])))
        data = np.frombuffer(data_bytes, dtype=subarray_type)

        if tuple(data.shape) != tuple(shape):
            raise Exception(
                f"Unexpected data shape when deserialising camera data: {data.shape}, expected {shape}"
            )

        return CameraData(data)

    def __repr__(self):
        return f"Camera data: {self.image}"


class Camera(Sensor):
    def capture_data(self):
        # initialize camera + take reference to the raw camera capture
        self.camera = PiCamera()
        self.camera.resolution = (640, 480)
        self.camera.framerate = 32
        rawCamera = PiRGBArray(self.camera, size=(640, 480))
        # warm up
        time.sleep(0.1)
        
        # capture frames from self.camera
        for frame in self.camera.capture_continuous(rawCapture, fromat="bgr", use_video_port=True):
            #take raw numpy array then initalize timestamp + occupied/unoccupied text
            image = frame.array
            # show frame
            cv2.imshow("Frame", image)
            key = cv2.waitKey(1) & 0xFF
            # clear stream in prep for next frame
            rawCapture.truncate(0)
