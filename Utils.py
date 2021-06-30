from PyQt5.QtCore import (QByteArray, QDataStream, QFile, QFileInfo,
                          QIODevice, QPoint, QPointF, QRectF, Qt, QRect, QSize)
from PyQt5.QtGui import (QColor, QBrush, QPixmap, QPainter, QBitmap, QIcon, QFont, QPen)

import numpy as np
from os import listdir


def colorPixmap(pix, color):
    newPix = QPixmap(pix.size())
    newPix.fill(Qt.transparent)
    mask = pix.createMaskFromColor(QColor(0, 0, 0, 0), Qt.MaskInColor)
    p = QPainter(newPix)
    p.setRenderHint(QPainter.SmoothPixmapTransform)
    p.setRenderHint(QPainter.Antialiasing)

    p.setBackgroundMode(Qt.TransparentMode)
    p.setPen(color)
    p.drawPixmap(newPix.rect(), mask, pix.rect())
    p.end()
    return newPix


def _circle_to_poly(center, r, astep=10):
    i = 0
    points = []
    while i < np.pi * 2:
        points.append([np.math.cos(i) * r +  center[0], np.math.sin(i) * r + center[1]])
        i += np.math.radians(astep)

    return points


def _NC(rgb):
    return np.array([float(rgb.red()) / 255., float(rgb.green()) / 255., float(rgb.blue()) / 255.] )


def _QC(rgb):
    if np.max(rgb) <= 1:
        fact = 255
    else:
        fact = 1

    if len(rgb) == 3:
        alpha = 255
    elif len(rgb) == 4:
        alpha = int(rgb[3] * fact)

    return QColor(int(rgb[0] * fact),int(rgb[1] * fact),int(rgb[2] * fact), alpha)


def _QP(pos):
    return QPointF(pos[0], pos[1])


def _NP(point):
    return np.array([point.x(), point.y()])


def _getPictures(loc):
       x = listdir(loc)
       x = np.array(x)
       L = len(x)
       condtnarray = ['.bmp','.gif','.jpg','jpeg','.png','.pbm','.pgm',\
                    '.ppm','.xbm','.xpm','.tif']#use png for dicom
       Lc          = len(condtnarray)
       conds       = np.zeros((1,Lc))
       locarray    = np.zeros((1,1))
       
       for k in range(L):
           xval = x[k][-4:] #k=-th item in directory
           for i in range(Lc): #loop to check is the file is one of the
              #supporter types
              conds[0,i] = (xval==condtnarray[i])
           sconds = np.sum(np.array(conds))
           if( sconds >0 ):
              locarray = np.concatenate( (locarray,np.array([[k]]) )) #array that shows
           # where in x the supported files are
       
       #locarray.astype(np.int64)
       x = x[locarray[1:].astype(np.int64)] 
       return x
       #self.messageBox.setText(np.array2string(self.__images))
       #self.messageBox.setText(str(np.sum(conds)))



