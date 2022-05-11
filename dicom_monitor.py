import os

import pydicom
import numpy


src_loc = "/home/adwaye/Documents/Monitor/-10001/Baseline"
files = os.listdir(src_loc)

dcm = pydicom.read_file(os.path.join(src_loc,files[1]))
