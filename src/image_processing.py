# Copyright 2025 Danish Islam
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from imports_and_constants import *
from hardware_wrappers import LiveStreamWrapper, CoreWrapper

# Abstraction for retrieving image
class ImageGrabber():

    def __init__(self, microscope_online: bool):
        self.microscope_online = microscope_online

    def get_image(self, live_stream_wrap: LiveStreamWrapper) -> np.ndarray:
        """ 
        Grabs an image from the live stream wrapper.

        Parameters
        ----------
        live_stream_wrap: LiveStreamWrapper
            Takes an instance of the wrapper of the LiveStream object in Micromanager.

        Returns
        -------
        np.ndarray
            Returns a 2D image.
        """

        if self.microscope_online:
            # Only runs when micromanager live stream is on
            img = live_stream_wrap.snap(False)
            tagged_image = img.get(0).legacy_to_tagged_image()

            image_array = np.reshape(
                tagged_image.pix,
                newshape=[-1, tagged_image.tags['Height'], tagged_image.tags['Width']]
            )

            image_array = (image_array / image_array.max() * 255).astype("uint8")[0, :, :]
            return image_array
        
        else:
            # reshaped_img = np.random.randint(0, 256, size=(2048, 2048), dtype=np.uint16) # Detached
            time.sleep(0.05)
            reshaped_img = np.load(r'tests\hongruo.npy')[512:1536,:] # The image would already be cropped
            image = (reshaped_img / reshaped_img.max() * 255).astype("uint8")
            return image

# Abstraction for segmentation
class ImageSegmentation():

    # Simple binary segmentation function
    @staticmethod
    def binary_thresholding(sqr_crop_img: np.ndarray) -> np.ndarray:
        """ 
        Performs binary thresholding on an input grayscale image. Values above
        the 99.96th percentile are set to 255 and the rest 0.

        Parameters
        ----------
        sqr_crop_img: np.ndarray
            Takes the cropped version of the captured image.

        Returns
        -------
        np.ndarray
            Returns a 2D binary thresholded image.
        """
        frame = cv2.resize(sqr_crop_img,(512,512))
        threshold = np.quantile(frame,0.9996)
        frame[frame >= threshold] = 255
        frame[frame < threshold] = 0

        return frame
    
    @staticmethod
    def inverted_binary_thresholding(sqr_crop_img:np.ndarray) -> np.ndarray:
        """ 
        Performs inverted binary thresholding on an input grayscale image. 
        Values above the 2nd percentile are set to 255 and the rest 0.

        Parameters
        ----------
        sqr_crop_img: np.ndarray
            Takes the cropped version of the captured image.

        Returns
        -------
        np.ndarray
            Returns a 2D binary thresholded image.
        """

        frame = cv2.resize(sqr_crop_img,(512,512))
        threshold = np.quantile(frame,1-0.98)
        frame[frame >= threshold] = 255
        frame[frame < threshold] = 0

        # Inversion
        frame = 255 - frame
        return frame
    
    @staticmethod
    def find_center(segmented:np.ndarray) -> tuple:
        """ 
        Finds the center of mass in the segmented image, returns
        coordinates as a tuple.

        Parameters
        ----------
        segmented: np.ndarray
            Takes the binary thresholded image.

        Returns
        -------
        tuple
            Returns an XY coordinate for the pixel corresponding to
            the center of mass.
        """

        # Normalize it so that it is easier to computer center of mass
        segmented = segmented / 255

        # Calcualte scipy's center of mass and return as int for pixel location
        center =  scipy.ndimage.measurements.center_of_mass(segmented)
        center = (int(center[1]),int(center[0]))
        return center