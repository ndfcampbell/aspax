import os
import sys

import numpy as np
from PyQt5 import QtGui
from PyQt5 import QtCore, QtWidgets
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt4agg import NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure
import cv2


class PlotWindow(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super(PlotWindow, self).__init__(parent)

        # a figure instance to plot on
        self.figure = Figure()

        # this is the Canvas Widget that displays the `figure`
        # it takes the `figure` instance as a parameter to __init__
        self.canvas = FigureCanvas(self.figure)

        # this is the Navigation widget
        # it takes the Canvas widget and a parent
        self.toolbar = NavigationToolbar(self.canvas, self)

        # Just some button connected to `plot` method
        self.button = QtWidgets.QPushButton('Plot')
        #self.button.clicked.connect(self.plot)

        # set the layout
        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(self.toolbar)
        layout.addWidget(self.canvas)
        layout.addWidget(self.button)
        self.setLayout(layout)
        self.ax = self.figure.add_subplot(111)

    def imshow(self,im):
        #self.ax = self.figure.add_subplot(111)
        self.ax.imshow(im,cmap='Greys_r')



    def plot(self,x,y):#todo: add the option to color and change the size etc, might have to pass **kwargs to imshow within
        ''' plot some random stuff '''
        # random data


        # create an axis


        # discards the old graph


        # plot data
        self.ax.plot(x,y, '-',color='lightgreen')

        # refresh canvas
        self.canvas.draw()




if __name__ == '__main__':
    rect_loc = 'C:/Users/amr62/Documents/aspax_studies_small/aspax_studies_small/27513/joint/1998/'
    poly_loc = 'C:/Users/amr62/Documents/aspax_studies_small/aspax_studies_small/27513/bone/1998/'
    im_loc   = 'C:/Users/amr62/Documents/aspax_studies_small/aspax_studies_small/27513/27513_1998_hands.JPG'
    im = cv2.imread(im_loc)
    rects = [os.path.join(rect_loc,f) for f in os.listdir(rect_loc)]
    polys = [os.path.join(poly_loc,f) for f in os.listdir(poly_loc)]



    app = QtWidgets.QApplication([])
    window = QtWidgets.QMainWindow()
    plotwidget = PlotWindow()
    layout = QtWidgets.QVBoxLayout()
    layout.addWidget(plotwidget)
    window.setCentralWidget(plotwidget)

    plotwidget.imshow(im)
    for rect in rects:
        x = np.loadtxt(rect)
        plotwidget.plot(np.append(x[:,0],x[0,0]),np.append(x[:,1],x[0,1]))

    for poly in polys:
        x = np.loadtxt(poly)
        plotwidget.plot(x[:,0],x[:,1])


    window.show()

    app.exec_()