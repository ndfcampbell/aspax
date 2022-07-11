import os

import pydicom
import numpy as np



def find_spacing_element(dicom_file,_print=False):
    """
    Iterates through the elements in dicom_file to find the element corresponding to the pixe spainc element
    :param dicom_file: a dicom file output of pydicom.readfile
    :return: a data element if pixel spacing data is found, none otherwise
    """
    pixel_elem = None
    for elements in dicom_file:
        vr = elements.VR
        if _print: print(elements)
        name =elements.name
        print(name)
        if "Spacing" in name:
            pixel_elem = elements
        elif "PixelSpacing" in name:
            pixel_elem = elements
        elif "ImagerPixelSpacing" in name:
            pixel_elem = elements


    if pixel_elem is not None:
        print(pixel_elem.name)
    else:
        print("no matches found for file")
    return pixel_elem

def extract_pixel_spacing(dicom_file):
    """
    tries to access ImagerPixelSpacing attribute of the dicom_file: if this is not present, then runs
    find_element_spacing to try to access the element corresponding the pixel imager spacing
    :param dicom_file: a dicom file output of pydicom.readfile
    :return: the imager spacing data if this is found, Nonetype otherwise
    """
    value = None
    try:
        value = dicom_file.ImagerPixelSpacing
        print("imager spacing worked")
    except AttributeError:
        pixel_elem = find_spacing_element(dicom_file)
        print(pixel_elem.name)
        if pixel_elem is not None:
            value = pixel_elem.value
    return value








if __name__=='__main__':
    top_loc = 'C:/Users/amr62/Documents/Monitor_aspax/'
    folders = [os.path.join(top_loc,f) for f in os.listdir(top_loc)]
    for loc in folders:
        if os.path.isdir(loc):
            files = os.listdir(loc)
            for f in files:
                if f.split('.')[-1]=='dcm':
                    dicom_file = pydicom.read_file(os.path.join(loc,f))
                    print("-----------------------------------------")
                    print(f)
                    value = extract_pixel_spacing(dicom_file)
                    print(value)
    # filename = 'C:/Users/amr62/Documents/Monitor_aspax/10001/Hand-DX-9300-42.dcm'
    # dicom_file = pydicom.read_file(filename)
    # elem = find_spacing_element(dicom_file)

