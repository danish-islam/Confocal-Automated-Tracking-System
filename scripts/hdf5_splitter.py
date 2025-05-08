""" 
A command line program made by Danish Islam meant for dividing HDF5 videos into smaller files.
Will help lab members in uploading videos of manageable lengths to CaTracker.

Current version is as of 5 PM on May 18th, 2024
"""

import h5py
import time
import numpy as np
import sys
import ast
import os
import threading

# ================================
# Video processing functions
# ================================

def load_video(hdf5_file_path, dataset_name):
    hdf5_file = h5py.File(hdf5_file_path, 'r')
    video = hdf5_file[dataset_name]
    num_frames = video.shape[0]
    total_memory_mb = video.nbytes / (1024 ** 3)  # Convert bytes to megabytes
    print("Loaded in the video. It has " + str(num_frames) + " frames and takes " + str(round(total_memory_mb,3)) + " GB w/o compression")
    return video

def parse_input(input_string):
    tuple_list = []
    tmp = input_string.split(" ")
    for tuple_string in tmp:
        tuple_list.append(ast.literal_eval(tuple_string))
    return tuple_list

def split_video(video,start_index, end_index):
    return video[start_index:end_index+1,:,:] 

def save_cropped_video(cropped_video, output_path):
    with h5py.File(output_path, 'w') as file:
        # file.create_dataset('video_frames', data=cropped_video)
        file.create_dataset('video_frames', data=cropped_video, compression='gzip', compression_opts=9, chunks=(1, 1024, 2048), dtype='uint8')

# ================================
# Animations
# ================================

def spinner_animation(stop_spinner):
    spinner = ['|     ', '/     ', '-     ', '\\     ',
               '||    ', '//    ', '--    ', '\\\\    ',
               '|||   ', '///   ', '---   ', '\\\\\\   ',
               '||||  ', '////  ', '----  ', '\\\\\\\\  ',
               '||||| ', '///// ', '----- ', '\\\\\\\\\\ ',
               '||||||', '//////', '------', '\\\\\\\\\\\\',
               '||||||', '||||||', '||||| ', '||||  ', '|||   ', '||    ', '|     '
            ]
    idx = 0
    while not stop_spinner.is_set():
        sys.stdout.write('\b\b\b\b\b\b')  # Move cursor back one position
        sys.stdout.write(spinner[idx % len(spinner)])  # Write the new spinner character
        sys.stdout.flush()
        idx += 1
        time.sleep(0.1)

def start_spinner():
    stop_spinner = threading.Event()
    spinner_thread = threading.Thread(target=spinner_animation, args=(stop_spinner,))
    spinner_thread.start()
    return stop_spinner

def stop_spinner(stop_spinner):
    stop_spinner.set()

# ================================
# Main Function
# ================================

if __name__ == "__main__":

    print("\n======================================")
    print("Zhen Lab HDF5 Video Splitter 🔬🥽")
    print("A command line program by Danish Islam")

    slash = None
    if(os.name == "nt"):
        slash = "\\"
        print("Detected you are on a Windows environment")
    else:
        slash = "/"
        print("Detected you are on a MacOS/Linux environment")
    print("======================================\n")

    # Step 1: Take in path argument
    print("1. Please input a valid path to the HDF5 video you want to divide up.")
    path = input("Enter here: ") 

    if not os.path.exists(path):
        print("Enter a valid path")
        sys.exit(1)
    if path.split(".")[1] != "h5":
        print("Enter a valid HDF5 file")
        sys.exit(1)
    print("Confirmed to be a valid HDF5 file existing on your computer\n")

    # Step 2: Load in the video
    print("2. Loading in your video, please wait...")
    video = load_video(path, "video_frames") 
    print()

    # Step 3: Take tuples from user
    print("3. Please enter a list of tuples representing the coverage of each sub video e.g. (1,5) (6,10)")
    string_input = input("Enter here: ") # DEBUG, UNCOMMENT LATER
    tuple_list = parse_input(string_input) # Function completed

    # Step 4: Create sub-videos
    print("\n4. Generating the sub-videos in the same directory as the input path")
    for i, tup in enumerate(tuple_list):

        print("Creating a sub-video from frame " + str(tup[0]) + " to " + str(tup[1]) + "...        ", end="", flush=True)
        spinner_stop_event = start_spinner()

        s = time.time()
        sub_video = split_video(video, tup[0], tup[1]) # Complete function
        output_path = os.path.dirname(path) + slash + os.path.basename(path).split(".")[0] + "_subvideo" + str(tup[0]) + "to" + str(tup[1]) + ".h5"
        save_cropped_video(sub_video,output_path) # DEBUG, UNCOMMENT LATER
        stop_spinner(spinner_stop_event)
        e = time.time() 

        print("\rCreated a sub-video from frame " + str(tup[0]) + " to " + str(tup[1]) + "!" + " Took " + str(round(e-s,2)) + " seconds.")
    print()


