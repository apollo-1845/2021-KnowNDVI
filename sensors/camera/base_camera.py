import numpy as np
import cv2
from project_types import Data

from sensors.camera.color_map import fastiecm
from is_prod import is_prod

PREFERRED_RESOLUTION = (640, 480)


# common class to both fake camera and real camera
class CameraData(Data):
    """A photo taken from a camera, with methods to convert to NDVI."""

    image = None

    def __init__(self, image):
        """Construct the image"""
        self.image = image
        self.image = cv2.resize(self.image, PREFERRED_RESOLUTION) # Consistent sizing

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

        if tuple(data.shape) != tuple(shape) and not is_prod:
            raise Exception(
                f"Unexpected data shape when deserialising camera data: {data.shape}, expected {shape}"
            )

        return CameraData(data)

    def __repr__(self):
        return f"Camera data: {self.image}"

    def display(self):
        img = self.image
        if(len(img.shape) == 2):
            # One channel - apply color map
            img = cv2.applyColorMap(img.astype(np.uint8), fastiecm)

        # Display with cv2
        title = self.__repr__()
        cv2.namedWindow(title)  # create window
        cv2.imshow(title, img) # display image
        cv2.waitKey(0) # wait for key press
        cv2.destroyAllWindows()

    """Onboard Processing"""

    def mask_cover(self):
        """Use a circular mask to remove camera cover"""
        # Mask out camera cover
        self.image[cam_cover_mask == 0] = np.nan
        print(self.image.shape, self.image)



# Camera cover mask
cam_cover_mask = np.zeros((480, 640), dtype="uint8")
cv2.circle(cam_cover_mask, (320, 240), 250, 1, -1) # White circle
print("Mask", cam_cover_mask)


def test_camera_data_dimensions(shape):
    if len(shape) != 3 and not is_prod:
        raise Exception(
            f"Camera data image does not have 3 dimensions. The actual number is {len(shape)}"
        )
