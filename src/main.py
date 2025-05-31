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
from threads import *
from gui import *
from hardware_wrappers import *

# ---- Main Function ----#

if __name__ == "__main__":
    app = QApplication(sys.argv)

    splash = SplashScreen()
    splash.show()
    time.sleep(1)
    splash.close()

    # global live_stream_wrap
    live_stream_wrap = LiveStreamWrapper(microscope_online)

    # Check to make sure the livestream is open first, this makes image capture faster
    if live_stream_wrap.get_is_live_mode_on() == False:
        print("Turn on the livestream before running our program!")
        QMessageBox.critical(None,"Error","Turn on the livestream before running our program!")
        sys.exit()

    ref_time = time.time()

    # global core_wrap
    core_wrap = CoreWrapper(microscope_online)
    print("Initialization 1/7: Core and LiveStreamManager initialized")

    if microscope_online:
        live_stream_wrap.set_live_mode_on(False)
        core_wrap.set_roi(0,512,2048,1024)
        live_stream_wrap.set_live_mode_on(True)
    print("Initialization 2/7: Livestream ROI Changed")

    # Create the main window
    window = MainWindow(core_wrap,live_stream_wrap,microscope_online)
    print("Initialization 3/7: Main Window Created")

    # Initialize and start the grab image thread
    grab_image_thread = ImageGrabThread(live_stream_wrap, microscope_online) # New parameter
    grab_image_thread.frame_ready.connect(window.update_image) # Sends captured image to MainWindow
    window.grab_image_thread = grab_image_thread
    grab_image_thread.start()
    print("Initialization 4/7: Grab Image Thread Started")

    # Initialize and start the computer vision thread
    computer_vision_thread = ComputerVisionThread(core_wrap, microscope_online)
    grab_image_thread.frame_ready.connect(computer_vision_thread.receive_frame) # Sends captured image to ComputerVisionThread
    computer_vision_thread.result_ready.connect(window.update_segmented_image) # Sends segmented image to MainWindow
    computer_vision_thread.skeleton_ready.connect(window.update_skeleton_image)  # Sends skeleton image to MainWindow
    window.computer_vision_thread = computer_vision_thread
    computer_vision_thread.start()
    print("Initialization 5/7: Computer Vision-Segmentation Thread Started")

    # Initialize and start the track thread
    track_thread = TrackThread(core_wrap, microscope_online)
    track_thread.cur_coordinates_ready.connect(window.update_coordinates)
    computer_vision_thread.tracking_ready.connect(track_thread.receive_tracking_pointer) # Sends tracking coordinates from ComputerVisionThread to TrackThread
    window.track_thread = track_thread
    track_thread.start()
    print("Initialization 6/7: Track Thread Started")

    # Show the main window
    window.show()
    print("Initialization 7/7: Show GUI to User")

    # Start the GUI event loop
    sys.exit(app.exec_())

