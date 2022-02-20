from project_types import Sensor
from sensors.camera.base_camera import CameraData

from settings import PREFERRED_RESOLUTION, PREFERRED_RES_NP

from picamera import PiCamera
import numpy as np

OUTPUT_RES_NP = PREFERRED_RES_NP + (3,)  # With 3-byte colour depth

class Camera(Sensor):
    """A physical camera using the Raspberry Pi's PiCamera API."""

    def __init__(self):
        """Initialize camera."""
        self.camera = PiCamera()
        self.camera.resolution = PREFERRED_RESOLUTION
        self.camera.start_preview()

    def capture_data(self):
        """Capture frames from self.camera."""
        output = np.empty(OUTPUT_RES_NP, dtype=np.uint8)
        self.camera.capture(output, 'bgr')

        return CameraData.from_color_image(output)
