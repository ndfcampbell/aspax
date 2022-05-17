import os

import pydicom
import numpy


src_loc = "C:/Users/amr62\Documents/Monitor/-10005/Baseline"
files = os.listdir(src_loc)

dcm = pydicom.read_file(os.path.join(src_loc,files[1]))
