from PyQt5.QtWidgets import *


from Profiles import *
import shutil
import numpy as np
import cv2


# Global variables to flag what tab needs to be navigated back to after creating new scoring sheet
review_scoring_sheet_flag = 0
inspect_x_rays_flag = 0
zoom_tracker = 1
image_file_list = []
distance_edit_flag = 0
coordinate_count = 0
xray_image = 0



from MenuWidgets import area_menu_widget,score_menu_widget, \
    xray_selection_menu, XrayDataCreationDialog,  XRayCreationWindow, XrayData, NameSignature,output_annotation_name,\
    save_csv, load_csv

from ImagingWidgets import ImageHandler
from DiagnosticWidgets import PlotWindow


class InspectXRays(QMainWindow):
    def __init__(self,ctx):
        super(InspectXRays,self).__init__()
        self.ctx = ctx
        self._panels = []
        self.initialise_left_panel()   #initialises self.menu_tabs and adds it to self._panels
        self.initialise_right_panel()  #initialises self.image_scene and adds it to self._panels


        # self.merge_layouts()
        self.split_layouts()
        self.setCentralWidget(self.main_widget)
        self.output_loc = 'saved_data'
        self.connect_sub_buttons()
        self.initialise_xray_record()
        self.xray_selection_menu.wd_info.setText(os.path.abspath(self.output_loc))
        self.load_new_score_sheet()



    def initialise_left_panel(self):
        layout = QVBoxLayout()
        self.xray_selection_menu = xray_selection_menu()
        self.xray_selection_menu.setMinimumWidth(500)
        self.xray_selection_menu.setMaximumWidth(500)
        # score_profiles = [f.split('.')[0] for f in os.listdir(self.ctx.profiles) if f.split('.')[-1]=='h5']
        score_profiles = [keys for keys,_ in self.ctx.score_profiles.items()]
        self.xray_selection_menu.score_selector.addItems(score_profiles)





        layout.addWidget(self.xray_selection_menu)

        self.menu_tabs = QTabWidget()
        self.menu_tabs.setMinimumWidth(500)
        self.menu_tabs.setMaximumWidth(500)
        # self.widget_distance_menu = distance_menu_widget()
        self.widget_area_menu     = area_menu_widget(self.ctx.joint_list)

        self.widget_score_menu    = score_menu_widget()

        # self.widget_label_menu    = label_extraction_menu_widget()
        # self.menu_tabs.addTab(self.widget_distance_menu,'Distance')
        self.menu_tabs.addTab(self.widget_area_menu,'Annotation')
        self.menu_tabs.addTab(self.widget_score_menu,'Score')
        # self.menu_tabs.addTab(self.widget_label_menu,'Label')
        layout.addWidget(self.menu_tabs)
        self.left_panel = QWidget()
        self.left_panel.setLayout(layout)
        self._panels = self._panels+[self.left_panel]

        self.xray_record = None


    def load_new_score_sheet(self):
        # profile_loc = os.path.join('score_profiles',str(self.xray_selection_menu.score_selector.currentText())+'.h5')
        profile_loc = self.ctx.score_profiles[str(self.xray_selection_menu.score_selector.currentText())]
        profile = load_profile(profile_loc)
        profile['score_technique'] = str(self.xray_selection_menu.score_selector.currentText())
        self.menu_tabs.removeTab(1)
        self.widget_score_menu = score_menu_widget(profile=profile)
        self.menu_tabs.addTab(self.widget_score_menu,self.widget_score_menu.score_technique)
        self.connect_sub_buttons()

        date = NameSignature(self.xray_selection_menu.combobox_xrayid.currentText()).year
        #self.xray_record.meta_table[]
        file_loc = os.path.join(self.output_loc,'scores')
        #print(file_loc)
        file_loc = os.path.join(file_loc,date)
        file_name = os.path.join(file_loc,self.widget_score_menu.score_technique + '.csv')

        if os.path.isfile(file_name):
            my_dict = load_csv(file_name)
            self.widget_score_menu.load_table_view(my_dict)

        file_loc = os.path.join(self.output_loc)
        file_name = os.path.join(file_loc,"annotation_tracking_"+date+".csv")
        if os.path.isfile(file_name):
            my_dict = load_csv(file_name)
            self.widget_area_menu.load_table_view(my_dict)



    def initialise_right_panel(self):

        # Creating toolbar

        # Toolbar settings - guidance on https://www.learnpyqt.com/courses/start/actions-toolbars-menus/
        self.image_widget = ImageHandler(self.ctx.image_handler_icons)
        self._panels = self._panels + [self.image_widget]


    def open_output_folder_selector(self):
        dlg = QFileDialog()
        dlg.setFileMode(QFileDialog.Directory)
        if dlg.exec_():
            folder_names = dlg.selectedFiles()
            self.output_loc = os.path.join(os.sep,folder_names[0])
            if not os.path.isdir(self.output_loc):
                os.makedirs(self.output_loc)
            self.xray_selection_menu.wd_info.setText(self.output_loc)
            self.xray_selection_menu.combobox_xrayid.clear()
            self.xray_selection_menu.combobox_studyid.clear()
            self.display_studies()
            #self.display_xrays()



    def open_study_creator(self):
        #print('function triggered')
        dlg = QFileDialog()
        dlg.setFileMode(QFileDialog.AnyFile)
        # dlg.setFilter("Text files (*.txt)")
        filenames =[]# QStringList()

        if dlg.exec_():
            filenames = dlg.selectedFiles()
            # f = open(filenames[0],'r')
            self.image_widget.load_image(file_name=filenames[0])
            self.image_widget.toolbar.buttons['Good Image Quality'].setChecked(1)
            print("Image quality is ={:}".format(int(self.image_widget.image_quality_flag)))

            self.create_image_menu = XrayDataCreationDialog()
            if QMessageBox.Yes:
                self.create_xray_window = XRayCreationWindow()
                self.create_xray_window.show()
                self.name_sig  = NameSignature(fileName=filenames[0].split('/')[-1].split('.')[0])
                #print(self.name_sig.year)
                self.create_xray_window.xray_creation_options.save_button.clicked.connect(
                    lambda:self.create_xray_data(filenames[0]))

                self.create_xray_window.xray_creation_options.qline_edits['Acquisition Date'].setText(self.name_sig.year)

                self.create_xray_window.xray_creation_options.qline_edits['Study id'].setText(self.name_sig.id)
                self.create_xray_window.xray_creation_options.qline_edits['Body Part'].setText(self.name_sig.organ)


                self.create_xray_window.xray_creation_options.discard_button.clicked.connect(
                    lambda:self.create_xray_window.close())

    def open_xray_adder(self):
        #print('function triggered')
        dlg = QFileDialog()
        dlg.setFileMode(QFileDialog.AnyFile)
        # dlg.setFilter("Text files (*.txt)")
        filenames =[]# QStringList()

        if dlg.exec_():
            filenames = dlg.selectedFiles()
            # f = open(filenames[0],'r')
            self.image_widget.load_image(file_name=filenames[0])
            self.image_widget.toolbar.buttons['Good Image Quality'].setChecked(1)
            print("Image quality is ={:}".format(int(self.image_widget.image_quality_flag)))


            self.create_image_menu = XrayDataCreationDialog()
            if QMessageBox.Yes:
                self.create_xray_window = XRayCreationWindow()

                self.create_xray_window.show()
                self.name_sig  = NameSignature(fileName=filenames[0].split('/')[-1].split('.')[0])
                #print(self.name_sig.year)
                self.create_xray_window.xray_creation_options.save_button.clicked.connect(
                    lambda:self.add_xray_to_study(filenames[0]))


                self.create_xray_window.xray_creation_options.qline_edits['Acquisition Date'].setText(self.name_sig.year)

                self.create_xray_window.xray_creation_options.qline_edits['Study id'].setText(self.name_sig.id)
                self.create_xray_window.xray_creation_options.qline_edits['Body Part'].setText(self.name_sig.organ)
                id_text = self.xray_selection_menu.combobox_studyid.currentText()
                if id_text is not None or id_text!='':
                    self.create_xray_window.xray_creation_options.qline_edits['Study id'].setText(id_text)


                self.create_xray_window.xray_creation_options.discard_button.clicked.connect(
                    lambda:self.create_xray_window.close())


    def create_xray_data(self,filename):
        # self.create_xray_window.xray_creation_options.qline_edits['Acquisition Date','Xray id','Xray Location']
        # self.name_sig = NameSignature(fileName=filenames[0].split('/')[-1])

        acquisition_date = self.create_xray_window.xray_creation_options.qline_edits['Acquisition Date'].text()
        Xray_id          = self.create_xray_window.xray_creation_options.qline_edits['Study id'].text()
        organ_name       = self.create_xray_window.xray_creation_options.qline_edits['Body Part'].text()


        if os.path.isdir(os.path.join(self.output_loc,Xray_id)):
            self.popupWindow = QMessageBox.question(self,'Warning!',
                                                    "Study with same Id already exists, please change the id or "
                                                    "select add x-ray to id instead." ,
                                                    QMessageBox.Ok)
            return -1

        self.xray_record = XrayData(image_name=filename.split('/')[-1],xray_id=Xray_id,acquisition_date=acquisition_date,\
                                                                                  organ_name=organ_name,
                                    save_loc=self.output_loc)

        shutil.copyfile(self.image_widget.image_filename,os.path.join(self.xray_record.save_loc,
                                                                  self.image_widget.image_filename.split(
            '/')[-1] ) )
        # print(self.xray_record.save_loc)
        self.create_xray_window.close()
        self.xray_selection_menu.combobox_studyid.addItem(Xray_id)
        self.xray_selection_menu.combobox_studyid.setCurrentIndex(self.xray_selection_menu.combobox_studyid.count() - 1)


    def add_xray_to_study(self,filename):
        acquisition_date = self.create_xray_window.xray_creation_options.qline_edits['Acquisition Date'].text()
        Xray_id          = self.create_xray_window.xray_creation_options.qline_edits['Study id'].text()
        organ_name       = self.create_xray_window.xray_creation_options.qline_edits['Body Part'].text()
        self.xray_record.add_xray(image_name=filename.split('/')[-1],xray_id=Xray_id,acquisition_date=acquisition_date,
                             save_loc=self.output_loc,
                             organ_name=organ_name)
        shutil.copyfile(self.image_widget.image_filename,os.path.join(self.xray_record.save_loc,
                                                                  self.image_widget.image_filename.split(
            '/')[-1] ) )
        self.xray_selection_menu.combobox_xrayid.addItem(filename.split('/')[-1])
        self.xray_selection_menu.combobox_xrayid.setCurrentIndex(self.xray_selection_menu.combobox_xrayid.count() - 1)

        self.create_xray_window.close()
        self.display_image_info()





    def connect_sub_buttons(self):

        self.display_studies()
        self.xray_selection_menu.set_wdir_button.clicked.connect(self.open_output_folder_selector)
        self.xray_selection_menu.new_study_button.clicked.connect(self.open_study_creator)
        self.xray_selection_menu.addXrayToStudy_button.clicked.connect(self.open_xray_adder)
        self.xray_selection_menu.combobox_studyid.currentIndexChanged.connect(self.display_xrays)
        self.xray_selection_menu.combobox_xrayid.activated.connect(self.load_selected_xrays)
        self.xray_selection_menu.combobox_xrayid.currentIndexChanged.connect(self.load_selected_xrays)
        self.xray_selection_menu.score_selector.currentIndexChanged.connect(self.load_new_score_sheet)
        self.widget_area_menu.save_button.clicked.connect(self.save_annotation)
        self.widget_score_menu.save_button.clicked.connect(self.save_scores)
        self.widget_area_menu.view_button.clicked.connect(self.display_all_current_annotations)
        self.widget_area_menu.unsure_button.clicked.connect(self.update_tracking_annotation)
        self.widget_score_menu.unsure_button.clicked.connect(self.update_tracking_score)
        self.image_widget.toolbar.buttons['Good Image Quality'].triggered.connect(self.update_image_quality_score)
        self.image_widget.toolbar.buttons['Bad Image Quality'].triggered.connect(self.update_image_quality_score)



    def split_layouts(self):
        self.main_widget = QSplitter()
        for panel in self._panels:
            self.main_widget.addWidget(panel)

    def merge_layouts(self):
        self.main_layout = QHBoxLayout()
        self.main_widget = QWidget()

        for panel in self._panels:
            self.main_layout.addWidget(panel)

        self.main_widget.setLayout(self.main_layout)


    def save_annotation(self):
        if self.xray_record is None:
            self.popupWindow = QMessageBox.question(self,'Warning!',
                                                    "No xray record loaded. Please create or load an x-ray record "
                                                    "before "
                                                    "saving the "
                                                    "score" ,
                                                    QMessageBox.Ok)
            return -1
        if self.image_widget.image_scene.polyline_annotate_item is None and \
                self.image_widget.image_scene.rect_annotate_item is None:
            self.popupWindow = QMessageBox.question(self,'Warning!',
                                                    "No labels drawn, please draw a label before attempting to save "
                                                    "one" ,
                                                    QMessageBox.Ok)
            return -1

        if self.widget_area_menu.line_edit_labels.text() == '':
            self.popupWindow = QMessageBox.question(self,'Warning!',
                                                    "Please select which bone or joint you wish to save" ,
                                                    QMessageBox.Ok)
            return -1

        if self.image_widget.image_scene.polyline_annotate_item is None and \
                self.image_widget.image_scene.rect_annotate_item is not None and \
                self.widget_area_menu.annotation_button_group.checkedButton().text() == 'Bone':
            self.popupWindow = QMessageBox.question(self,'Warning!',
                                                    "Please select Joint when annotating with a rectangle" ,
                                                    QMessageBox.Ok)
            return -1

        if self.widget_area_menu.side_button_group.checkedButton() is None:
            self.popupWindow = QMessageBox.question(self,'Warning!',
                                                    "Please select the L or R before saving",
                                                    QMessageBox.Ok)

        if self.image_widget.image_scene.polyline_annotate_item is not None and \
                self.image_widget.image_scene.rect_annotate_item is None and \
                self.widget_area_menu.annotation_button_group.checkedButton().text() == 'Joint':
            self.popupWindow = QMessageBox.question(self,'Warning!',
                                                    "Please select Bone when annotating with a polyline" ,
                                                    QMessageBox.Ok)


        dates     = np.array(self.xray_record.meta_table['acquisition_date'],dtype=np.int)
        filenames = np.array(self.xray_record.meta_table['file_name'])

        id = np.where(filenames == self.xray_selection_menu.combobox_xrayid.currentText())

        # print(self.xray_selection_menu.combobox_xrayid.currentText())
        # print(id)
        level1_name = self.xray_record.meta_table['organ'][id[0][0]]

        # level1_name = self.xray_record.meta_table['organ']
        side_name   = self.widget_area_menu.side_button_group.checkedButton().text()
        if side_name=='N/A':
            side_name = 'NA'
        level2_name = side_name
        level3_name = self.widget_area_menu.line_edit_labels.text()

        annotation_id = output_annotation_name(level1_name =level1_name,
                                               level2_name=level2_name,
                                               level3_name=level3_name)
        area_name = level3_name+'_'+side_name
        #print(area_name)
        date = dates[id[0][0]]
        #print(date)
        if self.image_widget.image_scene.polyline_annotate_item is not None and \
                self.widget_area_menu.annotation_button_group.checkedButton().text()=='Bone':
            self.xray_record.save_bone_outline(bone_id=annotation_id,date=date,
                                               plineItem=self.image_widget.image_scene.polyline_annotate_item)
            self.widget_area_menu.update_table_view(row_name=area_name,signal='Completed')

        if self.image_widget.image_scene.polyline_annotate_item is not None and \
                self.widget_area_menu.annotation_button_group.checkedButton().text()=='Tissue':
            self.xray_record.save_tissue_outline(bone_id=annotation_id,date=date,
                                               plineItem=self.image_widget.image_scene.polyline_annotate_item)
            self.widget_area_menu.update_table_view(row_name=area_name,signal='Completed')

        if self.image_widget.image_scene.rect_annotate_item is not None and \
                self.widget_area_menu.annotation_button_group.checkedButton().text()=='Joint':
            self.xray_record.save_patch(joint_id=annotation_id,date=date,\
            rectItem=self.image_widget.image_scene.rect_annotate_item)
            self.widget_area_menu.update_table_view(row_name=area_name,signal='Completed')

        if self.image_widget.image_scene.polyline_annotate_item is not None and \
                self.widget_area_menu.annotation_button_group.checkedButton().text()=='Phantom':
            annotation_id = 'Phantom'
            self.xray_record.save_phantom_outline(bone_id=annotation_id,date=date,\
            plineItem=self.image_widget.image_scene.polyline_annotate_item)
            self.widget_area_menu.update_table_view(row_name=area_name,signal='Completed')

        if self.image_widget.image_scene.polyline_annotate_item is not None and \
                self.widget_area_menu.annotation_button_group.checkedButton().text()=='Landmark':

            self.xray_record.save_landmark(landmark_id=annotation_id,date=date,\
            plineItem=self.image_widget.image_scene.polyline_annotate_item)


        file_name = 'annotation_tracking_'+str(date)+'.csv'
        xray_id = self.xray_selection_menu.combobox_studyid.currentText()
        file_loc = os.path.join(os.path.join(self.output_loc,xray_id),file_name)
        df = self.widget_area_menu.tableView.model()._data
        save_csv(df,fileName=file_loc)





    def update_tracking_annotation(self):
        if self.xray_record is None:
            self.popupWindow = QMessageBox.question(self,'Warning!',
                                                    "No xray record loaded. Please create or load an x-ray record "
                                                    "before "
                                                    "saving the "
                                                    "score" ,
                                                    QMessageBox.Ok)
            return -1


        if self.widget_area_menu.line_edit_labels.text() == '':
            self.popupWindow = QMessageBox.question(self,'Warning!',
                                                    "Please select which bone or joint you wish to save" ,
                                                    QMessageBox.Ok)
            return -1

        if self.widget_area_menu.side_button_group.checkedButton() is None:
            self.popupWindow = QMessageBox.question(self,'Warning!',
                                                    "Please select the L or R before saving",
                                                    QMessageBox.Ok)


        dates     = np.array(self.xray_record.meta_table['acquisition_date'],dtype=np.int)
        filenames = np.array(self.xray_record.meta_table['file_name'])

        id = np.where(filenames == self.xray_selection_menu.combobox_xrayid.currentText())

        # print(self.xray_selection_menu.combobox_xrayid.currentText())
        # print(id)
        level1_name = self.xray_record.meta_table['organ'][id[0][0]]

        # level1_name = self.xray_record.meta_table['organ']
        side_name   = self.widget_area_menu.side_button_group.checkedButton().text()
        if side_name=='N/A':
            side_name = 'NA'
        level2_name = side_name
        level3_name = self.widget_area_menu.line_edit_labels.text()

        annotation_id = output_annotation_name(level1_name =level1_name,
                                               level2_name=level2_name,
                                               level3_name=level3_name)
        area_name = level3_name+'_'+side_name
        date = dates[id[0][0]]
        self.widget_area_menu.update_table_view(row_name=area_name,signal='Unsure')
        df = self.widget_area_menu.tableView.model()._data

        file_name = 'annotation_tracking_'+str(date)+'.csv'
        xray_id = self.xray_selection_menu.combobox_studyid.currentText()
        file_loc = os.path.join(os.path.join(self.output_loc,xray_id),file_name)
        save_csv(df,fileName=file_loc)


    def update_image_quality_score(self):
        if self.xray_record is None:
            self.popupWindow = QMessageBox.question(self,'Warning!',
                                                    "No xray record loaded. Please create or load an x-ray record "
                                                    "before "
                                                    "saving the "
                                                    "score" ,
                                                    QMessageBox.Ok)
            return -1



        dates     = np.array(self.xray_record.meta_table['acquisition_date'],dtype=np.int)
        filenames = np.array(self.xray_record.meta_table['file_name'])

        id = np.where(filenames == self.xray_selection_menu.combobox_xrayid.currentText())
        try:
            image_quality_array = np.array(self.xray_record.meta_table['image_quality'])
        except KeyError:
            image_quality_array = np.ones(dates.shape)


        image_quality_array[id[0][0]] = int(self.image_widget.toolbar.buttons['Good Image Quality'].isChecked())

        self.xray_record.meta_table['image_quality'] = image_quality_array
        self.xray_record.save_metadata()




    def update_tracking_score(self):
        if self.xray_record is None:
            self.popupWindow = QMessageBox.question(self,'Warning!',
                                                    "No xray record loaded. Please create or load an x-ray record "
                                                    "before "
                                                    "saving the "
                                                    "score" ,
                                                    QMessageBox.Ok)
            return -1


        if self.widget_score_menu.side_button_group.checkedButton() is None:
            self.popupWindow = QMessageBox.question(self,'Warning!',
                                                            "Please select a side to allocate the score" ,
                                                            QMessageBox.Ok)
            return -1



        dates     = np.array(self.xray_record.meta_table['acquisition_date'],dtype=np.int)
        filenames = np.array(self.xray_record.meta_table['file_name'])

        id = np.where(filenames == self.xray_selection_menu.combobox_xrayid.currentText())

        # print(self.xray_selection_menu.combobox_xrayid.currentText())
        # print(id)
        level1_name = self.xray_record.meta_table['organ'][id[0][0]]

        # level1_name = self.xray_record.meta_table['organ']
        side_name   = self.widget_score_menu.side_button_group.checkedButton().text()
        if side_name=='N/A':
            side_name = 'NA'
        level2_name = side_name
        level3_name = self.widget_score_menu.score_area_box.currentText()

        annotation_id = output_annotation_name(level1_name =level1_name,
                                               level2_name=level2_name,
                                               level3_name=level3_name)
        area_name = level3_name+'_'+side_name
        date = dates[id[0][0]]
        self.widget_area_menu.update_table_view(row_name=area_name,signal='Unsure')
        df = self.widget_area_menu.tableView.model()._data

        file_name = 'annotation_tracking_'+str(date)+'.csv'
        xray_id = self.xray_selection_menu.combobox_studyid.currentText()
        file_loc = os.path.join(os.path.join(self.output_loc,xray_id),file_name)
        save_csv(df,fileName=file_loc)

    def save_scores(self):
        if self.xray_record is None:
            self.popupWindow = QMessageBox.question(self,'Warning!',
                                                    "No xray record loaded. Please create or load an x-ray record "
                                                    "before "
                                                    "saving the "
                                                    "score" ,
                                                    QMessageBox.Ok)
        else:
            date = NameSignature(self.xray_selection_menu.combobox_xrayid.currentText()).year
            #self.xray_record.meta_table[]
            file_loc = os.path.join(self.xray_record.save_loc,'scores')
            #print(file_loc)
            file_loc = os.path.join(file_loc,date)
            file_name = os.path.join(file_loc,self.widget_score_menu.score_technique+'.csv')
            self.widget_score_menu.save_table_view(file_loc=file_name)


    def display_studies(self):
        if not os.path.isdir(self.output_loc):
            return -1
        studies = [f for f in os.listdir(self.output_loc) if os.path.isdir(os.path.join(self.output_loc,f))]
        for it in studies:
            self.xray_selection_menu.combobox_studyid.addItem(it)


    def display_xrays(self):
        """
        changes the list in the xray id box to be a list of filenames of images presemt in tehe metaloc of the selected
        study id and loads the last image in that list of file names
        """
        if self.xray_selection_menu.combobox_studyid.count()>0:
            study_name = self.xray_selection_menu.combobox_studyid.currentText()
            meta_loc   = os.path.join(self.output_loc,study_name)
            # meta_data  = pd.read_csv(os.path.join(meta_loc,'metadata.csv'))
            meta_data = load_csv(os.path.join(meta_loc,'metadata.csv'))
            dates      = meta_data['acquisition_date']
            fileNames  = meta_data['file_name']
            self.xray_selection_menu.combobox_xrayid.clear()
            for it in fileNames:
                self.xray_selection_menu.combobox_xrayid.addItem(it)
            meta_loc = os.path.join(self.output_loc,self.xray_selection_menu.combobox_studyid.currentText())
            self.xray_record = XrayData(image_name=None,xray_id=None,acquisition_date=None,meta_loc=meta_loc)
            # self.initialise_xray_record()
            self.load_selected_xrays()

    def initialise_xray_record(self):
        if not os.path.isdir(self.output_loc):
            return -1
        if self.xray_selection_menu.combobox_studyid.currentText() is not None:

            meta_loc = os.path.join(self.output_loc,self.xray_selection_menu.combobox_studyid.currentText())
            self.xray_record = XrayData(image_name=None,xray_id=None,acquisition_date=None,meta_loc=meta_loc)
            self.display_xrays()
            self.load_selected_xrays()

    def load_selected_xrays(self):
        """
        method that loads the xray corrsponding the the id being displayed in the study id box and the filename being
        displayed in the xray id box
        will read in the filename being isplyed in xray id and will look for the file in self.output_loc/study_id
        """
        meta_loc = os.path.join(self.output_loc,self.xray_selection_menu.combobox_studyid.currentText())
        # dates = np.array(self.xray_record.meta_table['acquisition_date'],dtype=np.int)
        file_names = np.array(self.xray_record.meta_table['file_name'])
        organs     = np.array(self.xray_record.meta_table['organ'])

        #
        #
        id =np.where(file_names==self.xray_selection_menu.combobox_xrayid.currentText())
        # print(dates)
        # print(self.xray_selection_menu.combobox_xrayid.currentText())
        # print(id)
        # image_name = self.xray_record.meta_table['file_name'][id[0][0]]#.to_numpy()[0]
        image_name = self.xray_selection_menu.combobox_xrayid.currentText()

        try:
            image_quality_array = np.array(self.xray_record.meta_table['image_quality'])
            image_qual_bool     = bool(int(float(image_quality_array[id[0][0]])))
            print(image_qual_bool)
            self.image_widget.toolbar.buttons['Good Image Quality'].setChecked(image_qual_bool)
            self.image_widget.toolbar.buttons['Bad Image Quality'].setChecked(not image_qual_bool)
        except KeyError:
            self.image_widget.toolbar.buttons['Good Image Quality'].setChecked(1)
            print("No image quality info present in metadata")

        #print(image_name)
        if os.path.isfile(os.path.join(meta_loc,image_name)):
            self.image_widget.load_image(file_name=os.path.join(meta_loc,image_name))

            print("Image quality is ={:}".format(int(self.image_widget.image_quality_flag)))
            self.display_image_info()
            # self.xray_selection_menu.xray_info_box_date.setText(str(dates[id[0][0]]))
            # self.xray_selection_menu.xray_info_box_organ.setText(organs[id[0][0]])


    def display_image_info(self):
        dates = np.array(self.xray_record.meta_table['acquisition_date'],dtype=np.int)
        file_names = np.array(self.xray_record.meta_table['file_name'])
        organs     = np.array(self.xray_record.meta_table['organ'])
        #
        #
        id =np.where(file_names==self.xray_selection_menu.combobox_xrayid.currentText())
        if len(id)!=0:
            if len(id[0])!=0:
                self.xray_selection_menu.xray_info_box_date.setText(str(dates[id[0][0]]))
                self.xray_selection_menu.xray_info_box_organ.setText(organs[id[0][0]])
            else:
                ('empty array for the id where the filenames = the combobox content')


    def display_all_current_annotations(self):
        im_loc = os.path.join(self.output_loc,self.xray_selection_menu.combobox_studyid.currentText())
        date = NameSignature(self.xray_selection_menu.combobox_xrayid.currentText()).year
        im_name = self.xray_selection_menu.combobox_xrayid.currentText()
        # self.xray_record.meta_table[]
        joint_loc = os.path.join(self.xray_record.save_loc, 'joint')
        joint_loc = os.path.join(joint_loc, date)
        bones_loc = os.path.join(self.xray_record.save_loc, 'bone')
        bones_loc = os.path.join(bones_loc, date)
        rects = [os.path.join(joint_loc, f) for f in os.listdir(joint_loc)]
        polys = [os.path.join(bones_loc, f) for f in os.listdir(bones_loc)]
        self.display_window = PlotWindow()

        for rect in rects:
            x = np.loadtxt(rect)
            self.display_window.plot(np.append(x[:, 0], x[0, 0]), np.append(x[:, 1], x[0, 1]))

        for poly in polys:
            x = np.loadtxt(poly)
            self.display_window.plot(x[:, 0], x[:, 1])

        im = cv2.imread(os.path.join(im_loc,im_name))
        self.display_window.imshow(im)




        self.display_window.show()






def main():
    app = QApplication([])
    window = InspectXRays()
    window.show()
    app.exec_()


if __name__=='__main__':
    main()