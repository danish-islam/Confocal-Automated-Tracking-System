"""
This test file is written to test if stage movement
from the SDK is working properly.
"""
import sys
import os
import importlib.util
import time

pyd_path = os.path.abspath(os.path.join("..", "lib", "ti2_stage_wrapper.pyd"))
module_name = "ti2_stage_wrapper"
sys.path.append(os.path.dirname(pyd_path))
spec = importlib.util.spec_from_file_location(module_name, pyd_path)
module = importlib.util.module_from_spec(spec)
sys.modules[module_name] = module
spec.loader.exec_module(module)

module.connectToMicroscope()

module.runXYVectorialTransfer(1,5,1,0)
time.sleep(0.95)

module.runXYVectorialTransfer(1,0,1,0)