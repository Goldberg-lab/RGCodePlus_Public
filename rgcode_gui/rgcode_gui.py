# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'rgcode_gui/etc/gui.ui'
#
# Created by: PyQt5 UI code generator 5.12.3
#
# WARNING! All changes made in this file will be lost!
from os import path

root_dir = path.dirname(path.dirname(path.abspath(__file__)))

from rgcode_gui.lib.util import connect_events, get_models_list, update_model_list
from rgcode.lib.settings import default_count_model_path

from PyQt5 import QtCore, QtGui, QtWidgets

from PyQt5.QtCore import QThread, pyqtSignal


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(651, 440)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.inputBox = QtWidgets.QGroupBox(self.centralwidget)
        self.inputBox.setGeometry(QtCore.QRect(10, 10, 311, 51))
        self.inputBox.setObjectName("inputBox")
        self.inputEdit = QtWidgets.QLineEdit(self.inputBox)
        self.inputEdit.setGeometry(QtCore.QRect(10, 20, 211, 20))
        self.inputEdit.setObjectName("inputEdit")
        self.inputBrowse = QtWidgets.QPushButton(self.inputBox)
        self.inputBrowse.setGeometry(QtCore.QRect(230, 20, 75, 23))
        self.inputBrowse.setObjectName("inputBrowse")
        self.parametersBox = QtWidgets.QGroupBox(self.centralwidget)
        self.parametersBox.setGeometry(QtCore.QRect(10, 130, 311, 260)) 
        self.angleBox = QtWidgets.QGroupBox(self.parametersBox)
        self.angleBox.setGeometry(QtCore.QRect(10, 200, 291, 51))
        self.angleBox.setObjectName("angleBox")
        self.angleBox.setCheckable(True)
        self.angleBox.setChecked(False)
        self.angleEdit = QtWidgets.QLineEdit(self.angleBox)
        self.angleEdit.setGeometry(QtCore.QRect(10, 20, 271, 20))
        self.angleEdit.setText("45")
        self.angleEdit.setObjectName("angleEdit")
        self.parametersBox.setObjectName("parametersBox")
        self.resolutionBox = QtWidgets.QGroupBox(self.parametersBox)
        self.resolutionBox.setGeometry(QtCore.QRect(10, 20, 291, 51))
        self.resolutionBox.setCheckable(True)
        self.resolutionBox.setChecked(False)
        self.resolutionBox.setObjectName("resolutionBox")
        self.resolutionEdit = QtWidgets.QLineEdit(self.resolutionBox)
        self.resolutionEdit.setGeometry(QtCore.QRect(10, 20, 271, 20))
        self.resolutionEdit.setText("")
        self.resolutionEdit.setObjectName("resolutionEdit")
        self.thresholdBox = QtWidgets.QGroupBox(self.parametersBox)
        self.thresholdBox.setGeometry(QtCore.QRect(10, 80, 291, 51))
        self.thresholdBox.setCheckable(True)
        self.thresholdBox.setChecked(False)
        self.thresholdBox.setObjectName("thresholdBox")
        self.thresholdEdit = QtWidgets.QLineEdit(self.thresholdBox)
        self.thresholdEdit.setGeometry(QtCore.QRect(10, 20, 271, 20))
        self.thresholdEdit.setObjectName("thresholdEdit")
        self.bwBox = QtWidgets.QGroupBox(self.parametersBox)
        self.bwBox.setGeometry(QtCore.QRect(10, 140, 291, 51))
        self.bwBox.setCheckable(True)
        self.bwBox.setChecked(False)
        self.bwBox.setObjectName("bwBox")
        self.bwEdit = QtWidgets.QLineEdit(self.bwBox)
        self.bwEdit.setGeometry(QtCore.QRect(10, 20, 271, 20))
        self.bwEdit.setObjectName("bwEdit")
        self.modelBox = QtWidgets.QGroupBox(self.centralwidget)
        self.modelBox.setGeometry(QtCore.QRect(10, 70, 311, 51))
        self.modelBox.setObjectName("modelBox")
        self.modelBrowse = QtWidgets.QPushButton(self.modelBox)
        self.modelBrowse.setGeometry(QtCore.QRect(230, 20, 75, 23))
        self.modelBrowse.setObjectName("modelBrowse")
        self.modelComboBox = QtWidgets.QComboBox(self.modelBox)
        self.modelComboBox.setGeometry(QtCore.QRect(10, 20, 211, 22))
        self.modelComboBox.setObjectName("modelComboBox")
        self.progressBox = QtWidgets.QGroupBox(self.centralwidget)
        self.progressBox.setGeometry(QtCore.QRect(330, 260, 311, 71))
        self.progressBox.setObjectName("progressBox")
        self.progressLabel = QtWidgets.QLabel(self.progressBox)
        self.progressLabel.setGeometry(QtCore.QRect(10, 20, 281, 16))
        self.progressLabel.setObjectName("progressLabel")
        self.progressBar = QtWidgets.QProgressBar(self.progressBox)
        self.progressBar.setGeometry(QtCore.QRect(10, 40, 291, 23))
        self.progressBar.setProperty("value", 24)
        self.progressBar.setObjectName("progressBar")
        self.outputBox = QtWidgets.QGroupBox(self.centralwidget)
        self.outputBox.setGeometry(QtCore.QRect(330, 10, 311, 51))
        self.outputBox.setCheckable(True)
        self.outputBox.setChecked(False)
        self.outputBox.setObjectName("outputBox")
        self.outputEdit = QtWidgets.QLineEdit(self.outputBox)
        self.outputEdit.setGeometry(QtCore.QRect(10, 20, 211, 20))
        self.outputEdit.setObjectName("outputEdit")
        self.outputBrowse = QtWidgets.QPushButton(self.outputBox)
        self.outputBrowse.setGeometry(QtCore.QRect(230, 20, 75, 23))
        self.outputBrowse.setObjectName("outputBrowse")
        self.startButton = QtWidgets.QPushButton(self.centralwidget)
        self.startButton.setGeometry(QtCore.QRect(470, 380, 75, 23))
        self.startButton.setObjectName("startButton")
        self.stopButton = QtWidgets.QPushButton(self.centralwidget)
        self.stopButton.setEnabled(False)
        self.stopButton.setGeometry(QtCore.QRect(560, 380, 75, 23))
        self.stopButton.setObjectName("stopButton")
        self.seg_modelBox = QtWidgets.QGroupBox(self.centralwidget)
        self.seg_modelBox.setGeometry(QtCore.QRect(330, 70, 311, 51))
        self.seg_modelBox.setCheckable(False)
        self.seg_modelBox.setObjectName("seg_modelBox")
        self.seg_modelBrowse = QtWidgets.QPushButton(self.seg_modelBox)
        self.seg_modelBrowse.setGeometry(QtCore.QRect(230, 20, 75, 23))
        self.seg_modelBrowse.setObjectName("seg_modelBrowse")
        self.seg_modelComboBox = QtWidgets.QComboBox(self.seg_modelBox)
        self.seg_modelComboBox.setGeometry(QtCore.QRect(10, 20, 211, 22))
        self.seg_modelComboBox.setObjectName("seg_modelComboBox")
        self.optionsBox = QtWidgets.QGroupBox(self.centralwidget)
        self.optionsBox.setGeometry(QtCore.QRect(330, 130, 311, 131))
        self.optionsBox.setObjectName("optionsBox")
        self.checkOverlay = QtWidgets.QCheckBox(self.optionsBox)
        self.checkOverlay.setGeometry(QtCore.QRect(10, 40, 271, 17))
        self.checkOverlay.setObjectName("checkOverlay")
        self.checkSegmentation = QtWidgets.QCheckBox(self.optionsBox)
        self.checkSegmentation.setGeometry(QtCore.QRect(10, 100, 271, 17))
        self.checkSegmentation.setChecked(True)
        self.checkSegmentation.setObjectName("checkSegmentation")
        self.checkIsodensity = QtWidgets.QCheckBox(self.optionsBox)
        self.checkIsodensity.setGeometry(QtCore.QRect(10, 60, 271, 17))
        self.checkIsodensity.setChecked(True)
        self.checkIsodensity.setObjectName("checkIsodensity")
        self.checkRecursive = QtWidgets.QCheckBox(self.optionsBox)
        self.checkRecursive.setGeometry(QtCore.QRect(10, 20, 271, 17))
        self.checkRecursive.setObjectName("checkRecursive")
        self.checkSVG = QtWidgets.QCheckBox(self.optionsBox)
        self.checkSVG.setGeometry(QtCore.QRect(10, 80, 271, 17))
        self.checkSVG.setChecked(False)
        self.checkSVG.setObjectName("checkSVG")
        MainWindow.setCentralWidget(self.centralwidget)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "RGCode"))
        self.inputBox.setTitle(_translate("MainWindow", "Input folder or file"))
        self.inputBrowse.setText(_translate("MainWindow", "Browse"))
        self.parametersBox.setTitle(_translate("MainWindow", "Options"))
        self.resolutionBox.setTitle(_translate("MainWindow", "Specify the resolution manually (pixels/µm)"))
        self.thresholdBox.setTitle(_translate("MainWindow", "Specify the threshold of the prediction map"))
        self.angleBox.setTitle(_translate("MainWindow", "Quadrant rotation angle (degrees)"))
        self.thresholdEdit.setText(_translate("MainWindow", "0.99"))
        self.bwBox.setTitle(_translate("MainWindow", "Specify the isodensity bandwidth"))
        self.bwEdit.setText(_translate("MainWindow", "100"))
        self.modelBox.setTitle(_translate("MainWindow", "Counting model selection"))
        self.modelBrowse.setText(_translate("MainWindow", "Browse"))
        self.progressBox.setTitle(_translate("MainWindow", "Progress"))
        self.progressLabel.setText(_translate("MainWindow", "Waiting to start..."))
        self.outputBox.setTitle(_translate("MainWindow", "Custom output folder"))
        self.outputBrowse.setText(_translate("MainWindow", "Browse"))
        self.startButton.setText(_translate("MainWindow", "Start"))
        self.stopButton.setText(_translate("MainWindow", "Stop"))
        self.seg_modelBox.setTitle(_translate("MainWindow", "Segmentation model selection"))
        self.seg_modelBrowse.setText(_translate("MainWindow", "Browse"))
        self.optionsBox.setTitle(_translate("MainWindow", "Options"))
        self.checkOverlay.setText(_translate("MainWindow", "Create an overlay image with the model output"))
        self.checkSegmentation.setText(_translate("MainWindow", "Segment the retina and measure area and density"))
        self.checkIsodensity.setText(_translate("MainWindow", "Export an isodensity map of the retina"))
        self.checkRecursive.setText(_translate("MainWindow", "Look for pictures in subfolders of the input folder"))
        self.checkSVG.setText(_translate("MainWindow", "Export the isodensity map as SVG"))

    
    def onCountChanged(self, value):
        value, file = value
        self.progressBar.setValue(value)

        if file == "Finished!":
            text = file
            # disables the stop button
            self.stopButton.setEnabled(False)
            self.startButton.setEnabled(True)
        else:
            text = f"Processing {file}..."

        self.progressLabel.setText(text)


    def update_gui(self):
        count_models = get_models_list(f"{root_dir}/rgcode/models/count")
        update_model_list(self.modelComboBox, count_models)
        seg_models = get_models_list(f"{root_dir}/rgcode/models/segmentation")
        update_model_list(self.seg_modelComboBox, seg_models)

        self.progressBar.setValue(0)

        connect_events(self, count_models, seg_models)



# if __name__ == "__main__":
#     import sys
#     app = QtWidgets.QApplication(sys.argv)
#     MainWindow = QtWidgets.QMainWindow()
#     ui = Ui_MainWindow()
#     ui.setupUi(MainWindow)
#     MainWindow.show()
#     sys.exit(app.exec_())


def main():
    import sys
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    ui.update_gui()
    MainWindow.show()
    sys.exit(app.exec_())


main()
