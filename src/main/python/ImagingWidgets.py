
import time
from PyQt5.QtWidgets import QGraphicsView,QGraphicsScene,QWidget,QToolBar,QVBoxLayout,QAction
from PyQt5.QtGui import QColor,QPixmap
from PyQt5.QtCore import Qt
from GraphicsItems import PolylineItem,RectItem
from DataModels import Polyline, Rect
import numpy as np


from Utils import _NP


class MyView(QGraphicsView):

    # Function that controls mouse clicks - if right click, it sets the previous mouse positions (???), otherwise event
    def mousePressEvent(self, event):
        if event.button() == Qt.RightButton:  # If the click event on the button is right-click
            self.__prevMousePos = event.pos()  # Set the previous mouse position as the previous mouse position
        else:
            super(MyView, self).mousePressEvent(event)

    # Function that controls mouse movements -
    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.RightButton:
            offset = self.__prevMousePos - event.pos()  # Calculates the movements in offset variable
            self.__prevMousePos = event.pos()  # Saves current mouse position as new previous mouse position
            # Below translates difference in mouse positions to differences in scroll bars, implementing movement
            self.verticalScrollBar().setValue(self.verticalScrollBar().value() + offset.y())
            self.horizontalScrollBar().setValue(self.horizontalScrollBar().value() + offset.x())
        else:  # Otherwise, normal mouse behaviour with left click - inherited by super
            super(MyView, self).mouseMoveEvent(event)


class MyScene(QGraphicsScene):
    actual_distance_between_points = 0
    def __init__(self, parent=None):
        super(MyScene, self).__init__(parent)
        pixmap = QPixmap(100, 100)
        pixmap.fill(Qt.red)
        self.pixmap = self.addPixmap(pixmap)

        self.polyline_annotate_item = None
        self.rect_annotate_item     = None
        self.start                  = None
        self.end                    = None
        self.annotation_length      = 0
        self.list_of_undone_points  = []
        self.draw_poly_flag = False
        self.draw_rect_flag = False
        self.pressed = False

    def display_image(self,img):
        self.clear()
        self.pixmap = self.addPixmap(img)
        self.update()

    # Function to override the QGraphicsScene mouse press behaviour, conditional on what functionality is selected
    def mousePressEvent(self, event):
        items = self.items(event.scenePos())


        for item in items:
            if item is self.pixmap:
                self.update()
                coord = _NP(item.mapFromScene(event.scenePos()))  # Store the click coordinates in a list of lists
                self.start = self.end = coord
                # print(coord)

                if self.draw_poly_flag and event.modifiers() != Qt.ControlModifier: # If the measure distance
                    # functionality is active
                    if self.annotation_length == 0: # Draw and store first coordinate
                        polyline_annotate = Polyline(coord)
                        self.polyline_annotate_item = PolylineItem(polyline_annotate)
                        self.polyline_annotate_item.edge_color = QColor("#FF511C")
                        self.addItem(self.polyline_annotate_item)
                        self.annotation_length += 1
                    else:
                        self.polyline_annotate_item.model.addControlPoints(np.expand_dims(coord,axis=0))
                        self.annotation_length += 1
                if self.rect_annotate_item is not None and event.modifiers() != Qt.ControlModifier:
                    x1,y1,w,h=self.rect_annotate_item.model.x,self.rect_annotate_item.model.y,\
                            self.rect_annotate_item.model.width,self.rect_annotate_item.model.height
                    x2, y2 = x1+w, y1+h
                    x = coord[0]
                    y = coord[1]
                    if (x1 < x and x < x2):
                        if (y1 < y and y < y2):
                            self.pressed = True
                            self.start = coord
                            print(True)
                        else:
                            print(False)

        super(MyScene, self).mousePressEvent(event)

    def mouseMoveEvent(self, event):
        items = self.items(event.scenePos())

        for item in items:
            if item is self.pixmap:

                coord = _NP(item.mapFromScene(event.scenePos()))
                self.end = coord

                if self.pressed and self.rect_annotate_item is not None:
                    coord = _NP(item.mapFromScene(event.scenePos()))
                    print(coord)

                    dx = self.start[0]-self.rect_annotate_item.model.x
                    dy = self.start[1]-self.rect_annotate_item.model.y
                    self.start = coord
                    self.rect_annotate_item.model._shiftControlPts(dx,dy)
                    self.rect_annotate_item.update()
                    print(self.rect_annotate_item.model.control_points)
                    self.update()
        super(MyScene,self).mouseMoveEvent(event)
        self.update()
                # rect_model = Rect(x=self.start[0],y=self.start[0],width=width,height=height)
                # self.rect_annotate_item = RectItem(x=self.start[0],y=self.start[1],width=width,height=height)
                # self.addItem(self.rect_annotate_item)

    def mouseReleaseEvent(self,event):
        self.pressed = False
        items = self.items(event.scenePos())
        for item in items:
            if item is self.pixmap:
                width  = self.end[0]-self.start[0]
                height = self.end[1]-self.start[1]
                rect_model = Rect(x=self.start[0],y=self.start[0],width=width,height=height)
                if self.rect_annotate_item is None and self.draw_rect_flag:
                    self.rect_annotate_item = RectItem(x=self.start[0],y=self.start[1],width=width,height=height)
                    self.addItem(self.rect_annotate_item)
        super(MyScene,self).mouseMoveEvent(event)
        self.update()





    def clear_poly(self):
        if self.polyline_annotate_item is not None:
            self.removeItem(self.polyline_annotate_item)
            self.polyline_annotate_item=None
            self.annotation_length     = 0
        if self.rect_annotate_item is not None:
            self.removeItem(self.rect_annotate_item)
            self.rect_annotate_item=None
            self.start     = None
            self.end       = None

    def undo(self):
        if self.annotation_length>0:
            self.removeItem(self.polyline_annotate_item)


            time.sleep(0.1)
            control_points = self.polyline_annotate_item.model.control_points
            polyline_annotate = Polyline(control_points[:-1])
            self.polyline_annotate_item = PolylineItem(polyline_annotate)
            self.polyline_annotate_item.edge_color = QColor("#FF511C")
            self.addItem(self.polyline_annotate_item)
            self.annotation_length-=1



# Class to handle the x-ray image - including zooming, contrasts, annotating etc.
class ImageHandler(QWidget):

    def __init__(self,icon_library):
        super().__init__()
        self.scaling_factor = 1.1
        self._empty = True
        self.image_view = MyView()
        self.image_view.setMouseTracking(False)
        self.image_view.scale(0.55, 0.55)
        self.image_view.centerOn(0, 0)
        self.image_view.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.image_view.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.image_scene = MyScene()
        self.load_image('CPSA0019h2011.png')
        # self.load_image('johncena.jpg')
        self.layout = QVBoxLayout()
        self.image_view.setScene(self.image_scene)
        self.toolbar = ImagingToolbar(icon_library)
        self.layout.addWidget(self.toolbar)

        self.layout.addWidget(self.image_view)
        self.setLayout(self.layout)
        self.icons = icon_library
        self.activate_toolbar()

        #replace with a connect toolbar
        # Toolbar settings - guidance on https://www.learnpyqt.com/courses/start/actions-toolbars-menus/
    def activate_toolbar(self):
        self.toolbar.buttons['Zoom Out'].triggered.connect(self.zoom_out)
        self.toolbar.buttons['Zoom In'].triggered.connect(self.zoom_in)
        self.toolbar.buttons['Undo'].triggered.connect(self.image_scene.undo)
        self.toolbar.buttons['Clear Label'].triggered.connect(self.image_scene.clear_poly)
        self.toolbar.buttons['Draw Polyline'].setCheckable(1)
        self.toolbar.buttons['Draw Rectangle'].setCheckable(1)
        self.toolbar.buttons['Draw Polyline'].triggered.connect(self.toggle_action_states)
        self.toolbar.buttons['Draw Rectangle'].triggered.connect(self.toggle_action_states)

        #.triggered.connect(self.image_scene.clear_poly)
        # self.toolbar.buttons['Draw Rect'].triggered.connect(self.image_scene.clear_poly)

    def load_image(self, file_name):
        self.image_filename = file_name
        self.pixmap          = QPixmap()
        self.pixmap.load(file_name)

        self.get_image_dimensions()
        self.display_image(self.pixmap)

    def display_image(self, img):
        self.image_scene.clear()
        # w = img.size[0]
        self.image_scene.display_image(img)
        # w = 1000
        # h = 1000
        # self.image_view.fitInView(QRectF(0, 0, w, h), Qt.KeepAspectRatio)
        self.image_scene.update()



    def get_image_dimensions(self):
        pass
        # ImageHandler.image_width_pixels = ImageHandler.image.width()
        # ImageHandler.image_height_pixels = ImageHandler.image.height()
        # ImageHandler.image_width_mm = ImageHandler.image.widthMM()
        # ImageHandler.image_height_mm = ImageHandler.image.heightMM()


    def get_image(self):
        return self.image

    def get_image_scene(self):
        return self.image_scene

    def toggle_action_states(self):
        if self.toolbar.buttons['Draw Rectangle'].isChecked():
            self.toolbar.buttons['Draw Polyline'].setChecked(0)

        if self.toolbar.buttons['Draw Polyline'].isChecked():
            self.toolbar.buttons['Draw Rectangle'].setChecked(0)

        self.image_scene.draw_rect_flag = self.toolbar.buttons['Draw Rectangle'].isChecked()
        self.image_scene.draw_poly_flag = self.toolbar.buttons['Draw Polyline'].isChecked()

    # Function to zoom in
    def zoom_in(self):
        global zoom_tracker
        if zoom_tracker < 10:
            self.zoom_in_scaling_factor = self.scaling_factor
            self.image_view.scale(self.zoom_in_scaling_factor, self.zoom_in_scaling_factor)
            zoom_tracker = zoom_tracker * self.zoom_in_scaling_factor
            self.layout.addWidget(self.image_view)
            self.update()

    def zoom_out(self):
        global zoom_tracker
        if zoom_tracker > 0.3:
            self.zoom_out_scaling_factor = 1 / self.scaling_factor
            self.image_view.scale(self.zoom_out_scaling_factor, self.zoom_out_scaling_factor)
            zoom_tracker = zoom_tracker * self.zoom_out_scaling_factor
            self.layout.addWidget(self.image_view)
            self.update()


class ImagingToolbar(QToolBar):
    def __init__(self,icon_lib):
        super(ImagingToolbar,self).__init__()
        self.setStyleSheet("background-color: rgb(22,204,177);")
        # action_icon_names   = [os.path.join("icons",f) for f in ["draw_poly.png","draw_rect.png","zoom_out.png",
        #                                                     "zoom_in.png",
        #                                          "undo.png",
        #                               "redo.png",
        #                        "clear-icon-3.png"]]
        self.icons = icon_lib
        action_descriptions = ["Draw Polyline","Draw Rectangle","Zoom Out","Zoom In","Undo","Redo","Clear Label"]
        self.load_buttons()


    def load_buttons(self):
        # assert len(action_icon_names)==len(descriptions)
        self.buttons = {}
        # Create toolbar widgets, connect to actions and add to toolbar#
        for keys,val in self.icons.items():
            action_button = QAction(val,keys,self)
            self.addAction(action_button)
            self.buttons[keys] = action_button



# def main():
#     app = QApplication([])
#     window = QMainWindow()
#
#     my_frame_widget = ImageHandler()
#     layout = QVBoxLayout()
#     layout.addWidget(my_frame_widget)
#     window.setCentralWidget(my_frame_widget)
#     # layout.addWidget(QPushButton('3'))
#     window.show()
#     app.exec_()
#
#
# if __name__=='__main__':
#     main()