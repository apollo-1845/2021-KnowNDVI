import math
import os

import numpy as np
import cv2
from project_types import Data

from sensors.camera.color_map import fastiecm
from settings import IS_PROD, PREFERRED_RESOLUTION, PREFERRED_RES_NP, MASK, CAN_DISCARD, USE_PNG, OUT_DIR


# Camera cover mask
cam_cover_mask = np.zeros(PREFERRED_RES_NP, dtype="uint8")
cv2.circle(cam_cover_mask, (320, 240), 250, (255, 255, 255), -1)  # White circle


# PNG image IDs
save_id = 1
not_found = os.path.exists(os.path.join(".", "out", str(save_id) + "_nir.png"))
while (not_found):
    # Does not exist = found
    save_id += 1
    not_found = os.path.exists(os.path.join(".", "out", str(save_id) + "_nir.png"))
print("Image ID:", save_id)


class CameraData(Data):
    """A photo taken from a camera, with methods to convert to NDVI."""

    image = None

    @staticmethod
    def from_color_image(image):
        """Represent a raw image as an NDVI image."""
        img = CameraData.process(image)
        instance = CameraData()
        instance.image = img
        return instance

    @staticmethod
    def from_processed_np_array(image):
        """Construct a CameraData object from processed data."""
        instance = CameraData()
        instance.image = image
        return instance

    def get_raw(self):
        return self.image

    def serialise(self) -> bytes:
        if (self.image is None):
            return None  # No image - discarded
        elif(USE_PNG):
            return self.serialise_save()
        else:

            shape = self.image.shape
            test_camera_data_dimensions(shape)
            # 3 numbers
            shape_bytes = np.array(shape, np.uint32).tobytes()

            data_bytes = self.image.tobytes()

            return shape_bytes + data_bytes

    @staticmethod
    def deserialise(b):
        if(b == 0x00):
            # No image
            return None
        elif(USE_PNG):
            result = CameraData.deserialise_save(b)
            return result
        else:
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

    def serialise_save(self) -> bytes:
        global save_id
        # As JPEG, return image ID
        image_id = save_id

        nir, vis = cv2.split(self.image)
        cv2.imwrite(os.path.join(OUT_DIR, str(image_id) + "_nir.png"), nir)
        cv2.imwrite(os.path.join(OUT_DIR, str(image_id) + "_vis.png"), vis)

        # Return as bytes; dynamic size based on size of image ID
        result = int.to_bytes(image_id, length=(image_id.bit_length()+7)//8, byteorder='big')
        print("EN", image_id)

        save_id += 1 # Next image
        return result

    @staticmethod
    def deserialise_save(b):
        # Load from bytes
        load_id = int.from_bytes(b, byteorder='big')
        print("DE", save_id)
        # As JPEG, get from ID
        nir = cv2.imread(os.path.join(".", "out", str(load_id) + "_nir.png"), cv2.IMREAD_ANYCOLOR)
        vis = cv2.imread(os.path.join(".", "out", str(load_id) + "_vis.png"), cv2.IMREAD_ANYCOLOR)

        img = np.dstack((nir, vis))

        return CameraData.from_processed_np_array(img)


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
        if CAN_DISCARD:
            # Discard if not useful
            discard = CameraData.should_discard(image)
            if(discard):
                print("Discarding")
                return None
        return image

    @staticmethod
    def should_discard(image):
        """Discard if (1) completely black"""
        if(np.nanmax(image) <= 100):
            # Completely black - night - cannot use
            return True
        return False

    def mask_cover(image):
        """Use a circular mask to remove camera cover."""
        # Mask out camera cover
        image[cam_cover_mask == 0] = 0
        return image

    def extract_channels(image):
        """Keep only NIR and VIS channels in this order."""
        # Only blue (representing NIR) and red (representing vis (also just red)) channels
        nir, _, vis = cv2.split(image)
        # "Zips" the two arrays together
        return np.dstack((nir, vis))

def test_camera_data_dimensions(shape):
    if len(shape) != 3 and not IS_PROD:
        raise Exception(
            f"Camera data image does not have 3 dimensions. The actual number is {len(shape)}"
        )
