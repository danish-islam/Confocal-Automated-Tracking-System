import tifffile
import numpy as np
import os
import h5py
import time
import shutil
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QVBoxLayout, QFileDialog, QLabel, QSlider, QHBoxLayout
import math


class VideoHDF5App(QWidget):
    def __init__(self):
        super().__init__()

        self.init_ui()

    def init_ui(self):
        self.setWindowTitle('TIFF Folder to HDF5 Video Converter')
        self.resize(900, 300)

        # Create widgets
        self.folder_button = QPushButton('Select Folder')
        self.compression_label = QLabel('Compression Factor:')
        self.compression_slider = QSlider()
        self.compression_slider.setOrientation(1)  # Set slider orientation to vertical
        self.compression_slider.setMinimum(1)  # Set minimum value
        self.compression_slider.setMaximum(9)  # Set maximum value
        self.compression_display = QLabel('Compression Factor: 1')
        self.run_button = QPushButton('Run Function')
        self.progress_label = QLabel('Progress:  Time left:')

        # Connect button clicks to functions
        self.folder_button.clicked.connect(self.select_folder)
        self.run_button.clicked.connect(self.run_function)
        self.compression_slider.valueChanged.connect(self.update_compression_display)

        # Set up the layout
        layout = QVBoxLayout()
        layout.addWidget(self.folder_button)
        layout.addWidget(self.compression_label)
        layout.addWidget(self.compression_slider)
        layout.addWidget(self.compression_display)
        layout.addWidget(self.run_button)
        layout.addWidget(self.progress_label)

        self.setLayout(layout)
        style = """
                QWidget{
                    background: #262D37;
                }
                QLabel{
                    color: #fff;
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
                """
        self.setStyleSheet(style)

    def select_folder(self):
        folder_path = QFileDialog.getExistingDirectory(self, 'Select Folder', os.path.expanduser('~'))
        if folder_path:
            self.selected_folder = folder_path
            self.folder_button.setText(f'Selected Folder: {folder_path}')
        else:
            print("No folder selected.")

    def update_compression_display(self):
        compression_value = self.compression_slider.value()
        self.compression_display.setText(f'Compression Factor: {compression_value}')

    def run_function(self):
        # print(self.selected_folder)
        if hasattr(self, 'selected_folder'):
            compression_value = self.compression_slider.value()

            # Example output file path, adjust as needed
            hdf5_file_path = self.selected_folder + '/../' + 'output/video.h5'

            # Call the modified function with progress callback
            self.create_video_hdf5_with_progress(self.selected_folder, hdf5_file_path, compression_value)

    def create_video_hdf5_with_progress(self, tif_folder, hdf5_file_path, compression_value):

        # Find number of files in folder
        ls = os.listdir(tif_folder)
        num_files = len(ls)
        count = 0

        # Find out initial shape
        first_img = os.path.join(tif_folder, ls[1])
        tif_array = tifffile.imread(first_img)
        frame_shape = tif_array.shape

        output_directory = os.path.dirname(hdf5_file_path)
        if os.path.exists(output_directory):
            shutil.rmtree(output_directory)
        os.makedirs(output_directory)

        with h5py.File(hdf5_file_path, 'a') as hdf5_file:
            video_dataset = hdf5_file.require_dataset('video_frames', shape=(0, frame_shape[0], frame_shape[1]),
                                                      maxshape=(None, 2048, 2048), compression="gzip",
                                                      compression_opts=compression_value, chunks=(1, 1024, 2048), dtype='uint16')

            # Loop through all files in folder
            ls = os.listdir(tif_folder)
            for filename in ls:

                if (filename.endswith(('.tif', '.tiff')) == False):
                    count = count + 1
                    continue

                s = time.time()
                file_path = os.path.join(tif_folder, filename)
                tif_array = tifffile.imread(file_path)
                current_size = video_dataset.shape[0]
                video_dataset.resize(current_size + 1, axis=0)
                video_dataset[current_size, :, :] = tif_array
                e = time.time()
                time_elapsed = e - s
                print("Time taken: " + str(time_elapsed))

                approx_time_left = time_elapsed * (num_files - count)

                # Update progress in the GUI
                self.progress_label.setText("Progress: " + str(count) + "\\" + str(num_files) + " Time left: <" + str(
                    math.ceil(approx_time_left / 60)) + " minute(s)")
                count = count + 1
                QApplication.processEvents()  # Ensure GUI updates

            self.progress_label.setText("Progress: " + str(count) + "\\" + str(num_files) + " Time left: Done!")

        # Display HDF5 file contents
        with h5py.File(hdf5_file_path, 'r') as hdf5_file:

            print("\nInput: " + self.selected_folder)
            print("Output: " + hdf5_file_path +"\n")

            print("Contents of HDF5 file:")
            print("-----------------------")
            print("Attributes:")
            print(hdf5_file.attrs)
            print("\nDatasets:")
            for name, dataset in hdf5_file.items():
                print(f"Dataset: {name}")
                print(f"Shape: {dataset.shape}")
                print(f"Dtype: {dataset.dtype}")
                print(f"Compression: {dataset.compression}")
                print(f"Compression Options: {dataset.compression_opts}")


if __name__ == '__main__':
    app = QApplication([])
    window = VideoHDF5App()
    window.show()
    app.exec_()