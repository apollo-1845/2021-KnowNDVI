import cv2
import numpy as np
import requests

from project_types import Sensor

from sensors.camera.base_camera import CameraData


class FakeCamera(Sensor):
    """A virtual sensor that mimics a camera using images from the web"""

    current_picture_id = 1
    image = None

    def set_id(self, img_id: int):
        """Set the input image to a certain number id of the images in https://github.com/raspberrypilearning/astropi-ndvi"""
        # Get data link
        url = f"https://github.com/raspberrypilearning/astropi-ndvi/blob/master/en/resources/cslab3ogel_Files_RawData_raw_image_{img_id}.jpeg?raw=true"
        self.set_image_by_url(url)

    # def set_local(self, path: str):
    #     with open(path, "rb") as file_bytes:
    #         # Set input image
    #         self.set_image_by_bytes(file_bytes)

    def set_image_by_url(self, url: str):
        """Set the input image to the data from a certain URL"""
        # Request data from dataset
        with requests.get(url) as r:
            byte_resp = r.content
            # Set input image
            self.set_image_by_bytes(byte_resp)

    def set_image_by_bytes(self, bytes_in: bytes):
        """Store the bytes representing an image as an opencv image"""
        array_resp = np.array(list(bytes_in), np.uint8)
        # Convert to OpenCV Image
        self.image = cv2.imdecode(array_resp, cv2.IMREAD_UNCHANGED)

    def capture_data(self):
        """Imitates taking a photo and returns a new CameraData instance"""
        self.set_id(self.current_picture_id)
        # we need to get a number 1-250 inclusive, so wrap around
        self.current_picture_id = (self.current_picture_id + 1) % 249 + 1
        return CameraData.from_color_image(self.image)
