from imports_and_constants import *
from threads import ImageGrabThread, ComputerVisionThread, TrackThread
from hardware_wrappers import *

# ---- GUI Design ----#

# MainWindow class to create the GUI
class MainWindow(QWidget):

    # This will initalize the dimensions of the GUI
    def __init__(self, core_wrap: CoreWrapper, live_stream_wrap: LiveStreamWrapper):
        """ 
        Initializes the GUI.

        Parameters
        ----------
        core_wrap: CoreWrapper
            Takes an instance of the wrapper of the Core object in Micromanager.
        live_stream_wrap: LiveStreamWrapper
            Takes an instance of the wrapper of the LiveStream object in Micromanager.

        Returns
        -------
        None
        """

        super().__init__()
        self.setWindowTitle("Confocal Automated Tracking System")

        self.track_thread = None
        self.computer_vision_thread = None
        self.grab_image_thread = None
        self.core_wrap = core_wrap
        self.live_stream_wrap = live_stream_wrap
        self.track_right = True
        self.is_tracking_enabled = False

        # Labels for video feeds
        self.left_label = QLabel("Livestream from Grab Image Thread")
        self.right_label = QLabel("Livestream from Grab Image Thread")
        self.zoomed_label = QLabel("Zoomed image")
        self.segmented_label = QLabel("Segmentation Result from Computer Vision Thread")
        self.skeleton_label = QLabel("Skeleton Result from Computer Vision Thread")

        # Labels for frame titles
        self.left_video_title = QLabel("LEFT")
        self.left_video_title.setFont(QFont("Arial", 16))
        self.right_video_title = QLabel("RIGHT")
        self.right_video_title.setFont(QFont("Arial", 16))
        self.zoomed_video_title = QLabel("RIGHT CROPPED")
        self.zoomed_video_title.setFont(QFont("Arial", 16))
        self.segmented_video_title = QLabel("SEGMENTED")
        self.segmented_video_title.setFont(QFont("Arial", 16))
        self.skeleton_video_title = QLabel("TRACKING POINT")
        self.skeleton_video_title.setFont(QFont("Arial", 16))

        # Labels for buttons
        self.track_button = QPushButton("Track")
        self.track_button.setCheckable(True)
        self.track_button.setChecked(False)  # Start with the tracking loop enabled
        self.stop_stage_button = QPushButton("Stop Stage")
        self.inverse_seg_button = QPushButton("Inverse Segmentation")
        self.track_other_panel_button = QPushButton("Track Other Panel")
        self.display_capture_time_button = QPushButton("Display Capture Time")
        self.display_capture_time_button.setCheckable(True)
        self.exit_button = QPushButton("Exit")

        # self.stop_stage_button.setEnabled(False) # DEBUG

        # Create a vertical layout for the buttons on the left side
        buttons_layout = QVBoxLayout()
        buttons_layout.addSpacing(30)
        buttons_layout.addWidget(self.track_button)
        buttons_layout.addWidget(self.stop_stage_button)
        buttons_layout.addWidget(self.inverse_seg_button)
        buttons_layout.addWidget(self.track_other_panel_button)
        buttons_layout.addWidget(self.display_capture_time_button)
        buttons_layout.addWidget(self.exit_button)
        buttons_layout.addStretch()

        # Left Video Layout
        left_video_layout = QVBoxLayout()
        left_video_layout.addWidget(self.left_video_title, alignment=Qt.AlignHCenter)
        left_video_layout.addWidget(self.left_label)

        # Right Video Layout
        right_video_layout = QVBoxLayout()
        right_video_layout.addWidget(self.right_video_title, alignment=Qt.AlignHCenter)
        right_video_layout.addWidget(self.right_label)

        # Zoomed Video Layout
        zoomed_video_layout = QVBoxLayout()
        zoomed_video_layout.addWidget(self.zoomed_video_title, alignment=Qt.AlignHCenter)
        zoomed_video_layout.addWidget(self.zoomed_label)

        # Segmented Video Layout
        segmented_video_layout = QVBoxLayout()
        segmented_video_layout.addWidget(self.segmented_video_title, alignment=Qt.AlignHCenter)
        segmented_video_layout.addWidget(self.segmented_label)

        # Skeleton Video Layout
        skeleton_video_layout = QVBoxLayout()
        skeleton_video_layout.addWidget(self.skeleton_video_title, alignment=Qt.AlignHCenter)
        skeleton_video_layout.addWidget(self.skeleton_label)

        # Create a main layout to hold both the buttons layout and image/result layout
        upper_layout = QHBoxLayout()
        upper_layout.addLayout(buttons_layout)
        upper_layout.addLayout(left_video_layout)
        upper_layout.addLayout(right_video_layout)
        upper_layout.addLayout(zoomed_video_layout)
        upper_layout.addLayout(segmented_video_layout)
        upper_layout.addLayout(skeleton_video_layout)

        # Label for coordinates and velocity bar
        self.coordinates_label = QLabel("Coordinates: (0,0)")
        bottom_layout = QHBoxLayout()
        bottom_layout.addWidget(self.coordinates_label)
        bottom_layout.setAlignment(Qt.AlignLeft)

        main_layout = QVBoxLayout()
        main_layout.addLayout(upper_layout)
        main_layout.addLayout(bottom_layout)

        self.setLayout(main_layout)

        style = """ 
                QPushButton{
                    color: black;
                    border: 1px solid;
                    padding: 5px 10px;
                    border-radius: 5px;
                    font-size: 9pt;
                    outline: none;
                }
                QPushButton:checked{
                    color: white;
                    background: #a1a09f;
                    border: 1px solid;
                    padding: 5px 10px;
                    border-radius: 5px;
                    font-size: 9pt;
                    outline: none;
                }
                QPushButton:pressed{
                    color: white;
                    background: #a1a09f;
                    border: 1px solid;
                    padding: 5px 10px;
                    border-radius: 5px;
                    font-size: 9pt;
                    outline: none;
                }
                QPushButton:disabled {
                    color: grey;
                    background-color: #d3d3d3;
                    border: 1px solid grey;
                    padding: 5px 10px;
                    border-radius: 5px;
                    font-size: 9pt;
                    outline: none;
                }
                """
        self.setStyleSheet(style)

        # Connect the button's clicked signals to their respective methods
        self.track_button.clicked.connect(self.toggle_tracking_loop)
        self.exit_button.clicked.connect(self.close_application)
        self.stop_stage_button.clicked.connect(self.stop_stage)
        self.inverse_seg_button.clicked.connect(self.inverse_segmentation_clicked)
        self.display_capture_time_button.clicked.connect(self.display_capture_time)
        self.track_other_panel_button.clicked.connect(self.track_other_panel)

    # When closed the application it makes sure the stage movement from our custom API is stopped
    def close_application(self):
        """ 
        Ensures stage movement is stopped from custom API before closing the appplication.

        Parameters
        ----------
        None

        Returns
        -------
        None
        """
         
        print("Exiting the application.")

        # Make track thread stable before closing application
        if self.track_thread.is_tracking_enabled:
            self.track_thread.is_tracking_enabled = False
        self.track_thread.drive_stage(0, 0)

        if Microscope:
            self.live_stream_wrap.set_live_mode_on(False)
            self.core_wrap.set_roi(0, 0, 2048, 2048)
            self.live_stream_wrap.set_live_mode_on(True)

        self.close()

    def stop_stage(self):
        """ 
        Stops movement in all directions to stabilize stage if control is lost.

        Parameters
        ----------
        None

        Returns
        -------
        None
        """

        MoveStage.connectToMicroscope()
        MoveStage.runXYVectorialTransfer(1, 0, 1, 0)
        MoveStage.runXYVectorialTransfer(-1, 0, 1, 0)
        MoveStage.runXYVectorialTransfer(1, 0, -1, 0)
        MoveStage.runXYVectorialTransfer(-1, 0, -1, 0)
        print("Failsafe: Stopped the stage in all directions!")

    @pyqtSlot(object)
    def update_image(self, frame: np.ndarray):
        """ 
        Updates the video feed in the application.

        Parameters
        ----------
        frame: np.ndarray
            Frame being captured from micromanager livestream.

        Returns
        -------
        None
        """

        # Concatenate microscope view and zoomed in view
        copy = frame.copy()
        #original = cv2.resize(frame,(512,512))
        left = cv2.resize(frame[:,:1024],(512,512))
        right = cv2.resize(frame[:,1024:],(512,512))
        # Add condition here for right-left
        zoomed = None
        if self.track_right:
            zoomed = cv2.resize(frame[:,1024:][(512 - 385):(512 + 385), (512 - 385):(512 + 385)],(512,512)) # Get sqr crop of right panel
            self.zoomed_video_title.setText("RIGHT CROPPED")
        else:
            zoomed = cv2.resize(frame[:,:1024][(512 - 385):(512 + 385), (512 - 385):(512 + 385)],(512,512)) # Get sqr crop of left panel
            self.zoomed_video_title.setText("LEFT CROPPED")

        # Convert the NumPy array to QImage (Updated for grayscale)
        height, width = left.shape
        bytes_per_line = width
        image = QImage(left.tobytes(), width, height, bytes_per_line, QImage.Format_Grayscale8)
        pixmap = QPixmap.fromImage(image)
        self.left_label.setPixmap(pixmap)

        height, width = right.shape
        bytes_per_line = width
        image = QImage(right.tobytes(), width, height, bytes_per_line, QImage.Format_Grayscale8)
        pixmap = QPixmap.fromImage(image)
        self.right_label.setPixmap(pixmap)

        # Convert the NumPy array to QImage (Updated for grayscale)
        height, width = zoomed.shape
        bytes_per_line = width
        image = QImage(zoomed.tobytes(), width, height, bytes_per_line, QImage.Format_Grayscale8)
        pixmap = QPixmap.fromImage(image)
        self.zoomed_label.setPixmap(pixmap)

    @pyqtSlot(object)
    def update_segmented_image(self, frame: np.ndarray):
        """ 
        Updates the segmented video feed in the application.

        Parameters
        ----------
        frame: np.ndarray
            Frame being captured from segmentation loop.

        Returns
        -------
        None
        """

        # Convert the NumPy array to QImage (Updated for grayscale)
        # height, width = frame.shape

        copy = frame.copy()
        height,width = copy.shape
        bytes_per_line = width
        image = QImage(copy.tobytes(), width, height, bytes_per_line, QImage.Format_Grayscale8)

        # Set the image on the QLabel
        pixmap = QPixmap.fromImage(image)
        self.segmented_label.setPixmap(pixmap)

    @pyqtSlot(object)
    def update_skeleton_image(self, frame: np.ndarray):
        """ 
        Updates the skeletonized video feed in the application.

        Parameters
        ----------
        frame: np.ndarray
            Frame being captured from the skeletonization loop.

        Returns
        -------
        None
        """

        # Convert the NumPy array to QImage (Updated for grayscale)
        copy = frame.copy()
        copy = copy.astype('uint8') * 255
        height,width = copy.shape
        bytes_per_line = width
        image = QImage(copy.tobytes(), width, height, bytes_per_line, QImage.Format_Grayscale8)

        # Set the image on the QLabel
        pixmap = QPixmap.fromImage(image)
        self.skeleton_label.setPixmap(pixmap)

    @pyqtSlot(object)
    def update_coordinates(self, coordinates):
        """ 
        Updates the stage coordinates in live time in the GUI.

        Parameters
        ----------
        coordinates: np.ndarray
            The current stage coordinates.

        Returns
        -------
        None
        """

        self.coordinates_label.setText(f"Coordinates: ({coordinates[0]}, {coordinates[1]})")

    def toggle_tracking_loop(self):
        """ 
        Flips tracking flag.

        Parameters
        ----------
        None

        Returns
        -------
        None
        """

        # Toggle the tracking loop in the TrackThread when the button is clicked
        self.track_thread.toggle_tracking_loop()
        self.is_tracking_enabled = not self.is_tracking_enabled

        # Disable other buttons
        if(self.is_tracking_enabled):
            self.stop_stage_button.setEnabled(False)
            self.inverse_seg_button.setEnabled(False)
            self.track_other_panel_button.setEnabled(False)
        else:
            self.stop_stage_button.setEnabled(True)
            self.inverse_seg_button.setEnabled(True)
            self.track_other_panel_button.setEnabled(True)
    
    def inverse_segmentation_clicked(self):
        """ 
        Flips inverse segmentation flag.

        Parameters
        ----------
        None

        Returns
        -------
        None
        """

        self.computer_vision_thread.toggle_inverse()
        
    def track_other_panel(self):
        """ 
        Flips track left/right panel flag.

        Parameters
        ----------
        None

        Returns
        -------
        None
        """
        
        self.computer_vision_thread.toggle_track_right()
        self.track_right = not self.track_right
    
    def display_capture_time(self):
        """ 
        Displays capture time in terminal if enabled.

        Parameters
        ----------
        None

        Returns
        -------
        None
        """

        self.grab_image_thread.toggle_display_capture_time()

class SplashScreen(QSplashScreen):
    def __init__(self, parent=None):
        super(SplashScreen, self).__init__(QPixmap(r"assets\loading_screen.png"))

    def showMessage(self, message):
        self.showMessage(message, alignment=Qt.AlignBottom | Qt.AlignHCenter, color=Qt.white)