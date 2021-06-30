import sys
import csv
import os
from pandas import DataFrame
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import *
from PyQt5.QtGui import QIcon,QColor,QPalette,QFont,QPixmap,QPainter,QPen,QImage,QTransform,QPolygon,QBrush,\
    QPolygonF
from PyQt5.QtCore import *
from pywidgets.qt5.GraphicsItems import InteractiveScene,PolylineItem,RectItem,CircleItem,SplineItem,RingItem,LayerItem
from pywidgets.qt5.DataModels import Polyline
from MyUI_MOD import ImageHandler
from MyUI_EX import MyView
import numpy as np
from math import sqrt
from PIL import Image


class LabelName(object):
    def __init__(self,xray_name,side_name,organ_name,suborgan_name):
        """

        :param xray_name: name of the xray
        :type xray_name: string
        :param side_name: name of the side 'R', 'L'
        :type side_name:  string
        :param organ_name: name of the main organ
        :type organ_name: string
        :param suborgan_name: name of the sub area within the organ
        :type suborgan_name:  string
        :return:
        :rtype:
        """
        if xray_name=='':
            self.xray_name = 'XX'
        else:
            self.xray_name     = xray_name

        if side_name=='':
            self.side_name = 'XX'
        else:
            self.side_name     = side_name

        if organ_name =='':
            self.organ_name = 'XX'
        else:
            self.organ_name    = organ_name
        if suborgan_name == '':
            self.suborgan_name  = 'XX'
        else:
            self.suborgan_name = suborgan_name

    def create_file_name(self):
        filename = make_file_name([self.xray_name,self.organ_name,self.suborgan_name,self.side_name])
        return filename


class AnnotationLabel(object):
    def __init__(self,xray_name,side_name,organ_name,suborgan_name,label_type):
        """
        :param xray_name: name of the xray image on which the annotation is made
        :type xray_name:  string
        :param side_name: name of the side 'R' or 'L'
        :type side_name:  string
        :param organ_name: name of the organ example feet or hands
        :type organ_name:  string
        :param suborgan_name: name of the area within the organ being measured
        :type suborgan_name: string
        :param label_type: name of the type of label
        :type label_type: string
        """
        if side_name is not None: assert side_name=='R' or side_name=='L'

        self.Label_Name = LabelName(xray_name,side_name,organ_name,suborgan_name)


        if label_type == '':
            self.label_type = 'XX'
        else:
            self.label_type = label_type


    def create_file_name(self):
        prefix = self.Label_Name.create_file_name()
        filename = make_file_name([prefix,self.label_type])

        return filename

    def save_annotation(self,cv,target_folder):
        filename = self.create_file_name()
        np.savetxt(os.path.join(target_folder,filename+'.txt'),cv)




class PsAScoreData(object):
    def __init__(self,score,xray_name,side_name,organ_name,suborgan_name,scoring_type,damage_type):
        """
        :param score: value of the score
        :type score:  float
        :param scoring_type:
        :type scoring_type:
        :param damage_type:
        :type damage_type:
        """
        self.label_name   = LabelName(xray_name,side_name,organ_name,suborgan_name)
        self.score        = score
        self.scoring_type = scoring_type
        self.damage_type  = damage_type
        self.xray_name    = xray_name

    def output_score_lib(self):
        mylib = {}
        mylib['XRay_id'] = self.label_name.xray_name
        mylib['Score']   = self.score
        mylib['Side']    = self.label_name.side_name
        mylib['Organ']   = self.label_name.organ_name
        mylib['SubOrgan'] = self.label_name.suborgan_name
        mylib['Scoring_technique'] = self.scoring_type
        mylib['Damage_type'] = self.damage_type
        return mylib




class PsAScoreDataFrame(object):
    def __init__(self):
        self.columns   = ['Scoring_technique','Damage_type','SubOrgan','Organ','Side','Score','XRay_id']
        self.dict      = dict.fromkeys(self.columns)

    def append_score(self,score):
        #todo: need to update this so that there is a list and the list gets updated
        """

        :param score:
        :type score: PsAScoreDataFrame
        :return:
        :rtype:
        """
        score_lib = score.output_score_lib()
        tempdict  = self.dict

        self.dict = {**tempdict,**score_lib}







def make_file_name(stringlist):
    filename = stringlist[0]
    for nm in stringlist[1:]:
        filename += '_'+nm
    return filename


if __name__=='__main__':
    score          = 1
    xray_name      = 'cpsa222'
    side_name      = 'R'
    organ_name     = 'Hands'
    suborgan_name  = 'MCP1'
    scoring_type   = 'Ratingen'
    damage_type    = 'Erosion'

    score_data      = PsAScoreData(score,xray_name,side_name,organ_name,suborgan_name,scoring_type,damage_type)
    score_data.output_score_lib()
    score_dataframe = PsAScoreDataFrame()
    score_dataframe.append_score(score_data)

    score          = 2
    xray_name      = 'cpsa223'
    side_name      = 'R'
    organ_name     = 'Hands'
    suborgan_name  = 'MCP1'
    scoring_type   = 'Ratingen'
    damage_type    = 'Erosion'

    score_data      = PsAScoreData(score,xray_name,side_name,organ_name,suborgan_name,scoring_type,damage_type)
    score_dataframe.append_score(score_data)