import sys
import os
import pytest
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from hardware_wrappers import *

MICROSCOPE_STATUS = False

def test_simulate_move_stage():
    try:
        # Convert pixel to cartesian coords
        core_wrap = CoreWrapper(MICROSCOPE_STATUS)
        coord_converter = PixToCartCoords(MICROSCOPE_STATUS)
        head_pixel_x = 0
        head_pixel_y = 0
        image_height = 512
        image_width = 512
        x_target, y_target = coord_converter.pixel_to_cartesian_coords(core_wrap, head_pixel_x, head_pixel_y,
                                                                       image_height, image_width)

        # Calculate velocity to feed in
        stage_coord_grabber = GetStageCoords(core_wrap, MICROSCOPE_STATUS)
        x_cur = stage_coord_grabber.get_x_coord()
        y_cur = stage_coord_grabber.get_y_coord()
        x_diff = x_target - x_cur
        y_diff = y_target - y_cur
        x_velocity = 6 * x_diff
        y_velocity = 6 * y_diff
        
        prev_x_direction = 1  # Positive direction
        prev_y_direction = 1 # Positive direction
        MoveStage.connectToMicroscope(MICROSCOPE_STATUS)
        MoveStage.drive_stage(x_velocity, y_velocity,
                              prev_x_direction, prev_y_direction,
                              MICROSCOPE_STATUS)

    except Exception as e:
        print(f"An error occurred: {e}")
        pytest.fail("Error in coordinate conversion to move stage flow")