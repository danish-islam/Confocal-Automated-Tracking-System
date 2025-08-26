"""
This test file is written to test if stage movement
from the SDK is working properly.
"""
import sys
import os
import importlib.util
import time

parent_dir = os.getcwd()
print("Parent dir: ", parent_dir)
os.chdir(parent_dir + "/lib")

pyd_path = os.path.abspath(os.path.join("ti2_stage_wrapper.pyd"))
print(pyd_path)
module_name = "ti2_stage_wrapper"
sys.path.append(os.path.dirname(pyd_path))
spec = importlib.util.spec_from_file_location(module_name, pyd_path)
ti2_stage_wrapper = importlib.util.module_from_spec(spec)
sys.modules[module_name] = ti2_stage_wrapper
spec.loader.exec_module(ti2_stage_wrapper)

os.chdir(parent_dir)
print("Current dir: ", os.getcwd())

ti2_stage_wrapper.connectToMicroscope()

ti2_stage_wrapper.runXYVectorialTransfer(1,5,1,0)
time.sleep(0.95)

ti2_stage_wrapper.runXYVectorialTransfer(1,0,1,0)