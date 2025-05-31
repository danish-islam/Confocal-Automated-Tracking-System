import sys
import os
import pytest
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from image_processing import *

MICROSCOPE_STATUS = False

def test_image_grab_and_binthreshold():
    # Retrieve image
    live_stream_wrap = LiveStreamWrapper(MICROSCOPE_STATUS)
    image_grabber = ImageGrabber(MICROSCOPE_STATUS)
    actual_raw_img = image_grabber.get_image(live_stream_wrap)

    expected_raw_img = np.load(r'tests/hongruo.npy')[512:1536,:]
    expected_raw_img = (expected_raw_img / expected_raw_img.max() * 255).astype("uint8")
    assert np.array_equal(actual_raw_img, expected_raw_img)

    # Do binary thresholding
    actual_segmented_img = ImageSegmentation.binary_thresholding(actual_raw_img)

    expected_segmented_img = cv2.resize(expected_raw_img,(512,512))
    threshold = np.quantile(expected_segmented_img, 0.9996)
    expected_segmented_img[expected_segmented_img >= threshold] = 255
    expected_segmented_img[expected_segmented_img < threshold] = 0
    assert np.array_equal(actual_segmented_img, expected_segmented_img)

    # Find center of mass
    actual_pixel_coordinates = ImageSegmentation.find_center(actual_segmented_img)
    expected_pixel_coordinates = (355, 282)
    assert (actual_pixel_coordinates == expected_pixel_coordinates)


def test_image_grab_and_inverse_binthreshold():
    # Retrieve image
    live_stream_wrap = LiveStreamWrapper(MICROSCOPE_STATUS)
    image_grabber = ImageGrabber(MICROSCOPE_STATUS)
    actual_raw_img = image_grabber.get_image(live_stream_wrap)

    expected_raw_img = np.load(r'tests/hongruo.npy')[512:1536,:]
    expected_raw_img = (expected_raw_img / expected_raw_img.max() * 255).astype("uint8")
    assert np.array_equal(actual_raw_img, expected_raw_img)

    # Do binary thresholding
    actual_segmented_img = ImageSegmentation.inverted_binary_thresholding(actual_raw_img)

    expected_segmented_img = cv2.resize(expected_raw_img,(512,512))
    threshold = np.quantile(expected_segmented_img, 1-0.98)
    expected_segmented_img[expected_segmented_img >= threshold] = 255
    expected_segmented_img[expected_segmented_img < threshold] = 0
    expected_segmented_img = 255 - expected_segmented_img # Inversion
    assert np.array_equal(actual_segmented_img, expected_segmented_img)

    # Find center of mass
    actual_pixel_coordinates = ImageSegmentation.find_center(actual_segmented_img)
    expected_pixel_coordinates = (351, 236)
    assert (actual_pixel_coordinates == expected_pixel_coordinates)

