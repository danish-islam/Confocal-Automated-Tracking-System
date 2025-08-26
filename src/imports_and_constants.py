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

microscope_online = True

# Dynamic loading of ti2_stage_wrapper (expects Ti2_Mic_Driver.dll and ti2_stage_wrapper.pyd in lib folder)
if microscope_online:
    parent_dir = os.getcwd()
    os.chdir(parent_dir + "/lib")

    pyd_path = os.path.abspath(os.path.join("ti2_stage_wrapper.pyd"))
    module_name = "ti2_stage_wrapper"
    sys.path.append(os.path.dirname(pyd_path))
    spec = importlib.util.spec_from_file_location(module_name, pyd_path)
    ti2_stage_wrapper = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = ti2_stage_wrapper
    spec.loader.exec_module(ti2_stage_wrapper)

    os.chdir(parent_dir)