from abc import ABC, abstractmethod

import requests, numpy, cv2

from sensors.sensor import Sensor


class FakeCamera(Sensor):
    image = None

    def set_id(self, id:int):
        """Set the input image to a certain number id of the images at https://github.com/raspberrypilearning/astropi-ndvi/tree/master/en/resources"""
        # Get data link
        url = f"https://github.com/raspberrypilearning/astropi-ndvi/blob/master/en/resources/cslab3ogel_Files_RawData_raw_image_{id}.jpeg?raw=true"
        self.set_url(url)

    def set_local(self, path:str):
        with open(path, "rb") as file_bytes:
            # Set input image
            self.set_bytes(file_bytes)

    def set_url(self, url:str):
        """Set the input image to the data from a certain URL"""
        # Request data from dataset
        with requests.get(url) as r:
            byte_resp = r.content
            # Set input image
            self.set_bytes(byte_resp)

    def set_bytes(self, bytes_in:bytes):
        array_resp = numpy.array(list(bytes_in), numpy.uint8)
        # Convert to OpenCV Image
        self.image = cv2.imdecode(array_resp, cv2.IMREAD_UNCHANGED)

    def capture_data(self):
        return self.image