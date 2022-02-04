import os
import shutil

from PyQt5 import QtWidgets
from PyQt5.QtWidgets import *
from PyQt5.QtGui import QIcon,QColor,QPalette,QFont,QPixmap,QPainter,QPen,QImage,QTransform,QPolygon,QBrush,\
    QPolygonF, QPalette, QGradient, QLinearGradient
from PyQt5.QtCore import *








import numpy as np



class TestWidget(QWidget):
    def __init__(self):
        super(TestWidget,self).__init__()

        self.layout = QVBoxLayout()
        self.button = QPushButton("set wd")
        self.layout.addWidget(self.button)
        self.line_edit = QLineEdit()
        self.layout.addWidget(self.line_edit)


        self.setLayout(self.layout)
        self.connect_methods()

    def set_wd(self):
        response = QFileDialog.getExistingDirectory(
            self,
            caption='Select a folder'
        )

        self.line_edit.setText(response)



    def connect_methods(self):
        self.button.clicked.connect(self.set_wd)




if __name__=='__main__':
    #main()
    # xray_record = XrayData(image_name='CPSA0045h2012.png',xray_id='CPSA0045',acquisition_date='2012')
    # xray_record.add_xray(image_name='CPSA0045h2019.png',xray_id='CPSA0045',acquisition_date='2019',
    #  save_loc='saved_data',
    #  organ_name='hand')
    #
    #
    # loaded_record = XrayData(image_name='CPSA0045h2012.png',xray_id='CPSA0045',acquisition_date='2012',
    #                          meta_loc=xray_record.save_loc)
    #
    """#
    dest_loc = '/media/adwaye/2tb/data/xray_data/aspax_studies'
    src_loc  = '/media/adwaye/2tb/data/xray_data/anonymised_backup/results/'
    ids      = find_unique_ids(src_loc)
    #study    = XrayStudy
    filename = '/media/adwaye/2tb/data/xray_data/anonymised_backup/results/29471_2000_hands.jpg'
    #study    = XrayStudy(filename=filename,save_loc=dest_loc)
    for id in ids:
        print(id)
        study     = XrayStudy(id,save_loc=dest_loc)
        study.load_xrays_from_loc(loc = src_loc)
    """
    import sys
    app = QApplication(sys.argv)
    w = TestWidget()
    w.show()
    sys.exit(app.exec_())
