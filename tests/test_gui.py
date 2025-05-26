import sys
import os
import pytest
from PyQt5 import QtCore
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from gui import *

MICROSCOPE_STATUS = False

def create_window():
    live_stream_wrap = LiveStreamWrapper(MICROSCOPE_STATUS)
    core_wrap = CoreWrapper(MICROSCOPE_STATUS)
    print("Core and LiveStreamManager initialized")

    window = MainWindow(core_wrap,live_stream_wrap,MICROSCOPE_STATUS)
    print("Main Window Created")

    grab_image_thread = ImageGrabThread(live_stream_wrap, MICROSCOPE_STATUS) # New parameter
    grab_image_thread.frame_ready.connect(window.update_image) # Sends captured image to MainWindow
    window.grab_image_thread = grab_image_thread
    grab_image_thread.start()
    print("Grab Image Thread Started")

    computer_vision_thread = ComputerVisionThread(core_wrap, MICROSCOPE_STATUS)
    grab_image_thread.frame_ready.connect(computer_vision_thread.receive_frame) # Sends captured image to ComputerVisionThread
    computer_vision_thread.result_ready.connect(window.update_segmented_image) # Sends segmented image to MainWindow
    computer_vision_thread.skeleton_ready.connect(window.update_skeleton_image)  # Sends skeleton image to MainWindow
    window.computer_vision_thread = computer_vision_thread
    computer_vision_thread.start()
    print("Computer Vision-Segmentation Thread Started")

    track_thread = TrackThread(core_wrap, MICROSCOPE_STATUS)
    track_thread.cur_coordinates_ready.connect(window.update_coordinates)
    computer_vision_thread.tracking_ready.connect(track_thread.receive_tracking_pointer) # Sends tracking coordinates from ComputerVisionThread to TrackThread
    window.track_thread = track_thread
    track_thread.start()
    print("Track Thread Started")

    return window

def test_main_window_button_clicks(qtbot):
    window = create_window()
    qtbot.addWidget(window)
    window.show()

    assert window.track_button.isEnabled()
    assert window.stop_stage_button.isEnabled()
    assert window.inverse_seg_button.isEnabled()
    assert window.track_other_panel_button.isEnabled()
    assert window.display_capture_time_button.isEnabled()
    assert window.exit_button.isEnabled()

    qtbot.mouseClick(window.track_button, QtCore.Qt.LeftButton)
    assert not window.stop_stage_button.isEnabled()
    assert not window.inverse_seg_button.isEnabled()
    assert not window.track_other_panel_button.isEnabled()

    qtbot.mouseClick(window.track_button, QtCore.Qt.LeftButton)
    assert window.track_button.isEnabled()
    assert window.stop_stage_button.isEnabled()
    assert window.inverse_seg_button.isEnabled()
    assert window.track_other_panel_button.isEnabled()
    assert window.display_capture_time_button.isEnabled()
    assert window.exit_button.isEnabled()

    qtbot.mouseClick(window.exit_button, QtCore.Qt.LeftButton)

def test_display_information(qtbot):
    window = create_window()
    qtbot.addWidget(window)
    window.show()

    actual_video_title = window.zoomed_video_title.text()
    expected_video_title = "RIGHT CROPPED"
    assert (actual_video_title == expected_video_title)

    qtbot.mouseClick(window.track_other_panel_button, QtCore.Qt.LeftButton)
    qtbot.waitUntil(lambda: window.zoomed_video_title.text() == "LEFT CROPPED", timeout=2000)
    actual_zoomed_video_title = window.zoomed_video_title.text()
    expected_zoomed_video_title = "LEFT CROPPED"
    assert (actual_zoomed_video_title == expected_zoomed_video_title)

    actual_coordinate_text = window.coordinates_label.text()
    expected_coordinate_text = "Coordinates: (0,0)"
    assert (actual_coordinate_text == expected_coordinate_text)


