import numpy as np
import cv2
from project_types import Data

from sensors.camera.color_map import fastiecm
from settings import IS_PROD, PREFERRED_RESOLUTION, PREFERRED_RES_NP, MASK

class CameraData(Data):
    """A photo taken from a camera, with methods to convert to NDVI."""

    image = None

    def from_color_image(image):
        """Represent a raw image as an NDVI image."""
        instance = CameraData()
        instance.image = CameraData.process(image)
        return instance

    def from_processed_np_array(image):
        """Construct a CameraData object from processed data."""
        instance = CameraData()
        instance.image = image
        return instance

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

        if tuple(data.shape) != tuple(shape) and not IS_PROD:
            raise Exception(
                f"Unexpected data shape when deserialising camera data: {data.shape}, expected {shape}"
            )

        return CameraData.from_processed_np_array(data)

    def __repr__(self):
        return f"Camera data: {self.image}"

    def display(self):
        img = self.image.copy()

        # Fill the missing colour channel with zeroes
        img = np.lib.pad(img, ((0,0), (0,0),(0,1)), 'constant', constant_values=(0))

        # if(len(img.shape) == 2):
        #     # One channel - apply color map
        #     img = cv2.applyColorMap(img.astype(np.uint8), fastiecm)

        # Display with cv2
        title = "Camera image preview"
        cv2.namedWindow(title)  # create window
        cv2.imshow(title, img) # display image
        cv2.waitKey(0) # wait for key press
        cv2.destroyAllWindows()

    """Onboard Processing"""
    def process(image):
        """Onboard processing to represent an image as a numpy array."""
        # Resize
        image = cv2.resize(image, PREFERRED_RESOLUTION)  # Consistent sizing
        # 2 channels
        image = CameraData.extract_channels(image)
        if MASK:
            # Remove the pixels that correspond to the window of the ISS
            image = CameraData.mask_cover(image)
        return image

    @staticmethod
    def mask_cover(image):
        """Use a circular mask to remove camera cover."""
        # Mask out camera cover
        image[cam_cover_mask == 0] = 0
        print(image.shape, image)
        return image

    def extract_channels(image):
        """Keep only NIR and VIS channels in this order."""
        # Only blue (representing NIR) and red (representing vis (also just red)) channels
        nir, _, vis = cv2.split(image)
        # "Zips" the two arrays together
        return np.dstack((nir, vis))


# Camera cover mask
cam_cover_mask = np.zeros(PREFERRED_RES_NP, dtype="uint8")
cv2.circle(cam_cover_mask, (320, 240), 250, (255, 255, 255), -1)  # White circle


def test_camera_data_dimensions(shape):
    if len(shape) != 3 and not IS_PROD:
        raise Exception(
            f"Camera data image does not have 3 dimensions. The actual number is {len(shape)}"
        )
