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
from hardware_wrappers import CoreWrapper, LiveStreamWrapper, GetStageCoords, MoveStage, PixToCartCoords
from image_processing import ImageGrabber, ImageSegmentation

# ---- Classes for all interactive threads ----#

# ImageGrabThread is an object that continuously grab images and sends it to ComputerVisionThread as well as MainWindow
class ImageGrabThread(QThread):

    # Define signal to emit image data to other classes
    frame_ready = pyqtSignal(object)

    def __init__(self, live_stream_wrap: LiveStreamWrapper, microscope_online: bool):
        """ 
        Initializes Image Grabber thread.

        Parameters
        ----------
        live_stream_wrap: LiveStreamWrapper
            Takes an instance of the wrapper of the LiveStream object in Micromanager.
        microscope_online: bool
            Boolean variable set to true if microscope is online

        Returns
        -------
        None
        """

        super().__init__()
        self.display_capture_time = False
        self.live_stream_wrap = live_stream_wrap
        self.microscope_online = microscope_online
    
    def toggle_display_capture_time(self):
        """ 
        Toggles display capture time.

        Parameters
        ----------
        None

        Returns
        -------
        None
        """

        self.display_capture_time = not self.display_capture_time
        print("Display capture time toggled:", self.display_capture_time)

    def run(self):
        """ 
        Begins the Image Grabber thread.

        Parameters
        ----------
        None

        Returns
        -------
        None
        """

        image_grabber = ImageGrabber(self.microscope_online) # Move out of loop for efficiency!

        while True:
            s = time.time()
            frame = image_grabber.get_image(self.live_stream_wrap)
            frame = np.flipud(frame) # NOTE: Had to invert y-axis for new camera!
            e = time.time()
            if(self.display_capture_time):
                print("Image capture time: " + str(e-s)) # DEBUG

            self.frame_ready.emit(frame)

# ComputerVisionThread is an object that performs computer vision segmentation, then sends the data to coordinates to TrackThread
# and segmentation/skeleton images to the MainWindow
class ComputerVisionThread(QThread):

    # Define your signals for emitting to other objects
    result_ready = pyqtSignal(object)
    tracking_ready = pyqtSignal(object)
    skeleton_ready = pyqtSignal(object)

    def __init__(self,core_wrap: CoreWrapper, microscope_online: bool):
        """ 
        Initializes Computer Vision thread.

        Parameters
        ----------
        core_wrap: CoreWrapper
            Takes an instance of the wrapper of the Core object in Micromanager.
        microscope_online: bool
            Boolean variable set to true if microscope is online

        Returns
        -------
        None
        """

        super().__init__()
        self.inverse = False
        self.track_right = True
        self.core_wrap = core_wrap
        self.microscope_online = microscope_online

    def toggle_inverse(self):
        """ 
        Toggles inverse segmentation.

        Parameters
        ----------
        None

        Returns
        -------
        None
        """

        self.inverse = not self.inverse
        print("Inverse segmentation toggled:", self.inverse)
    
    def toggle_track_right(self):
        """ 
        Toggles track right channel flag.

        Parameters
        ----------
        None

        Returns
        -------
        None
        """

        self.track_right = not self.track_right
        if(self.track_right):
            print("Track other panel toggled: Track Right")
        else:
            print("Track other panel toggled: Track Left")
    
    @pyqtSlot(object)
    def receive_frame(self, frame: np.ndarray):
        """ 
        Computer Vision thread receives frame from Image Grabber thread.

        Parameters
        ----------
        frame: np.ndarray
            Takes cropped image from Image Grabber thread.

        Returns
        -------
        None
        """

        if self.track_right:
            self.sqr_crop_img = frame[:,1024:][(512 - 385):(512 + 385), (512 - 385):(512 + 385)]
        else:
            self.sqr_crop_img = frame[:,:1024][(512 - 385):(512 + 385), (512 - 385):(512 + 385)]

    def run(self):
        """ 
        Begins the Computer Vision thread.

        Parameters
        ----------
        None

        Returns
        -------
        None
        """

        coordinate_converter = PixToCartCoords(self.microscope_online)

        while True:
            try:
                # Perform segmentation here
                segmented = None
                if self.inverse == False:
                    segmented = ImageSegmentation.binary_thresholding(self.sqr_crop_img)
                elif self.inverse == True:
                    segmented = ImageSegmentation.inverted_binary_thresholding(self.sqr_crop_img)
                time.sleep(0.09)

                # If the mask has non-zero values
                if np.any(segmented):

                    # Calculate the coordinate to recentre on and emit it
                    head_coordinates = ImageSegmentation.find_center(segmented)

                    cart_coords = coordinate_converter.pixel_to_cartesian_coords(self.core_wrap,head_coordinates[0], head_coordinates[1], 512, 512)

                    self.tracking_ready.emit(cart_coords)

                    # Emit segmented image to MainWindow
                    self.result_ready.emit(segmented)

                    # Emit skeleton image to MainWindow (In this case the center of mass visualization)
                    color = (1,1,1)
                    track_img = cv2.circle(np.float32(segmented),head_coordinates,10,color,2)
                    self.skeleton_ready.emit(track_img)

                else:
                    print("Lighting conditions aren't good")

            except:
                # Emit error message in case of emergency
                disp_img = np.load(r"assets\cv_error.npy")
                self.segmented = disp_img
                self.track_img = disp_img
                self.result_ready.emit(self.segmented)
                self.skeleton_ready.emit(self.segmented)
                self.tracking_ready.emit(-1)

# TrackThread is an object that perform tracking through a proportional controller
class TrackThread(QThread):
    cur_coordinates_ready = pyqtSignal(object)

    # Constructor to connect to microscope and set default previous directions
    def __init__(self,core_wrap, microscope_online: bool):
        """ 
        Initializes tracking thread.

        Parameters
        ----------
        microscope_online: bool
            Boolean variable set to true if microscope is online

        Returns
        -------
        None
        """

        super().__init__()
        self.core_wrap = core_wrap
        self.track_coords = None
        self.is_tracking_enabled = False  # Flag to indicate whether the tracking loop is enabled
        self.prev_x_direction = 1
        self.prev_y_direction = 1
        self.microscope_online = microscope_online
        MoveStage.connectToMicroscope(self.microscope_online)

        # self.drive_stage(0,0)

    # Make destructor to stop last movement, when program is terminated
    def __del__(self):
        """ 
        Destructor for Tracking thread, stops movement before program termination.

        Parameters
        ----------
        None

        Returns
        -------
        None
        """

        print("Reached!")
        self.drive_stage(0,0)

    # Receive the tracking pointer
    @pyqtSlot(object)
    def receive_tracking_pointer(self, pointer):
        """ 
        Computer Vision thread delivers tracking point to Tracking thread.

        Parameters
        ----------
        pointer: np.ndarray
            Desired tracking coordinates.

        Returns
        -------
        None
        """

        # Receive the tracking pointer from ComputerVisionThread
        self.track_coords = pointer
        self.start()  # Start the tracking thread when the pointer is received

    # This is the function to drive the stage, it receives the x, y velocities
    def drive_stage(self,x_velocity,y_velocity):
        """ 
        Calls custom stage API to drive the stage in a given x and y velocity.

        Parameters
        ----------
        x_velocity: float
            Desired X velocity of stage.
        y_velocity: float
            Desired Y velocity of stage.

        Returns
        -------
        None
        """

        # ti2_stage_wrapper.startAndStopMovement stops the previous movement by taking the previous direction of the movement, and begins a new one
        MoveStage.drive_stage(x_velocity,y_velocity,
                              self.prev_x_direction,self.prev_y_direction,
                              self.microscope_online)
        # Update previous movement direction
        self.prev_x_direction = 1 if (x_velocity > 0) else -1
        self.prev_y_direction = 1 if (y_velocity > 0) else -1

    def run(self):
        """ 
        Begins the Track thread.

        Parameters
        ----------
        None

        Returns
        -------
        None
        """

        get_stage_coords = GetStageCoords(self.core_wrap, self.microscope_online)

        while self.track_coords is not None and self.track_coords != -1:
            x_cur_pos = get_stage_coords.get_x_coord()
            y_cur_pos = get_stage_coords.get_y_coord()
            self.cur_coordinates_ready.emit([round(x_cur_pos, 1), round(y_cur_pos, 1)])
            if self.is_tracking_enabled:  # Check if the tracking loop is enabled

                # Proportional controller
                x_diff = self.track_coords[0] - x_cur_pos
                y_diff = self.track_coords[1] - y_cur_pos # TODO account for inversion
                x_velocity = 6 * x_diff
                y_velocity = 6 * y_diff

                self.drive_stage(x_velocity, y_velocity)
                # print("Tracking: " + str(self.track_coords) + " Time: " + str(time.time() - ref_time))
            time.sleep(0.05)  # Temp change to increase tracking framerate

    def toggle_tracking_loop(self):
        """ 
        Toggles the tracking flag.

        Parameters
        ----------
        None

        Returns
        -------
        None
        """

        # Toggle the state of the tracking loop when the button is clicked
        self.is_tracking_enabled = not self.is_tracking_enabled
        if self.is_tracking_enabled:
            print("Tracking loop enabled.")
        else:
            print("Tracking loop paused.")
            time.sleep(0.1)  # This should give run enough time to update its last directions to prevent -4 error
            self.drive_stage(0,0) # Stop last movement if tracking loop is paused!
