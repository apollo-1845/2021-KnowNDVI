from abc import ABC, abstractmethod
from project_types import Sensor
from picamera.array import PiRGBArray
from picamera import PiCamera
import time
import cv2
from base_camera import camera







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
        for frame in self.camera.capture_continuous(rawCamera, fromat="bgr", use_video_port=True):
            #take raw numpy array then initalize timestamp + occupied/unoccupied text
            image = frame.array
            # show frame
            cv2.imshow("Frame", image)
            key = cv2.waitKey(1) & 0xFF
            # clear stream in prep for next frame
            rawCamera.truncate(0)
