from pycromanager import Core
import numpy as np
import pycromanager
import matplotlib.pyplot as plt
snapLiveManager = pycromanager.Studio().get_snap_live_manager()
import time

def imageGrab(snapLiveManager):
    s = time.time()
    image = snapLiveManager.snap(False)
    image = image.get(0)
    image = image.get_raw_pixels()
    image_array = np.array(image,dtype=np.uint8)
    image_array = np.reshape(image_array,(2048,2048))
    s2 = time.time()
    image_array = (image_array / image_array.max() * 255)
    e2 = time.time()
    # print("Normalize time: "+ str(e2-s2))
    e = time.time()
    print("Time: " + str(e-s))

    plt.imshow(image_array,cmap="gist_gray")
    plt.show()

while(True):
    imageGrab(snapLiveManager)
