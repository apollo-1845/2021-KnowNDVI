from abc import ABC, abstractmethod

import requests, numpy, cv2

from sensors.sensor import Sensor


class FakeCamera(Sensor):
    url = None

    def set_image(self, id):
        """Set the input image to a certain number id of the images at https://github.com/raspberrypilearning/astropi-ndvi/tree/master/en/resources"""
        self.url = f"https://github.com/raspberrypilearning/astropi-ndvi/blob/master/en/resources/cslab3ogel_Files_RawData_raw_image_{id}.jpeg?raw=true"

    def capture_data(self):
        # Get data link
        url = self.url
        # Request data from dataset
        r = requests.get(url)
        byte_resp = r.content
        array_resp = numpy.array(list(byte_resp), numpy.uint8)
        r.close()
        # Convert to OpenCV Image
        image = cv2.imdecode(array_resp, cv2.IMREAD_UNCHANGED)
        return image