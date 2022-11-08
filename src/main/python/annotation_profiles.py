import time, os
from PyQt5.QtWidgets import QGraphicsView,QGraphicsScene,QWidget,QToolBar,QVBoxLayout,QAction, QButtonGroup, \
    QActionGroup, QApplication, QSlider, QMainWindow, QHBoxLayout, QLabel, QComboBox, QCheckBox, QPushButton, QFrame,\
    QTabWidget,QMessageBox, QLineEdit,QGridLayout

from PyQt5.QtGui import QColor,QPixmap, QFont
from PyQt5.QtCore import Qt
from graphics_items import PolylineItem,RectItem,BaseRectItem, DEFAULT_HANDLE_SIZE, DEFAULT_EDGE_WIDTH
from data_models import Polyline, Rect
import numpy as np
from menu_widgets import load_csv, save_csv


from utils import _NP


class AnnotationProfiler(object):
    """Base class to create a set of annotation instructions for annotators to annotate

    """
    def __init__(self):

        super(AnnotationProfiler,self).__init__()
        self.label_names=None
        self.graphics_type = None

    def load_model(self,save_loc):
        """
        loads the predictive model metadata from save loc which it uses to predict the loctaions of the labels.

        :param save_loc:
        :return:
        """
        pass

    def load_data(self):
        pass


class HandJointAnnotationProfiler(object):
    """Annotation exercise for joints of the hand. It iteratively generates names of joints to annotate next once the previous one was annotated. Currently unused

    :param output_loc:
    :type output_loc:
    """
    def __init__(self,output_loc):

        super(HandJointAnnotationProfiler,self).__init__()

        label_names = []
        for k in ['5','4','3','2']:
            for joint in ['DIP','PIP','MCP','CMC']:
                label_names += ['HANDS_L_' + joint + k]

        label_names += ['HANDS_L_IP1','HANDS_L_MCP1','HANDS_L_CMC1']
        label_names += ['HANDS_R_IP1','HANDS_R_MCP1','HANDS_R_CMC1']
        for k in ['2','3','4','5']:
            for joint in ['DIP','PIP','MCP','CMC']:
                label_names += ['HANDS_L_' + joint + k]
        self.label_names = label_names
        self.graphics_type = BaseRectItem
        self.organ_name = 'joint'
        self.output_loc = output_loc
        self.load_data()
        self.current_index = 0
        self.annot_dict = {}


    def load_data(self):
        """
        loads the raw data on which this is made

        :return:
        """
        pass
        #todo: create a predictive model that learns on the go: simpest is mean of gaussian
        pass
        # if os.path.isfile(os.path.join(self.output_loc,'raw_data.csv')):
        #     self.raw_data = load_csv(os.path.join(self.output_loc,'raw_data.csv'))
        # else:
        #     print("no raw data found")


    def load_model(self):
        """
        loads
        :return:
        """
        if os.path.isfile(os.path.join(self.output_loc,'raw_data.csv')):
            self.raw_data = load_csv(os.path.join(self.output_loc,'raw_data.csv'))
        else:
            print("no model found")


    def add_label(self,study_id,label_name):
        """
        stores the coordinates corresponding to label with label_name
        :param study_id:
        :param label_name:
        :return:
        """
        pass


    def init_next_label(self):
        pass


    def __call__(self):
        if self.current_index<len(self.label_names):
            current_label = self.label_names[self.current_index]
            # rect_annotate_item = RectItem(x=1000,y=1000,width=220,height=220)
            xmid=1000
            ymid=1000
            patch_size = 220
            self.annot_dict[current_label] = np.array([[xmid + patch_size//2,ymid - patch_size//2],
                                                [xmid - patch_size//2,ymid - patch_size//2],
                                                [xmid - patch_size//2,ymid + patch_size//2],
                                                [xmid + patch_size//2,ymid + patch_size//2]
                                                ])
            self.current_index+=1







if __name__=='__main__':
    label_names = []
    for k in ['5','4','3','2']:
        for joint in ['DIP','PIP','MCP','CMC']:

            label_names +=['HANDS_L_'+joint+k]

    label_names +=['HANDS_L_IP1','HANDS_L_MCP1','HANDS_L_CMC1']
    label_names += ['HANDS_R_IP1','HANDS_R_MCP1','HANDS_R_CMC1']
    for k in ['2','3','4','5']:
        for joint in ['DIP','PIP','MCP','CMC']:

            label_names +=['HANDS_L_'+joint+k]