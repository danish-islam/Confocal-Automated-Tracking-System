"""
This is the confocal Record and Compress program!

Next step: Now insert image info in text file
"""

from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QVBoxLayout, QWidget, QMessageBox, QSizePolicy, QSlider, QLabel, QFileDialog
from PyQt5.QtCore import QThread, pyqtSignal, Qt, QTimer
from queue import Queue
import time
import numpy as np
import pycromanager
import sys
import os
import shutil
from datetime import datetime
import tifffile
from pycromanager import Core

Microscope = True # If False, simulates image capture

dataset_name = "image"
Time = True
temp_path = ".\\temp\\"
default_output_path = ".\\temp"

# Wrapper for MicroManager core
class CoreWrapper():
    def __init__(self):
        if Microscope:
            self.core_instance = Core() # Microscope
        else:
            pass # Detached

    def get_x_position(self):
        if Microscope:
            return self.core_instance.get_x_position() # Microscope
        else:
            return 0 # Detached

    def get_y_position(self):
        if Microscope:
            return self.core_instance.get_y_position() # Microscope
        else:
            return 0 # Detached

    def set_roi(self,x_start,y_start,x_size,y_size):
        if Microscope:
            self.core_instance.set_roi(x_start,y_start,x_size,y_size)
        else:
            pass

# Abstraction for receiving stage coordinates
class GetStageCoords():
    @staticmethod
    def get_x_coord(core_wrap: CoreWrapper):
        if Microscope:
            return core_wrap.get_x_position() # Microscope
        else:
            return 0 # Detached

    @staticmethod
    def get_y_coord(core_wrap: CoreWrapper):
        if Microscope:
            return core_wrap.get_y_position() # Microscope
        else:
            return 0 # Detached

class LiveStreamWrapper():
    def __init__(self):
        if Microscope:
            self.livestream_instance = pycromanager.Studio().get_snap_live_manager() # Microscope
        else:
            pass # Detached

    def get_is_live_mode_on(self):
        if Microscope:
            return self.livestream_instance.get_is_live_mode_on() # Microscope
        else:
            return True # Detached

    def snap(self,display_img_bool):
        frame = None
        if Microscope:
            frame = self.livestream_instance.snap(display_img_bool)
        else:
            time.sleep(0.1)
            frame = np.load('hongruo.npy')[512:1536,:]
        return frame # Microscope

    def is_live_mode_on(self):
        if Microscope:
            return self.livestream_instance.is_live_mode_on()
        else:
            pass

    def set_live_mode_on(self,on_or_off):
        if Microscope:
            return self.livestream_instance.set_live_mode_on(on_or_off)
        else:
            pass

# Abstraction for retrieving image
class ImageGrabber():
    @staticmethod
    def get_image(live_stream_wrap: LiveStreamWrapper):
        if Microscope:
            # Only runs when micromanager live stream is on
            img = live_stream_wrap.snap(False)
            tagged_image = img.get(0).legacy_to_tagged_image()

            image_array = np.reshape(
                tagged_image.pix,
                newshape=[-1, tagged_image.tags['Height'], tagged_image.tags['Width']]
            )

            # image_array = (image_array / image_array.max() * 255).astype("uint8")[0, :, :]
            # image_array = (image_array).astype("uint8")[0, :, :] # No autocorrection
            time.sleep(0.02) # Gets closer to 10 Hz
            return image_array # 16 bit!!!

        else:
            s = time.time()
            reshaped_img = np.load('hongruo.npy')[512:1536,:] # The image would already be cropped
            # reshaped_img = np.random.randint(0, 256, size=(2048, 2048), dtype=np.uint16) # Detached
            image = (reshaped_img / reshaped_img.max() * 255).astype("uint8")
            # image = (reshaped_img).astype("uint8") # No autocorrection
            time.sleep(0.06)
            e = time.time()

            # print("Time for getting image: " + str(e-s))
            return image

class RecordingThread(QThread):
    count_updated = pyqtSignal(int)

    def __init__(self, image_queue):
        super().__init__()
        self.image_queue = image_queue
        self.is_recording = False
        self.count = 0

    def run(self):
        while True:
            if self.is_recording:
                s = time.time()
                frame = ImageGrabber.get_image(live_stream_wrap)
                e = time.time()

                # This block takes about 0.006s
                x_cur_pos = GetStageCoords.get_x_coord(core_wrap)
                y_cur_pos = GetStageCoords.get_y_coord(core_wrap)
                elapsed_time = time.time() - mainWindow.start_time
                # print([x_cur_pos,y_cur_pos, elapsed_time]) # Put this in a tuple of (image, x_cur_pos, y_cur_pos, elapsed_time)
                frame_info = (frame,x_cur_pos,y_cur_pos,elapsed_time)

                self.image_queue.put(frame_info) # Put tuple in queue
                # print("Image capture time: " + str(round(e-s,2)) +", Count: " + str(self.count)) # DEBUG
                self.count_updated.emit(self.count)
                self.count += 1

    def toggle_recording(self):
        self.is_recording = not self.is_recording

    def stop(self):
        self.is_running = False

class WriteToDiskThread(QThread):
    count_updated = pyqtSignal(int)

    def __init__(self, image_queue, file_queue, parent=None):
        super().__init__(parent)
        self.image_queue = image_queue
        self.recording = False  # Add a recording state variable
        self.count = 0
        self.running = True
        self.output_path = default_output_path
        self.text_file_path = None
        self.recording_path = ""

    def run(self):
        time.sleep(0.1)
        while self.running:
            if not self.image_queue.empty():
                s = time.time()

                # Grab image from queue and save it
                # get tuple from queue
                image_info = self.image_queue.get()
                image = image_info[0]
                tiff_file_path = self.numpy_image_to_tiff(image) 

                # Write to text file 
                data = (self.count, (image_info[1],image_info[2]),image_info[3])
                with open(writetodiskThread.text_file_path, 'a') as file:
                    file.write(str(data) + '\n')

                e = time.time()
                # print("Save to disk time: " + str(round(e-s,2)) + ",  Count: " + str(self.count)) # DEBUG
                self.count += 1

            else:
                time.sleep(0.1)  # Sleep briefly to avoid hogging CPU

    def toggle_recording(self):
        self.recording = not self.recording  # Toggle the recording state

    def numpy_image_to_tiff(self, image):
        tiff_output_path = "frame_" + str(self.count) + ".tif"
        full_path = self.recording_path + "\\" + tiff_output_path
        tifffile.imwrite(full_path, image, compression=None) # DEBUG!
        return tiff_output_path

    def force_stop(self):
        print("Add force stop functionality")

    def update_output_path(self,new_path):
        self.output_path = new_path

class MainWindow(QMainWindow):
    # Define a signal that doesn't pass any data
    record_signal = pyqtSignal()

    def __init__(self, recordingThread: RecordingThread, writetodiskThread: WriteToDiskThread):
        super().__init__()
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.updateTimerLabel)
        # self.start_time = time.time()

        self.initUI()
        self.recordingThread = recordingThread
        self.writetodiskThread = writetodiskThread

        self.concatCount = 0
        self.recordCount = 0

        self.record = False

        # Assuming recordingThread are passed and stored as attributes
        if recordingThread:
            recordingThread.count_updated.connect(self.updateRecordCount)
            recordingThread.count_updated.connect(self.updateTimerLabel)
        

        # Status Bar setup
        self.statusBar = self.statusBar()  # Initialize the status bar
        self.statusBar.setStyleSheet("""
            QStatusBar {
                background-color: #A9A9A9; /* Dark Gray */
                color: white;
            }
        """)
        self.statusBar.showMessage("Record Count: 0")

    def initUI(self):
        self.setWindowTitle('Confocal Record To TIFF - Danish Islam   Last Updated: May 5th, 2024')
        self.resize(900, 300)

        # Create a central widget and a layout
        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout()

        # Add directory selection button
        self.dir_select_button = QPushButton("Select Output Directory", self)
        self.dir_select_button.clicked.connect(self.select_output_directory)
        layout.addWidget(self.dir_select_button)

        # Create and setup the record button
        self.record_button = QPushButton("Record", self)
        self.record_button.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)  # Make button stretch
        self.record_button.setFixedHeight(40)
        self.record_button.setCheckable(True)
        layout.addWidget(self.record_button)

        # Slider
        self.compression_slider = QSlider()
        self.compression_slider.setOrientation(1)  # Set slider orientation to vertical
        self.compression_slider.setMinimum(1)  # Set minimum value
        self.compression_slider.setMaximum(9)  # Set maximum value
        self.compression_slider.setValue(9)
        self.compression_display = QLabel('Compression Factor: 9')

        # Connect the buttons to their respective slots
        self.record_button.clicked.connect(self.record_button_clicked)

        # Add a QLabel for the timer
        self.timer_label = QLabel("00:00:00")
        self.timer_label.setAlignment(Qt.AlignCenter)
        self.timer_label.setMinimumHeight(30)  # Set minimum height
        self.timer_label.setMaximumHeight(40)  # Set maximum height
        layout.addWidget(self.timer_label)

        # Apply the layout to the central widget
        central_widget.setLayout(layout)
        style = """
                QWidget{
                    background: #262D37;
                }
                QLabel{
                    color: #fff;
                    font-size: 28px; /* Increase font size */
                    padding-top: 8px; /* Reduce extra space */
                    padding-bottom: 8px; /* Reduce extra space */
                }
                QPushButton{
                    color: white;
                    background: #0577a8;
                    border: 1px #DADADA solid;
                    padding: 5px 10px;
                    border-radius: 10px;
                    font-size: 9pt;
                    outline: none;
                }
                QPushButton:checked{
                    color: #0577a8;
                    background: white;
                    border: 1px #DADADA solid;
                    padding: 5px 10px;
                    border-radius: 10px;
                    font-size: 9pt;
                    outline: none;
                }
                QPushButton:pressed{
                    color: #0577a8;
                    background: white;
                    border: 1px #DADADA solid;
                    padding: 5px 10px;
                    border-radius: 10px;
                    font-size: 9pt;
                    outline: none;
                }
                """
        self.setStyleSheet(style)

        # Start the timer
        self.timer.start(1000)

    def record_button_clicked(self):
        self.record = not self.record
        # Make new folder
        if(self.record == True):
            folder_name = current_time = datetime.now()
            time_str = current_time.strftime("%m%d%Y_%H%M%S")

            new_folder = writetodiskThread.output_path + "\\" + "recording_" + time_str
            os.makedirs(new_folder) # DEBUG
            writetodiskThread.recording_path = new_folder
            print("\nNew folder at " + new_folder + "\n")

            # Make a new text file 
            text_file_name = "recording_log_" + time_str + ".txt"
            text_file_path = writetodiskThread.output_path + "\\" + text_file_name
            writetodiskThread.text_file_path = text_file_path
            with open(text_file_path, 'w') as file:
                file.write('(Frame count, (X coord, Y coord), Elapsed Time) \n')
            
            self.reset_counts()
            self.start_time = time.time()
        # Emit the signal when the record button is clicked
        self.record_signal.emit()

    def updateTimerLabel(self):
        if self.record:
            elapsed_time = time.time() - self.start_time
            hours, remainder = divmod(elapsed_time, 3600)
            minutes, seconds = divmod(remainder, 60)
            self.timer_label.setText(f"{int(hours):02}:{int(minutes):02}:{int(seconds):02}")

    def wipe_temp_button_clicked(self):
        print("Delete all images in the temp folder if left over before compression")
        temp_folder_path = "temp"
        try:
            for filename in os.listdir(temp_folder_path):
                file_path = os.path.join(temp_folder_path, filename)
                if os.path.isfile(file_path) or os.path.islink(file_path):
                    os.unlink(file_path)
                elif os.path.isdir(file_path):
                    shutil.rmtree(file_path)
            print("All temporary files have been deleted.")
        except Exception as e:
            print(f"Failed to delete files in {temp_folder_path} due to: {e}")

    def updateConcatCount(self, count):
        self.concatCount = count
        self.updateStatusBar()

    def updateRecordCount(self, count):
        self.recordCount = count
        self.updateStatusBar()

    def updateStatusBar(self):
        self.statusBar.showMessage(f"Record Count: {self.recordCount}")

    def reset_counts(self):
        self.statusBar.showMessage("Record Count: 0")
        self.recordingThread.count = 0
        self.writetodiskThread.count = 0

    def select_output_directory(self):
        dir_path = QFileDialog.getExistingDirectory(self, "Select Output Directory")
        if dir_path:
            self.output_directory = dir_path
            self.dir_select_button.setText(f"Output Directory: {self.output_directory}")
            self.writetodiskThread.update_output_path(self.output_directory)

if __name__ == "__main__":
    app = QApplication([])

    # global ref_time
    # ref_time = time.time()

    global core_wrap
    core_wrap = CoreWrapper()

    global live_stream_wrap
    live_stream_wrap = LiveStreamWrapper()

    # Check to make sure the livestream is open first, this makes image capture faster
    if live_stream_wrap.get_is_live_mode_on() == False:
        print("Turn on the livestream before running our program!")
        QMessageBox.critical(None,"Error","Turn on the livestream before running our program!")
        sys.exit()

    image_queue = Queue()
    file_queue = Queue()

    recordingThread = RecordingThread(image_queue)
    writetodiskThread = WriteToDiskThread(image_queue, file_queue)

    mainWindow = MainWindow(recordingThread, writetodiskThread)

    mainWindow.record_signal.connect(recordingThread.toggle_recording)
    mainWindow.record_signal.connect(writetodiskThread.toggle_recording)

    recordingThread.start()
    writetodiskThread.start()

    mainWindow.show()
    app.exec_()