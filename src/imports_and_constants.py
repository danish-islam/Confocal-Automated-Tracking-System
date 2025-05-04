# ---- All necessary imports ----#

import numpy as np
import sys
import cv2
import time
from PyQt5.QtWidgets import QApplication, QLabel, QVBoxLayout, QHBoxLayout, QWidget, QPushButton, QSplashScreen, QMessageBox
from PyQt5.QtCore import QThread, pyqtSignal, pyqtSlot, Qt, QTimer
from PyQt5.QtGui import QImage, QPixmap, QFont
import matplotlib.pyplot as plt
import threading
import sys
import os
from scipy.ndimage import binary_hit_or_miss
import scipy.ndimage
import importlib.util

import pycromanager
from pycromanager import Core

# ---- Set to True if attached to microscope, False for debugging ----#

Microscope = False
if Microscope:
    # Change this to dynamic loading
    # import my_module # Only with Microscope on
    pyd_path = os.path.abspath(os.path.join("..", "lib", "my_module.pyd"))
    module_name = "my_module"
    sys.path.append(os.path.dirname(pyd_path))
    spec = importlib.util.spec_from_file_location(module_name, pyd_path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)