import numpy as np
from project_types import Data

#common class to both fake camera and real camera
class CameraData(Data):
    image = None


    def __init__(self, image):
        self.image = image


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

        if tuple(data.shape) != tuple(shape):
            raise Exception(
                f"Unexpected data shape when deserialising camera data: {data.shape}, expected {shape}"
            )

        return CameraData(data)

    def __repr__(self):
        return f"Camera data: {self.image}"

    def display(self):
        # Display with cv2
        title = self.__repr__()
        cv2.namedWindow(title)  # create window
        cv2.imshow(title, image) # display image
        cv2.waitKey(0) # wait for key press
        cv2.destroyAllWindows()

    """NDVI conversion"""

    def to_NDVI(self):
        nir, _, vis = cv2.split(self.image) # Image channels BRG
        total = ndvi + vis
        total[total==0] = 0.01 # No div by 0

        # More NIR = plants
        ndvi = (nir - vis) / total

        self.image = ndvi



def test_camera_data_dimensions(shape):
    if len(shape) != 3:
        raise Exception(
            f"Camera data image does not have 3 dimensions. The actual number is {len(shape)}"
        )