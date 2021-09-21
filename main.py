from fbs_runtime.application_context.PyQt5 import ApplicationContext, cached_property

from PyQt5.QtGui import  QIcon
import csv
# from MainWindow import InspectXRays


#from Utils import *
from PyQt5.QtWidgets import QMainWindow
import sys,os


class AppContext(ApplicationContext):
    def run(self):
        self.main_window.show()
        return self.app.exec_()

    @cached_property
    def main_window(self):
        return QMainWindow()#ImageHandler(self.image_handler_icons)#(self)

    @cached_property
    def joint_list(self):
        return self.get_resource(os.path.join("config","joint_list.txt"))

    @cached_property
    def score_profiles(self):

        return {'PsA-MSS'      :  os.path.join("config","PsA-MSS.h5"),
                'Ratingen'     :  os.path.join("config","Ratingen.h5"),
                'Steinbrocker' :  os.path.join("config","Steinbrocker.h5"),
                'VdH-PsA'      :  os.path.join("config","VdH-PsA.h5")
        }

    @cached_property
    def image_handler_icons(self):
        return {
            "Draw Polyline": QIcon(self.get_resource(os.path.join("images","draw_poly.png"))),
            "Draw Rectangle": QIcon(self.get_resource(os.path.join("images","draw_rect.png"))),
            "Zoom Out": QIcon(self.get_resource(os.path.join("images","zoom_out.png"))),
            "Zoom In": QIcon(self.get_resource(os.path.join("images","zoom_in.png"))),
            "Undo":QIcon(self.get_resource(os.path.join("images","undo.png"))),
            "Redo":QIcon(self.get_resource(os.path.join("images","redo.png"))),
            "Clear Label":QIcon(self.get_resource(os.path.join("images","clear-icon-3.png")))
        }


if __name__ == '__main__':
    # appctxt = ApplicationContext()       # 1. Instantiate ApplicationContext
    # window = InspectXRays()
    appctxt = AppContext()
    # window.resize(250, 150)
    # window.show()
    # exit_code = appctxt.app.exec_()      # 2. Invoke appctxt.app.exec_()
    exit_code = appctxt.run()
    sys.exit(exit_code)