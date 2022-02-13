from project_types import Sensor
from sensors.camera.base_camera import CameraData

from picamera import PiCamera
import numpy as np


class Camera(Sensor):
    """A physical camera using the Raspberry Pi's PiCamera API."""

    def __init__(self):
        """Initialize camera."""
        self.camera = PiCamera()
        self.camera.resolution = (640, 480)
        self.camera.start_preview()

    def capture_data(self):
        """Capture frames from self.camera."""
        output = np.empty((480, 640, 3), dtype=np.uint8)
        self.camera.capture(output, 'rgb')

        return CameraData.from_color_image(output)
