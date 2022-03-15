
import time, os
from PyQt5.QtWidgets import QGraphicsView,QGraphicsScene,QWidget,QToolBar,QVBoxLayout,QAction, QButtonGroup, \
    QActionGroup, QApplication, QSlider, QMainWindow, QHBoxLayout, QLabel, QComboBox, QCheckBox, QPushButton, QFrame,QTabWidget,QMessageBox, QLineEdit

from PyQt5.QtGui import QColor,QPixmap, QFont
from PyQt5.QtCore import Qt
from GraphicsItems import PolylineItem,RectItem, DEFAULT_HANDLE_SIZE, DEFAULT_EDGE_WIDTH
from DataModels import Polyline, Rect
import numpy as np
from MenuWidgets import Slider


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
        self.edge_width = DEFAULT_EDGE_WIDTH
        self.handle_size = DEFAULT_HANDLE_SIZE

    def display_image(self,img):
        self.clear()
        self.rect_annotate_item = None
        self.polyline_annotate_item = None
        self.annotation_length = 0
        self.start = None
        self.end = None
        self.pixmap = self.addPixmap(img)
        self.update()


    def add_polyline(self,control_points):
        polyline_annotate = Polyline(control_points)
        self.polyline_annotate_item = PolylineItem(polyline_annotate, edge_width=self.edge_width,
                                                   handle_size=self.handle_size)
        self.polyline_annotate_item.edge_color = QColor("#FF511C")

        self.addItem(self.polyline_annotate_item)
        print(len(control_points))
        self.annotation_length  = len(control_points)

    def add_rectItem(self,x,y,w,h):
        self.rect_annotate_item = RectItem(x=x, y=y, width=w, height=h)
        self.addItem(self.rect_annotate_item)
        self.addItem(self.rect_annotate_item.rotate_handle)


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
                        # polyline_annotate = Polyline(coord)
                        # self.polyline_annotate_item = PolylineItem(polyline_annotate,edge_width=self.edge_width,handle_size=self.handle_size)
                        # self.polyline_annotate_item.edge_color = QColor("#FF511C")
                        #
                        #
                        # self.addItem(self.polyline_annotate_item)
                        self.add_polyline(coord)

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


                    dx = self.start[0]-self.rect_annotate_item.model.x
                    dy = self.start[1]-self.rect_annotate_item.model.y
                    self.start = coord
                    self.rect_annotate_item.model._shiftControlPts(dx,dy)
                    self.rect_annotate_item.update()
                    print('control points= ')
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
                    self.add_rectItem(x=self.start[0],y=self.start[1],w=width,h=height)
                    # self.rect_annotate_item = RectItem(x=self.start[0],y=self.start[1],width=width,height=height)
                    # self.addItem(self.rect_annotate_item)
                    # self.addItem(self.rect_annotate_item.rotate_handle)
        super(MyScene,self).mouseMoveEvent(event)
        self.update()





    def clear_poly(self):
        if self.polyline_annotate_item is not None:
            self.removeItem(self.polyline_annotate_item)
            self.polyline_annotate_item=None
            self.annotation_length     = 0
        if self.rect_annotate_item is not None:
            self.removeItem(self.rect_annotate_item)
            self.removeItem(self.rect_annotate_item.rotate_handle)
            self.rect_annotate_item=None
            self.start     = None
            self.end       = None

    def undo(self):
        if self.annotation_length>0:
            self.removeItem(self.polyline_annotate_item)


            time.sleep(0.1)
            control_points = self.polyline_annotate_item.model.control_points
            polyline_annotate = Polyline(control_points[:-1])
            self.polyline_annotate_item = PolylineItem(polyline_annotate,edge_width=self.edge_width,
                                                   handle_size=self.handle_size)
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
        self.image_quality_flag = True
        self.toolbar = ImagingToolbar(icon_library)
        self.layout.addWidget(self.toolbar)

        self.annotation_options = AnnotationModelOptions()
        horizontal_dock = QHBoxLayout()
        horizontal_dock.addWidget(self.annotation_options,50)
        horizontal_widget = QWidget()
        horizontal_widget.setMinimumSize(800,200)
        horizontal_widget.setMaximumSize(800,200)

        horizontal_widget.setLayout(horizontal_dock)
        self.layout.addWidget(horizontal_widget)
        self.layout.addWidget(self.image_view)
        self.setLayout(self.layout)
        self.icons = icon_library
        self.activate_toolbar()
        self.zoom_tracker  = 1.0
        self.zoom_out_scaling_factor = 1.0

        #replace with a connect toolbar
        # Toolbar settings - guidance on https://www.learnpyqt.com/courses/start/actions-toolbars-menus/
    def activate_toolbar(self):
        self.toolbar.buttons['Zoom Out'].triggered.connect(self.zoom_out)
        self.toolbar.buttons['Zoom In'].triggered.connect(self.zoom_in)
        self.toolbar.buttons['Undo'].triggered.connect(self.image_scene.undo)
        self.toolbar.buttons['Clear Label'].triggered.connect(self.image_scene.clear_poly)

        draw_group = QActionGroup(self)
        draw_group.setExclusive(True)
        self.toolbar.buttons['Draw Polyline'].setCheckable(1)
        self.toolbar.buttons['Draw Rectangle'].setCheckable(1)
        draw_group.addAction(self.toolbar.buttons['Draw Rectangle'])
        draw_group.addAction(self.toolbar.buttons['Draw Polyline'])

        like_dislike_group = QActionGroup(self)
        like_dislike_group.setExclusive(True)
        self.toolbar.buttons['Bad Image Quality'].setCheckable(1)
        self.toolbar.buttons['Good Image Quality'].setCheckable(1)
        like_dislike_group.addAction(self.toolbar.buttons['Bad Image Quality'])
        like_dislike_group.addAction(self.toolbar.buttons['Good Image Quality'])
        self.toolbar.buttons['Draw Polyline'].triggered.connect(self.toggle_action_states)
        self.toolbar.buttons['Draw Rectangle'].triggered.connect(self.toggle_action_states)
        for key,val in self.annotation_options.score_sliders.items():
            #val.sliderMoved[int].connect(self.save_slider_value())
            val.valueChanged[int].connect(self.update_annotation_dimensions)

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

    def update_annotation_dimensions(self):



        size_dict = self.annotation_options.get_slider_value()
        self.image_scene.handle_size=size_dict['Dot Size']
        self.image_scene.edge_width = size_dict['Line Width']

        # self.image_scene.removeItem(self.image_scene.polyline_annotate_item)
        # qt5G.DEFAULT_HANDLE_SIZE = scala*maxSize
        # self.pLineItem = Pol	ylineItem(self.pLine,handle_size=100)
        #
        if self.image_scene.polyline_annotate_item is not None:
            self.image_scene.polyline_annotate_item.prepareGeometryChange()
            self.image_scene.polyline_annotate_item.handle_size = int(float(size_dict['Dot Size']))
            self.image_scene.polyline_annotate_item.edge_width  = int(float(size_dict['Line Width']))
            self.image_scene.polyline_annotate_item.model.update()
            # self.image_scene.polyline_annotate_item.update()
            self.image_scene.update()
        # self.image_scene.addItem(self.image_scene.polyline_annotate_item)
        # self.errorBox.setText(str(self.pLineItem.handle_size))




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
        # if self.toolbar.buttons['Draw Rectangle'].isChecked():
        #     self.toolbar.buttons['Draw Polyline'].setChecked(0)
        #
        # if self.toolbar.buttons['Draw Polyline'].isChecked():
        #     self.toolbar.buttons['Draw Rectangle'].setChecked(0)
        #
        # if self.toolbar.buttons['Good Image Quality'].isChecked():
        #     self.toolbar.buttons['Bad Image Quality'].setChecked(0)
        #
        # if self.toolbar.buttons['Bad Image Quality'].isChecked():
        #     self.toolbar.buttons['Good Image Quality'].setChecked(0)


        self.image_scene.draw_rect_flag = self.toolbar.buttons['Draw Rectangle'].isChecked()
        self.image_scene.draw_poly_flag = self.toolbar.buttons['Draw Polyline'].isChecked()
        self.image_quality_flag         = self.toolbar.buttons['Good Image Quality'].isChecked()

    # Function to zoom in
    def zoom_in(self):

        if self.zoom_tracker < 10:
            self.zoom_in_scaling_factor = self.scaling_factor
            self.image_view.scale(self.zoom_in_scaling_factor, self.zoom_in_scaling_factor)
            self.zoom_tracker = self.zoom_tracker * self.zoom_in_scaling_factor
            self.layout.addWidget(self.image_view)
            self.update()

    def zoom_out(self):

        if self.zoom_tracker > 0.3:
            self.zoom_out_scaling_factor = 1 / self.scaling_factor
            self.image_view.scale(self.zoom_out_scaling_factor, self.zoom_out_scaling_factor)
            self.zoom_tracker = self.zoom_tracker * self.zoom_out_scaling_factor
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
        # Create toolbar widgets, connect to actions and add to toolbar#set
        for keys,val in self.icons.items():
            action_button = QAction(val,keys,self)
            self.addAction(action_button)
            self.buttons[keys] = action_button

class AnnotationModelOptions(QWidget):
    def __init__(self,name='Score',profile={}):



        super(AnnotationModelOptions,self).__init__()
        self.layout = QHBoxLayout()
        self.init()


    def init(self):

        self.init_score_slider() #initialises the score sliders for dsicrete scales
        self.init_select_polylines()
        self.setLayout(self.layout)


    def init_score_slider(self):
        self.score_slider_layout = score_sliders(score_name="Annotation Model",damage_types=["Dot Size","Line Width"],
                                            damage_ranges=[(1,10),(1,10)])
        self.layout.addLayout(self.score_slider_layout)
        self.score_sliders = self.score_slider_layout.sliders
        self.score_sliders['Line Width'].setValue(DEFAULT_EDGE_WIDTH)
        # self.score_sliders['Line Width'].seMinimumSize(100,30)
        self.score_sliders['Dot Size'].setValue(DEFAULT_HANDLE_SIZE)
        # for key,val in self.score_sliders.items():
        #     #val.sliderMoved[int].connect(self.save_slider_value())
        #     val.valueChanged[int].connect(self.get_slider_value)

    def init_select_polylines(self):
        self.selection_layout = QVBoxLayout()
        layout1 = QHBoxLayout()
        polyline_label = QLabel("Polylines")
        polyline_label.setMaximumSize(60, 30)
        polyline_label.setMinimumSize(60, 30)
        self.polyline_dropdown = QComboBox()
        polyline_box_label = QLabel("Display Polys")
        polyline_box_label.setMaximumSize(90,30)
        polyline_box_label.setMinimumSize(90, 30)
        self.display_polylines_box = QCheckBox()
        layout1.addWidget(polyline_label)
        layout1.addWidget(self.polyline_dropdown)
        layout1.addWidget(polyline_box_label)
        layout1.addWidget(self.display_polylines_box)


        self.overwrite_poly_button = QPushButton("Overwrite")
        self.delete_poly_button = QPushButton("Delete")
        # self.poly_loc_line_edit = QLineEdit()
        layout2 = QHBoxLayout()
        layout2.addWidget(self.overwrite_poly_button)
        layout2.addWidget(self.delete_poly_button)
        # layout1.addWidget(self.overwrite_poly_button)

        layout3 = QHBoxLayout()
        rectItem_label = QLabel("Rect-Items")
        rectItem_label.setMaximumSize(60,30)
        rectItem_label.setMinimumSize(60, 30)
        self.rectItem_dropdown = QComboBox()
        rectItem_box_label = QLabel("Display Rectangles")
        rectItem_box_label.setMaximumSize(90,30)
        rectItem_box_label.setMinimumSize(90, 30)
        self.display_rectItem_box = QCheckBox()
        layout3.addWidget(rectItem_label)
        layout3.addWidget(self.rectItem_dropdown)
        layout3.addWidget(rectItem_box_label)
        layout3.addWidget(self.display_rectItem_box)

        self.overwrite_rect_button = QPushButton("Overwrite")
        self.delete_rect_button = QPushButton("Delete")
        layout4 = QHBoxLayout()
        layout4.addWidget(self.overwrite_rect_button)
        layout4.addWidget(self.delete_rect_button)

        widget1 =  QWidget()
        layout1.setContentsMargins(0,0,0,0)
        widget1.setLayout(layout1)

        widget2 = QWidget()
        widget2.setLayout(layout2)

        widget3 =  QWidget()
        widget3.setLayout(layout3)

        widget4 = QWidget()
        widget4.setLayout(layout4)

        layout_poly = QVBoxLayout()
        layout_poly.addWidget(widget1)
        layout_poly.addWidget(widget2)
        widget_poly = QFrame()
        widget_poly.setFrameStyle(QFrame.Box)
        widget_poly.setContentsMargins(0,0,0,0)
        widget_poly.setLayout(layout_poly)


        layout_rect = QVBoxLayout()
        layout_rect.addWidget(widget3)
        layout_rect.addWidget(widget4)
        widget_rect = QFrame()
        widget_rect.setFrameStyle(QFrame.Box)
        widget_rect.setContentsMargins(0,0,0,0)
        widget_rect.setLayout(layout_rect)

        # widget_poly.setStyleSheet("border: 1px solid black; margin: 0px; padding: 0px;")





        tabs = QTabWidget()
        # tabs.setMinimumWidth(1000)
        # tabs.setMaximumWidth(1000)
        tabs.addTab(widget_poly,'Polylines')
        tabs.addTab(widget_rect,'Rectangle')
        self.selection_layout.addWidget(tabs)
        # self.selection_layout.addWidget(widget1)
        # self.selection_layout.addWidget(widget2)
        # self.selection_layout.addWidget(widget_poly)
        # self.selection_layout.addWidget(widget3)
        # self.selection_layout.addWidget(widget4)
        self.selection_layout.setContentsMargins(0,0,0,0)
        self.layout.addLayout(self.selection_layout)
        self.delete_poly_button.clicked.connect(self.delete_selected_poly)


    def delete_selected_poly(self):
        annotation_name = self.polyline_dropdown.currentText()
        # print(annotation_name)

        annotation_path = os.path.join("", annotation_name+'.txt')
        # popupWindow = QMessageBox.question(self, 'Warning!',
        #                                         "Are you sure you want to delete "+annotation_name+"?",QMessageBox.No,
        #                                         QMessageBox.Ok)
        qm = QMessageBox
        ret = qm.question(self, '', "Are you sure to reset all the values?", qm.Yes | qm.No)
        if  ret == qm.Yes:
            print("deleting " +annotation_path)
        else:
            print("keeping " + annotation_path)


    def get_slider_value(self):
        my_dict  = self.score_slider_layout.get_slider_values()


        return my_dict




class score_sliders(QVBoxLayout):
    """
    For discrete scores
    """
    def __init__(self,score_name='Ratingen',damage_types=['Destruction','Proliferation'],damage_ranges=[(0,5),(0,5)],
                 opt_kwargs={}):
        super(score_sliders,self).__init__()
        self.opt_kwargs = opt_kwargs
        self.font_header = QFont('Android Roboto', 15)
        self.font_subheader = QFont('Android Roboto', 13)
        self.font_text = QFont('Android Roboto', 10)
        self.font_button = QFont('Android Roboto', 11)
        self.score_name    = score_name
        self.damage_types  = damage_types
        self.damage_ranges = damage_ranges
        self.sliders       = {}
        self.init_sliders()

    def init_sliders(self):
        min_label_width = self.opt_kwargs.pop('label_minimum_width',110)
        tick_spacing    = self.opt_kwargs.pop('tick_spacing',30)
        slider_gap      = self.opt_kwargs.pop('slider_gap',130)
        for damage,rng in zip(self.damage_types,self.damage_ranges):
            layout = QHBoxLayout()
            label  = QLabel(damage)
            label.setFont(self.font_text)
            label.setMinimumWidth(min_label_width)
            layout.addWidget(label)

            slider_layout = QVBoxLayout()
            score_slider   = Slider()
            score_slider.setStyleSheet("QSlider::handle:horizontal {background-color: #16CCB1;}")
            score_slider.setOrientation(Qt.Horizontal)
            score_slider.setRange(rng[0],rng[1])
            score_slider.setTickInterval(1)
            score_slider.setTickPosition(QSlider.TicksBelow)
            slider_layout.addWidget(score_slider)


            slider_label_layout  = QHBoxLayout()
            scores = np.arange(rng[0],rng[1]+1)
            for score in scores:
                slider_label_layout.addWidget(QLabel(str(score)))
                slider_label_layout.setSpacing(tick_spacing)
            slider_layout.addLayout(slider_label_layout)
            layout.addLayout(slider_layout)
            self.sliders[damage] = score_slider
            self.addLayout(layout)


    def reinit_values(self):
        for keys,val in self.sliders.items():
            val.setValue(0)

    def print_slider_values(self):
        for keys,val in self.sliders.items():
            print(val.value())

    def get_slider_values(self):
        mydict = {}
        for keys, val in self.sliders.items():
            mydict[keys]=val.value()
        print(mydict)
        return mydict

def main():
    app = QApplication([])
    window = QMainWindow()

    my_frame_widget = AnnotationModelOptions()
    layout = QVBoxLayout()
    layout.addWidget(my_frame_widget)
    window.setCentralWidget(my_frame_widget)
    # layout.addWidget(QPushButton('3'))
    window.show()
    app.exec_()


if __name__=='__main__':
    main()