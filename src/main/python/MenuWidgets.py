import os
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import *
from PyQt5.QtGui import QIcon,QColor,QPalette,QFont,QPixmap,QPainter,QPen,QImage,QTransform,QPolygon,QBrush,\
    QPolygonF
from PyQt5.QtCore import *

import numpy as np

import csv
import pandas as pd




# from DataUtils import *





class distance_menu_widget(QWidget):
    def __init__(self,name='Distance',joint_list="config/joint_list.txt"):
        super(distance_menu_widget,self).__init__()
        self.name = name
        self.font_header = QFont('Android Roboto', 15)
        self.font_subheader = QFont('Android Roboto', 13)
        self.font_text = QFont('Android Roboto', 10)
        self.font_button = QFont('Android Roboto', 11)
        self.layout      = QVBoxLayout()
        text_file = open(joint_list,"r")
        lines = text_file.readline().split(',')
        text_file.close()
        self.bones_joints_list = lines

        self.init()
        self.setLayout(self.layout)


    def init(self):
        self.init_output() #output box for distance- has a qlineitem and aqpushbutton('Measure)
        self.init_side_buttons() #initialises panel with R L N/A
        self.init_label_selection() #initialises qlineedit for the joint/bone selection
        self.init_save_discard() #initialises the buttons for the save and discard methods

    def init_output(self):
        """
        Creates a Qwidget that has a box and a qpushbutton('Measure)
        :return:
        :rtype:
        """
        self.output_box_layout = QHBoxLayout()
        self.output_box_layout.setContentsMargins(0,0,0,0)
        self.output_box = BoxDistanceArea()
        self.output_box.setText("0mm")
        self.output_box.add_to_layout(self.output_box_layout)

        self.output_button = QPushButton("Measure")
        self.output_button.setStyleSheet("background-color: #666666; color: white")
        self.output_button.setFont(self.font_button)
        self.output_button.setMaximumSize(130,30)
        self.output_button.setMinimumSize(130,30)

        self.output_box_layout.addWidget(self.output_button)

        self.output_box_widget = QWidget()
        self.output_box_widget.setLayout(self.output_box_layout)
        self.layout.addWidget(self.output_box_widget)

    def init_side_buttons(self):
        """
        Creates a widget with buttons R L N/A
        :return:
        :rtype:
        """
        self.side_buttons_layout = QHBoxLayout()

        self.side_button_group,self.side_buttons = make_buttons_from_list(titles=['L','R','N/A'])

        for button in self.side_buttons:
            button.setStyleSheet("background-color: #999999; color: white")
            button.setFont(self.font_button)
            button.setMaximumSize(30,30)
            button.setMinimumSize(30,30)
            button.setCheckable(True)
            # button.setAutoExclusive(True)
            button.clicked.connect(lambda: self.get_text(self.side_buttons))
            self.side_buttons_layout.addWidget(button,alignment=Qt.AlignLeft)

        self.side_buttons_layout.addSpacing(267)
        self.layout.addLayout(self.side_buttons_layout)

    def init_label_selection(self):
        """
        Initialises a qlineedit containing the choices for the area being delineated
        :return:
        :rtype:
        """
        self.line_edit_labels = QLineEdit()
        self.line_edit_labels.setFont(self.font_text)
        self.line_edit_labels.setTextMargins(2,1,2,1)
        self.line_edit_labels.setPlaceholderText("Start typing bone or joint name")
        self.line_edit_labels.setStyleSheet(
            "background-color: #f2f2f2; color: black; border-style: solid; border-width: 1px; border-color: #BFBFBF")
        self.line_edit_labels.setMaximumSize(270,30)
        self.line_edit_labels.setMinimumSize(270,30)

        completer = QCompleter(self.bones_joints_list)
        completer.setCaseSensitivity(False)
        self.line_edit_labels.setCompleter(completer)
        self.layout.addWidget(self.line_edit_labels)

    def init_save_discard(self):
        """
        Initialises the Qpushbutton for save and discarding
        :return:
        :rtype:
        """
        self.save_discard_layout = QHBoxLayout()
        self.save_discard_layout.addSpacing(290)
        self.save_button = SaveButton()
        self.save_button.add_to_layout(self.save_discard_layout)
        self.discard_button = QPushButton("X")
        self.discard_button.setStyleSheet("background-color: #FF6666; color: white")
        self.discard_button.setFont(self.font_button)
        self.discard_button.setMaximumSize(30,30)
        self.discard_button.setMinimumSize(30,30)
        self.save_discard_layout.addWidget(self.discard_button,alignment=Qt.AlignRight)
        self.save_discard_widget = QWidget()
        self.save_discard_widget.setLayout(self.save_discard_layout)

        self.layout.addWidget(self.save_discard_widget)

    def get_text(self,buttons):
        """
        Returns the text on the button that is checked from a list of autoexclusive qpushbuttons
        :param buttons: Autoexlusive buttons
        :type buttons:
        :return:
        :rtype:
        """
        text = ''
        for button in buttons:
            if button.isChecked():
                text = button.text()
        return text


class area_menu_widget(distance_menu_widget):
    def __init__(self,name='Area'):
        super(area_menu_widget,self).__init__(name=name)

    def init(self):
        self.init_output() #output box for Area- has a qlineitem and aqpushbutton('Measure)
        self.init_annotation_type() #initialises buttons for choice of bone/tissue/joint/other
        self.init_side_buttons() #initialises panel with R L N/A
        self.init_label_selection() #initialises qlineedit for the joint/bone selection
        self.init_save_discard() #initialises the buttons for the save and discard methods


    def init_annotation_type(self):
        """
        Initialises buttons that allow to choose between Joint bone tissue other
        :return:
        :rtype:
        """
        self.annotation_type_layout = QHBoxLayout()

        self.annotation_button_group,self.annotation_type_buttons = make_buttons_from_list(titles=['Joint','Bone',
                                                                                                 'Tissue',
                                                                                        'Other'])
        self.annotation_type_buttons[1].setChecked(True)

        for button in self.annotation_type_buttons:
            button.setStyleSheet("background-color: #999999; color: white")
            button.setFont(self.font_button)
            button.setMaximumSize(70,30)
            button.setMinimumSize(70,30)
            button.setCheckable(True)
            # button.setAutoExclusive(True)
            button.clicked.connect(self.get_label_name)
            self.annotation_type_layout.addWidget(button,alignment=Qt.AlignLeft)
            if button.text() == 'Bone':
                button.toggle()
        self.annotation_type_layout.addSpacing(90)
        self.layout.addLayout(self.annotation_type_layout)

    def get_label_name(self):
        self.limb_type     = 'H'
        self.side_name     = self.get_text(self.side_buttons)
        self.organ_name    = self.get_text(self.annotation_type_buttons)
        self.suborgan_name = self.line_edit_labels.text()
        self.extension_name = self.side_name+self.limb_type+self.suborgan_name
        print(self.extension_name)


class score_menu_widget(distance_menu_widget):
    def __init__(self,name='Score',profile={}):
        damage_types         = profile.pop('damage_types',['Destruction','Proliferation'])
        self.damage_types    = damage_types
        if type(self.damage_types) is np.ndarray:
            self.damage_types = self.damage_types.tolist()
        damage_ranges        = profile.pop('damage_scores',[(0,5),(0,5)])
        self.damage_ranges   = damage_ranges
        score_technique      = profile.pop('score_technique','Ratingen')
        self.score_technique = score_technique
        default_areas        = ["IP", "DIP2", "DIP3", "DIP4", "DIP5", "PIP2", "PIP3", "PIP4", "PIP5", "MCP1", "MCP2",
                                "MCP3", "MCP4", "MCP5"]#todo: expand the score profiles to have the default areas as
        # well
        damage_areas         = profile.pop('damage_areas',default_areas)
        self.damage_areas    = damage_areas
        super(score_menu_widget,self).__init__(name=name)


    def init(self):
        self.init_side_buttons() #initialises panel with R L N/A
        self.init_label_selection() #initialises qcombobox for the joint/bone selection
        self.init_score_slider() #initialises the score sliders for dsicrete scales
        self.init_save_discard() ##initialises the buttons for the save and discard methods
        self.init_table_view()

    def init_score_slider(self):
        score_slider_layout = score_sliders(score_name=self.score_technique,damage_types=self.damage_types,
                                            damage_ranges=self.damage_ranges)
        self.layout.addLayout(score_slider_layout)
        self.score_sliders = score_slider_layout.sliders
        for key,val in self.score_sliders.items():
            val.valueChanged[int].connect(self.save_slider_value)

    def init_label_selection(self):
        label_layout = QHBoxLayout()
        self.score_technique_label = QLabel(self.score_technique+' on')
        self.score_technique_label.setFont(self.font_text)
        self.score_area_box = QComboBox()
        self.score_area_box.setFont(self.font_text)
        self.score_area_box.setContentsMargins(2,1,2,1)
        self.score_area_box.setStyleSheet(
            "background-color: #f2f2f2; color: black; border-style: solid; border-width: 1px; border-color: "
            "#BFBFBF")
        self.score_area_box.setMaximumSize(300,30)
        self.score_area_box.setMinimumSize(300,30)
        self.score_area_box.addItems(self.damage_areas)
        label_layout.addWidget(self.score_technique_label)
        label_layout.addWidget(self.score_area_box)
        label_widget = QWidget()
        label_widget.setLayout(label_layout)
        self.layout.addWidget(label_widget)

    def init_table_view(self):
        table_layout = QVBoxLayout()
        self.tableView = QTableView()
        self.tableView.setObjectName("tableView")
        self.tableView_lineEdit = QLineEdit()
        self.tableView_lineEdit.setObjectName("lineEdit")
        table_layout.addWidget(self.tableView_lineEdit)
        table_layout.addWidget(self.tableView)
        table_widget = QWidget()
        table_widget.setLayout(table_layout)
        self.layout.addWidget(table_widget)

        self.create_table_view()
        # iris = sns.load_dataset('iris')
        # iris_df = pd.DataFrame(iris)
        # model = DataFrameModel(iris)
        # self.tableView.setModel(model)

    def create_table_view(self):
        row_index = [f+'_'+side for side in ['L','R'] for f in
                     self.damage_areas]
        col_names = ['Joint Name']+ self.damage_types
        data = np.zeros((len(row_index),len(col_names))).astype(np.int)
        # data[:]= np.NAN
        df = pd.DataFrame(data=data,columns=col_names)
        df['Joint Name'] = row_index
        self.load_table_view(df)



    def load_table_view(self,dataframe):
        model = DataFrameModel(dataframe)
        self.tableView.setModel(model)

    def save_table_view(self,file_loc):
        dataframe = self.tableView.model()._dataframe
        #todo: MainWindow will super handle this: will use the xradydata attributes to save the csv will save using
        dataframe.to_csv(file_loc)

    def save_slider_value(self):
        if self.side_button_group.checkedButton() is None:
            self.popupWindow = QMessageBox.question(self,'Warning!',
                                                    "Please select a side to allocate the score" ,
                                                    QMessageBox.Ok)
            for key, val in self.score_sliders.items():
                val.setValue(0)
                val.update()

        else:

            df = self.tableView.model()._dataframe

            for keys,val in self.score_sliders.items():
                row_name = str(self.score_area_box.currentText())+'_'+self.side_button_group.checkedButton().text()
                col_name = keys
                score_array = df[col_name].to_list()
                id = np.where(df['Joint Name']==row_name)
                score_array[id[0][0]] = val.value()
                df[col_name] = np.array(score_array).astype(np.int)
            self.load_table_view(df)



            #todo: set the value of df[col_name] to the slider value and reinit the tableView




class label_extraction_menu_widget(distance_menu_widget):
    def __init__(self):
        super(label_extraction_menu_widget,self).__init__()


    def init(self):
        self.init_label_selection() #initialises qlineedit to label the patch being extracted
        self.init_extraction_buttons() #initilises buttons extract area mark point
        self.init_save_discard()

    def init_label_selection(self):
        self.qline_label = QLineEdit()
        self.qline_label.setFont(self.font_text)
        self.qline_label.setTextMargins(2,1,2,1)
        self.qline_label.setPlaceholderText("Label extracted patch")
        self.qline_label.setStyleSheet(
            "background-color: #f2f2f2; color: black; border-style: solid; border-width: 1px; border-color: #BFBFBF")
        self.qline_label.setMaximumSize(270,30)
        self.qline_label.setMinimumSize(270,30)
        self.layout.addWidget(self.qline_label)

    def init_extraction_buttons(self):
        self.buttons_extract_layout = QHBoxLayout()
        self.extract_area_button = QPushButton("Extract area")
        self.extract_area_button.setStyleSheet("background-color: #999999; color: white")
        self.extract_area_button.setFont(self.font_button)
        self.extract_area_button.setMaximumSize(110,30)
        self.extract_area_button.setMinimumSize(110,30)
        # self.extract_area_button_extract.clicked.connect(self.flag_extract_area_button)
        # self.extract_area_button_extract.clicked.connect(self.button_extract_area_clicked_extract)
        #self.extract_area_button_extract.clicked.connect(self.draw_extract_rectangle)
        self.buttons_extract_layout.addWidget(self.extract_area_button,alignment=Qt.AlignLeft)
        self.mark_point_button = QPushButton("Mark point")
        self.mark_point_button.setStyleSheet("background-color: #999999; color: white")
        self.mark_point_button.setFont(self.font_button)
        self.mark_point_button.setMaximumSize(110,30)
        self.mark_point_button.setMinimumSize(110,30)

        # self.mark_point_button_extract.clicked.connect(self.flag_mark_point_button)
        # self.mark_point_button_extract.clicked.connect(self.button_mark_point_clicked_extract)
        self.mark_point_button.setAutoExclusive(True)
        self.extract_area_button.setAutoExclusive(True)
        self.mark_point_button.setCheckable(True)
        self.extract_area_button.setCheckable(True)
        self.buttons_extract_layout.addWidget(self.mark_point_button,alignment=Qt.AlignLeft)
        self.view_all_labels_button = QPushButton("View all labels")
        self.view_all_labels_button.setStyleSheet("background-color: rgb(102,102,102); color: white")
        self.view_all_labels_button.setFont(self.font_button)
        self.view_all_labels_button.setMaximumSize(170,30)
        self.view_all_labels_button.setMinimumSize(170,30)
        self.buttons_extract_layout.addWidget(self.view_all_labels_button,alignment=Qt.AlignLeft)
        # self.buttons_extract_layout.addSpacing(145)
        top_widget=QWidget()
        top_widget.setLayout(self.buttons_extract_layout)
        self.layout.addWidget(top_widget)



class Slider(QtWidgets.QSlider): # Class creating a changed slider
    # Reference code below in this class: https://stackoverflow.com/questions/52689047/moving-qslider-to-mouse-click-position
    def mousePressEvent(self, event):
        super(Slider, self).mousePressEvent(event)
        if event.button() == Qt.LeftButton:
            val = self.pixelPosToRangeValue(event.pos())
            self.setValue(val)

    def pixelPosToRangeValue(self, pos):
        opt = QtWidgets.QStyleOptionSlider()
        self.initStyleOption(opt)
        gr = self.style().subControlRect(QtWidgets.QStyle.CC_Slider, opt, QtWidgets.QStyle.SC_SliderGroove, self)
        sr = self.style().subControlRect(QtWidgets.QStyle.CC_Slider, opt, QtWidgets.QStyle.SC_SliderHandle, self)

        if self.orientation() == Qt.Horizontal:
            sliderLength = sr.width()
            sliderMin = gr.x()
            sliderMax = gr.right() - sliderLength + 1
        else:
            sliderLength = sr.height()
            sliderMin = gr.y()
            sliderMax = gr.bottom() - sliderLength + 1;
        pr = pos - sr.center() + sr.topLeft()
        p = pr.x() if self.orientation() == Qt.Horizontal else pr.y()
        return QtWidgets.QStyle.sliderValueFromPosition(self.minimum(), self.maximum(), p - sliderMin,
                                               sliderMax - sliderMin, opt.upsideDown)


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

        pass



def make_buttons_from_list(titles=['L','R','N/A']):
    groupBox = QButtonGroup()
    # groupBox.setCheckable(True)
    # groupBox.setChecked(True)
    groupBox.setExclusive(True)
    button_list = []
    for title in titles:
        button = QPushButton(title)
        # button.setAutoExclusive(True)
        button_list += [button]
        groupBox.addButton(button)

    return groupBox,button_list



def make_buttons_from_list_old(titles=['L','R','N/A']):
    button_list = []
    for title in titles:
        button_list += [QPushButton(title)]
    return button_list


class BoxDistanceArea(QLabel):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        # Font settings
        self.font_header = QFont('Android Roboto', 15)
        self.font_subheader = QFont('Android Roboto', 13)
        self.font_text = QFont('Android Roboto', 10)
        self.font_button = QFont('Android Roboto', 11)

        self.box = QLabel("0")
        self.box.setContentsMargins(2, 1, 2, 1)
        self.box.setFont(self.font_text)
        self.box.setStyleSheet(
            "background-color: white; color: red; border-style: solid; border-width: 1px; border-color: red")
        self.box.setMaximumSize(175, 30)
        self.box.setMinimumSize(175, 30)

    def update_distance_box(self, scene):
        self.box.setText(str(round(scene.get_distance(), 2)) + " mm")
        try:
            InspectXRays.save_distance_button.restore_save_button()
        except:
            pass

    def update_area_box(self, scene):
        self.box.setText(str(round(200, 2)) + " sqmm") # todo: take in real area


    def add_to_layout(self, layout):
        layout.addWidget(self.box, alignment=Qt.AlignLeft)




class SaveButton(QPushButton):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        # Font settings
        self.font_header = QFont('Android Roboto', 15)
        self.font_subheader = QFont('Android Roboto', 13)
        self.font_text = QFont('Android Roboto', 10)
        self.font_button = QFont('Android Roboto', 11)

        self.setText("Save")
        self.setStyleSheet("background-color: #16CCB1; color: white")
        self.setFont(self.font_button)
        self.setMaximumSize(75, 30)
        self.setMinimumSize(75, 30)

    def add_to_layout(self, layout):
        layout.addWidget(self, alignment=Qt.AlignRight)

    def set_to_saved(self):
        self.setText("Saved")
        self.setStyleSheet("background-color: #CCCCCC; color: black")
        self.setDisabled(True)

    def restore_save_button(self):
        self.setText("Save")
        self.setStyleSheet("background-color: #16CCB1; color: white")
        self.setDisabled(False)

    def restore_save_button_score(self):
        if self.save_score_flag == 1:
            self.setText("Save")
            self.setStyleSheet("background-color: #16CCB1; color: white")
            self.setDisabled(False)
            self.save_score_flag = 0


# class leftLayout():
class xray_selection_menu(QWidget):
    """
    class that handles the xray creation and the damage type selector
    """
    def __init__(self):
        super(xray_selection_menu,self).__init__()
        self.font_header = QFont('Android Roboto', 15)
        self.font_subheader = QFont('Android Roboto', 13)
        self.font_text = QFont('Android Roboto', 10)
        self.font_button = QFont('Android Roboto', 11)

        self.layout = QVBoxLayout()
        self.init_xray_creation_options()
        self.init_damage_selector()
        self.setLayout(self.layout)

    def init_xray_creation_options(self):
        layout = QHBoxLayout()
        study_id_label = QLabel("Study ID")
        study_id_label.setFont(self.font_text)
        layout.addWidget(study_id_label,1)  # Number for relative size compared to other widgets
        self.combobox_studyid = QComboBox()
        self.combobox_studyid.setFont(self.font_text)
        layout.addWidget(self.combobox_studyid,2)  # Number for relative size compared to other widgets

        xray_id_label = QLabel("Xray ID")
        xray_id_label.setFont(self.font_text)
        layout.addWidget(xray_id_label,1)  # Number for relative size compared to other widgets
        self.combobox_xrayid = QComboBox()
        self.combobox_xrayid.setFont(self.font_text)
        layout.addWidget(self.combobox_xrayid,2)  # Number for relative size compared to other widgets

        button_layout = QHBoxLayout()
        self.new_study_button = QPushButton("+ New Study")
        self.new_study_button.setStyleSheet(
            "QPushButton" "{" "background-color: rgb(102,102,102); color: white" "}" "QPushButton::pressed" "{"
            "background-color: #362699; color: white" "}")

        self.addXrayToStudy_button = QPushButton("Add X-ray to Study")
        self.addXrayToStudy_button.setStyleSheet(
            "QPushButton" "{" "background-color: rgb(102,102,102); color: white" "}" "QPushButton::pressed" "{"
            "background-color: #362699; color: white" "}")
        button_layout.addWidget(self.new_study_button)
        button_layout.addWidget(self.addXrayToStudy_button)


        widget_options = QWidget()
        widget_options.setLayout(layout)
        widget_buttons = QWidget()
        widget_buttons.setLayout(button_layout)
        self.layout.addWidget(widget_options)
        self.layout.addWidget(widget_buttons)



    def init_damage_selector(self):
        layout = QHBoxLayout()
        score_id_label = QLabel("Scoring Method")
        score_id_label.setFont(self.font_text)
        layout.addWidget(score_id_label,1)

        self.score_selector = QComboBox()
        self.score_selector.setFont(self.font_text)
        self.score_selector.setStyleSheet(
            "QPushButton" "{" "background-color: rgb(102,102,102); color: white" "}" "QPushButton::pressed" "{"
            "background-color: #362699; color: white" "}")
        layout.addWidget(self.score_selector,2)
        widget = QWidget()
        widget.setLayout(layout)
        self.layout.addWidget(widget)













class XrayDataCreationDialog(QMessageBox):
    def __init__(self):
        super(XrayDataCreationDialog,self).__init__()

        self.setIcon(QMessageBox.Information)
        self.setText("Do you wish to create a score sheet for this x-ray?")
        self.setWindowTitle("Score Sheet Creation")
        # self.continue_button = self.addButton(QPushButton("Continue"), QMessageBox.Yes,Q)
        self.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        # self.buttonClicked.connect(self.msgact_close)
        self.exec()



class XrayDataCreationOptions(QWidget):
    def __init__(self,name='Xray Annotation Creation'):
        super(XrayDataCreationOptions,self).__init__()
        self.name = name
        self.font_header = QFont('Android Roboto', 15)
        self.font_subheader = QFont('Android Roboto', 13)
        self.font_text = QFont('Android Roboto', 10)
        self.font_button = QFont('Android Roboto', 11)
        self.layout      = QHBoxLayout()
        # text_file = open("config/joint_list.txt","r")
        # lines = text_file.readline().split(',')
        # text_file.close()
        # self.bones_joints_list = lines

        self.init()
        self.setLayout(self.layout)


    def init(self):

        self.save_button = SaveButton()
        # self.save_button.add_to_layout(self.save_discard_layout)
        self.discard_button = QPushButton("X")
        self.discard_button.setStyleSheet("background-color: #FF6666; color: white")
        self.discard_button.setFont(self.font_button)
        self.discard_button.setMaximumSize(30,30)
        self.discard_button.setMinimumSize(30,30)

        self.qline_edits = {}
        self.input_box_layout = QVBoxLayout()
        self.desc_box_layout  = QVBoxLayout()
        for name in ['Acquisition Date','Xray id','Body Part']:
            self.qline_edits[name] = QLineEdit()
            label = QLabel(name)
            self.desc_box_layout.addWidget(label)
            self.input_box_layout.addWidget(self.qline_edits[name])
        self.desc_box_layout.addWidget(self.save_button)
        self.input_box_layout.addWidget(self.discard_button)

        self.input_box_widget = QWidget()
        self.input_box_widget.setLayout(self.input_box_layout)

        self.desc_box_widget = QWidget()
        self.desc_box_widget.setLayout(self.desc_box_layout)

        self.layout.addWidget(self.desc_box_widget)
        self.layout.addWidget(self.input_box_widget)


    def init_save_discard(self):
        """
        Initialises the Qpushbutton for save and discarding
        :return:
        :rtype:
        """
        self.save_discard_layout = QVBoxLayout()
        self.save_discard_layout.addSpacing(290)
        self.save_button = SaveButton()
        self.save_button.add_to_layout(self.save_discard_layout)
        self.discard_button = QPushButton("X")
        self.discard_button.setStyleSheet("background-color: #FF6666; color: white")
        self.discard_button.setFont(self.font_button)
        self.discard_button.setMaximumSize(30,30)
        self.discard_button.setMinimumSize(30,30)
        self.save_discard_layout.addWidget(self.discard_button,alignment=Qt.AlignRight)
        self.save_discard_widget = QWidget()
        self.save_discard_widget.setLayout(self.save_discard_layout)

        self.layout.addWidget(self.save_discard_widget)

    def get_text(self,buttons):
        """
        Returns the text on the button that is checked from a list of autoexclusive qpushbuttons
        :param buttons: Autoexlusive buttons
        :type buttons:
        :return:
        :rtype:
        """
        text = ''
        for button in buttons:
            if button.isChecked():
                text = button.text()
        return text


class XRayCreationWindow(QMainWindow):
    def __init__(self, parent=None):
        super(XRayCreationWindow, self).__init__(parent)
        self.xray_creation_options = XrayDataCreationOptions()
        self.setCentralWidget(self.xray_creation_options)



#extracts year,id and organ information from a saved filename
class NameSignature(object):
    def __init__(self,fileName):
        if len(fileName.split('.'))==2:
            fileName = fileName.split('.')[0]
        self.year  = ''
        self.organ = ''
        self.id    = ''
        self.verify(fileName)

    def verify(self,fileName):
        if len(fileName)==13 and (fileName[-5]=='h' or fileName[-5]=='f'):
            self.year  = fileName[-4:]
            self.organ = 'FEET' if fileName[-5]=='f' else 'HANDS'
            self.id    = fileName[:8]
        elif len(fileName.split('_'))==3:
            splits     = fileName.split('_')
            self.year  = splits[1]
            self.organ = splits[2].upper()
            self.id    = splits[0]


def output_annotation_name(level1_name ='hand',level2_name='R',level3_name='MCP1'):
    return level1_name+'_'+level2_name+'_'+level3_name



def update_dir(nameInit):
    output_directory = nameInit
    if not os.path.exists(output_directory):
        output_directory = os.path.join(output_directory,'1')
    else:
        highest_num = 0
        for f in os.listdir(output_directory):
            if os.path.exists(os.path.join(output_directory, f)):
                file_name = os.path.splitext(f)[0]
                try:
                    file_num = int(file_name)
                    if file_num > highest_num:
                        highest_num = file_num
                except ValueError:
                    print('The file name "%s" is not an integer. Skipping' % file_name)

        output_directory = os.path.join(output_directory, str(highest_num + 1))
    os.makedirs(output_directory)
    return output_directory

#Class that loads the latest data stored in the csv file into a python array
class XrayData(object):
    def __init__(self,image_name,xray_id,acquisition_date,save_loc='saved_data',organ_name='hand',meta_loc=None):


        if meta_loc is None:
            self.xray_id  = xray_id
            self.save_loc = os.path.join(save_loc,xray_id)
            self.meta_table = {'acquisition_date': [acquisition_date],'xray_id':[xray_id],'organ':[organ_name],
                               'file_name': [image_name]}


            for id in ['scores','bone','joint']:
                temp_loc = os.path.join(self.save_loc,id)
                if not os.path.isdir(os.path.join(temp_loc,acquisition_date)): os.makedirs(os.path.join(temp_loc,acquisition_date))
            self.save_metadata()
        else:
            self.init_from_meta(meta_loc)



    def save_metadata(self):
        fileName = os.path.join(self.save_loc,'metadata.csv')
        save_csv(mydict=self.meta_table,fileName=fileName)
        # df = pd.DataFrame(self.meta_table)
        # df.to_csv(os.path.join(self.save_loc,'metadata.csv'),index=False)



    def add_xray(self,image_name,xray_id,acquisition_date,save_loc='saved_data',organ_name='hand'):
        # self.meta_table = {'acquisition_date':acquisition_date,'xray_id':xray_id,'organ':organ_name}
        # if type(self.meta_table) is pd.core.frame.DataFrame:
        #     meta_table = {}
        #     meta_table['acquisition_date'] = np.append(self.meta_table['acquisition_date'].to_numpy(),acquisition_date)
        #     meta_table['xray_id'] = np.append(self.meta_table['xray_id'].to_numpy(),
        #                                                     xray_id)
        #     meta_table['organ'] = np.append(self.meta_table['organ'].to_numpy(),
        #                                                     organ_name)
        #     meta_table['file_name'] = np.append(self.meta_table['file_name'].to_numpy(),
        #                                                     image_name)
        #     self.meta_table = pd.DataFrame(meta_table)
        if type(self.meta_table) is dict:
            self.meta_table['acquisition_date'].append(acquisition_date)
            self.meta_table['xray_id'].append(xray_id)
            self.meta_table['organ'].append(organ_name)
            self.meta_table['file_name'].append(image_name)
            self.meta_table = pd.DataFrame(self.meta_table)
        for id in ['scores','bone','joint']:
            temp_loc = os.path.join(self.save_loc,id)
            if not os.path.isdir(os.path.join(temp_loc,acquisition_date)): os.makedirs(
                os.path.join(temp_loc,acquisition_date))
        self.save_metadata()


    def save_bone_outline(self,bone_id,date,plineItem):
        save_folder = os.path.join(self.save_loc,'bone')
        save_folder = os.path.join(save_folder,str(date))
        print(bone_id)
        filename    = os.path.join(save_folder,bone_id+'.txt')
        np.savetxt(filename,plineItem.control_points.tolist())

    def save_patch(self,joint_id,date,rectItem):
        save_folder =os.path.join(self.save_loc,'joint')
        save_folder = os.path.join(save_folder,str(date))
        filename = os.path.join(save_folder,joint_id + '.txt')
        np.savetxt(filename,rectItem.model.control_points.tolist())

    def load_patches(self):
        save_folder = os.path.join(self.save_loc,'joint_patch')

        my_lib = {}
        for f in os.listdir(save_folder):
            my_lib[f.split('.')[-1]] = np.loadtxt(os.path.join(save_folder,f))

    def load_outlines(self):
        save_folder = os.path.join(self.save_loc,'joint_patch')

        my_lib = {}
        for f in os.listdir(save_folder):
            my_lib[f.split('.')[-1]] = np.loadtxt(os.path.join(save_folder,f))

    def init_from_meta(self,meta_loc):
        """

        :param meta_loc: location pointing to the metadata.csv
        :return:
        """
        self.save_loc = meta_loc
        self.meta_table = load_csv(os.path.join(meta_loc,'metadata.csv'))
        # self.meta_table = pd.read_csv(os.path.join(meta_loc,'metadata.csv'))
        # self.meta_table = self.meta_table.to_dict()







# #class to create a dataframe that is viewable through qttableview
#
# class PandasModel(QAbstractTableModel):
#     """
#     https://stackoverflow.com/posts/44605011/revisions
#     """
#     def __init__(self, df = pd.DataFrame(), parent=None):
#         QAbstractTableModel.__init__(self, parent=parent)
#         self._df = df.copy()
#
#     def toDataFrame(self):
#         return self._df.copy()
#
#     def headerData(self, section, orientation, role=Qt.DisplayRole):
#         if role != Qt.DisplayRole:
#             return QVariant()
#
#         if orientation == Qt.Horizontal:
#             try:
#                 return self._df.columns.tolist()[section]
#             except (IndexError, ):
#                 return QtCore.QVariant()
#         elif orientation == Qt.Vertical:
#             try:
#                 # return self.df.index.tolist()
#                 return self._df.index.tolist()[section]
#             except (IndexError, ):
#                 return QVariant()
#
#     def data(self, index, role=Qt.DisplayRole):
#         if role != Qt.DisplayRole:
#             return QVariant()
#
#         if not index.isValid():
#             return QVariant()
#
#         return QVariant(str(self._df.ix[index.row(), index.column()]))
#
#     def setData(self, index, value, role):
#         row = self._df.index[index.row()]
#         col = self._df.columns[index.column()]
#         if hasattr(value, 'toPyObject'):
#             # PyQt4 gets a QVariant
#             value = value.toPyObject()
#         else:
#             # PySide gets an unicode
#             dtype = self._df[col].dtype
#             if dtype != object:
#                 value = None if value == '' else dtype.type(value)
#         self._df.set_value(row, col, value)
#         return True
#
#     def rowCount(self, parent=QModelIndex()):
#         return len(self._df.index)
#
#     def columnCount(self, parent=QModelIndex()):
#         return len(self._df.columns)
#
#     def sort(self, column, order):
#         colname = self._df.columns.tolist()[column]
#         self.layoutAboutToBeChanged.emit()
#         self._df.sort_values(colname, ascending= order == Qt.AscendingOrder, inplace=True)
#         self._df.reset_index(inplace=True, drop=True)
#         self.layoutChanged.emit()
#
# #
# class DataFrameModel(QAbstractTableModel):
#     """
#     https://stackoverflow.com/posts/44605011/revisions
#     """
#     DtypeRole = Qt.UserRole + 1000
#     ValueRole = Qt.UserRole + 1001
#
#     def __init__(self, df=pd.DataFrame(), parent=None):
#         super(DataFrameModel, self).__init__(parent)
#         self._dataframe = df
#
#     def setDataFrame(self, dataframe):
#         self.beginResetModel()
#         self._dataframe = dataframe.copy()
#         self.endResetModel()
#
#     def dataFrame(self):
#         return self._dataframe
#
#     dataFrame = pyqtProperty(pd.DataFrame, fget=dataFrame, fset=setDataFrame)
#
#     @pyqtSlot(int, Qt.Orientation, result=str)
#     def headerData(self, section: int, orientation: Qt.Orientation, role: int = Qt.DisplayRole):
#         if role == Qt.DisplayRole:
#             if orientation == Qt.Horizontal:
#                 return self._dataframe.columns[section]
#             else:
#                 return str(self._dataframe.index[section])
#         return QVariant()
#
#     def rowCount(self, parent=QModelIndex()):
#         if parent.isValid():
#             return 0
#         return len(self._dataframe.index)
#
#     def columnCount(self, parent=QModelIndex()):
#         if parent.isValid():
#             return 0
#         return self._dataframe.columns.size
#
#     def data(self, index, role=Qt.DisplayRole):
#         if not index.isValid() or not (0 <= index.row() < self.rowCount() \
#             and 0 <= index.column() < self.columnCount()):
#             return QVariant()
#         row = self._dataframe.index[index.row()]
#         col = self._dataframe.columns[index.column()]
#         dt = self._dataframe[col].dtype
#
#         val = self._dataframe.iloc[row][col]
#         if role == Qt.DisplayRole:
#             return str(val)
#         elif role == DataFrameModel.ValueRole:
#             return val
#         if role == DataFrameModel.DtypeRole:
#             return dt
#         return QVariant()
#
#     def roleNames(self):
#         roles = {
#             Qt.DisplayRole: b'display',
#             DataFrameModel.DtypeRole: b'dtype',
#             DataFrameModel.ValueRole: b'value'
#         }
#         return roles



class DictionaryTableModel(QAbstractTableModel):
    def __init__(self, dictionary):
        super(DictionaryTableModel, self).__init__()
        self._data = dictionary
        self._headers = []
        for keys,val in dictionary.items():
            self._headers += [keys]

    def data(self, index, role):
        if role == Qt.DisplayRole:
            # Look up the key by header index.
            column = index.column()
            column_key = self._headers[column]
            return self._data[column_key][index.row()]

    def rowCount(self, index):
        # The length of the outer list.
        return len(self._data)

    def columnCount(self, index):
        # The length of our headers.
        return len(self._headers)

    def headerData(self, section, orientation, role):
        # section is the index of the column/row.
        if role == Qt.DisplayRole:
            if orientation == Qt.Horizontal:
                return str(self._headers[section])

            if orientation == Qt.Vertical:
                return str(section)



def print_slider_values(sliders):
    for slider in sliders:
        print(slider.value())



def save_csv(mydict,fileName):
    with open(fileName,'w') as f:
        w = csv.writer(f)
        w.writerow(mydict.keys())
        w.writerows(mydict.items())


def load_csv(fileName):
    with open(fileName,mode='r') as infile:
        reader = csv.reader(infile)
        with open('coors_new.csv',mode='w') as outfile:
            writer = csv.writer(outfile)
            loaded_dict = {rows[0]:rows[1] for rows in reader}
    return loaded_dict


if __name__=='__main__':
    #main()
    xray_record = XrayData(image_name='CPSA0045h2012.png',xray_id='CPSA0045',acquisition_date='2012',
                           meta_loc='saved_data/165489')
    # xray_record.add_xray(image_name='CPSA0045h2012.png',xray_id='CPSA0045',acquisition_date='2012',
    # save_loc='saved_data',
    # organ_name='hand')





