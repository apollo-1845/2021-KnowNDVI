
import os

import numpy as np
import cv2
from project_types import Data

from settings import IS_PROD, PREFERRED_RESOLUTION, PREFERRED_RES_NP, MASK, \
    CAN_DISCARD, USE_PNG, OUT_DIR


# Camera cover mask
cam_cover_mask = np.zeros(PREFERRED_RES_NP, dtype="uint8")
cv2.circle(cam_cover_mask, (320, 240), 250, (255, 255, 255), -1)  # White circle

# PNG image IDs
save_id = 1
not_found = os.path.exists(f"./out/{save_id}_nir.png")
while not_found:
    # Does not exist = found
    save_id += 1
    not_found = os.path.exists(f"./out/{save_id}_nir.png")
print("Image ID:", save_id)


class CameraData(Data):
    """A photo taken from a camera, with methods to convert to NDVI."""

    image = None

    def is_invalid(self):
        """See if the data should not be recorded."""
        return self.image is None

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
        """Get the raw data value stored in this wrapper."""
        return self.image

    def serialise(self) -> bytes:
        """
        Return bytes that can be stored to represent the value.

        It can be done by representing the value as bytes or
        by serialising a file name with the data
        """
        if self.image is None and not IS_PROD:
            raise Exception("The image is None for CameraData serialisation")
        elif USE_PNG:
            return self.serialise_as_png()
        else:
            global save_id
            file_id = save_id
            np.savez_compressed(f"./out/cam_data_{file_id}.npz", data=self.image)

            save_id += 1  # Next image

            return int.to_bytes(file_id, length=(save_id.bit_length()+7)//8,
                                byteorder='big')

    @staticmethod
    def deserialise(b):
        """Reverse the serialisation process."""
        if(USE_PNG):
            result = CameraData.deserialise_as_png(b)
            return result
        else:
            file_id = int.from_bytes(b, byteorder='big')
            out = CameraData()
            out.image = np.load(f"./out/cam_data_{file_id}.npz")["data"]
            return out

    def serialise_as_png(self) -> bytes:
        """Serialise the image data as a png."""
        global save_id
        # As PNG, return image ID
        image_id = save_id

        nir, vis = cv2.split(self.image)
        cv2.imwrite(os.path.join(OUT_DIR, str(image_id) + "_nir.png"), nir)
        cv2.imwrite(os.path.join(OUT_DIR, str(image_id) + "_vis.png"), vis)

        # Return as bytes; dynamic size based on size of image ID
        result = int.to_bytes(image_id, length=(image_id.bit_length()+7)//8,
                              byteorder='big')
        print("Serialised image file id", image_id)

        save_id += 1  # Next image
        return result

    @staticmethod
    def deserialise_as_png(b):
        """Deserialise the image data as a png."""
        # Load from bytes
        load_id = int.from_bytes(b, byteorder='big')
        print("Deserialised image file id", load_id)
        # As PNG, get from ID
        nir = cv2.imread(os.path.join(".", "out", str(load_id) + "_nir.png"), \
                         cv2.IMREAD_ANYCOLOR)
        vis = cv2.imread(os.path.join(".", "out", str(load_id) + "_vis.png"), \
                         cv2.IMREAD_ANYCOLOR)

        img = np.dstack((nir, vis))

        return CameraData.from_processed_np_array(img)

    def __repr__(self):
        return f"Camera data: {self.image}"

    # def display(self): # For testing
    #     """Create a preview window of the contained image"""
    #     img = self.image.copy()
    #
    #     # Fill the missing colour channel with zeroes so that it can be displayed properly
    #     img = np.lib.pad(img, ((0, 0), (0, 0), (0, 1)),
    #                      'constant', constant_values=(0))
    #
    #     # if(len(img.shape) == 2):
    #     #     # One channel - apply color map
    #     #     img = cv2.applyColorMap(img.astype(np.uint8), fastiecm)
    #
    #     # Display with cv2
    #     title = "Camera image preview"
    #     cv2.namedWindow(title)  # create window
    #     cv2.imshow(title, img)  # display image
    #     cv2.waitKey(0)  # wait for key press
    #     cv2.destroyAllWindows()

    """Onboard Image Processing"""
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
            # Discard the images if not useful
            if CameraData.should_discard(image):
                print("Discarding the image")
                return None
        return image

    @staticmethod
    def should_discard(image):
        """Discard if (1) completely black."""
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
        """Keep only NIR and VIS channels, in this order."""
        # Only blue (representing NIR) and red (representing vis (also just red)) channels
        nir, _, vis = cv2.split(image)
        # "Zips" the two arrays together
        return np.dstack((nir, vis))
