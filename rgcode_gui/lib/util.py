import os
from os import path

import subprocess

from rgcode.lib.process import process_files, set_run_parameters, process_image, get_file_list
from rgcode.lib.util import set_output_path

from PyQt5.QtWidgets import QFileDialog, QMessageBox

from PyQt5.QtCore import QThread, pyqtSignal

class External(QThread):
    """
    Runs a counter thread.
    """

    countChanged = pyqtSignal(tuple)

    # def __init__(self, input_folder, output_folder, selected_model, overlay, recursive, parent=True):
    #     QThread.__init__(self)
    #     self.input_folder = input_folder
    #     self.output_folder = output_folder
    #     self.selected_model = selected_model
    #     self.overlay = overlay
    #     self.recursive = recursive

    def __init__(self, path_list, run_settings, parent=True):
        QThread.__init__(self)
        self.path_list = path_list
        self.run_settings = run_settings
    

    def run(self):
        # count = 0
        # while count < TIME_LIMIT:
        #     count +=1
        #     time.sleep(1)

        # overlay_folder, file_list, rbpms_model, results = set_run_parameters(self.input_folder,
        # self.output_folder,
        # self.selected_model,
        # self.recursive,
        # self.overlay)

        overlay_folder, file_list, count_model, seg_model, results = set_run_parameters(self.path_list,
        self.run_settings)

        for n, file in enumerate(file_list):
            
            current_file = path.split(file_list[n])[-1]

            self.countChanged.emit((n, current_file))
            print(f"\nProcessing file {n+1} of {len(file_list)}")

            process_image(file, count_model, seg_model, results, self.run_settings, overlay_folder)

            if n == (len(file_list) - 1):
                current_file = "Finished!"
            else:
                current_file = path.split(file_list[n + 1])[-1]

            self.countChanged.emit((n + 1, current_file))


# model_list = []


def connect_events(win, count_models, seg_models):
    win.inputBrowse.pressed.connect(lambda: update_input(win, win.inputEdit))
    win.outputBrowse.pressed.connect(lambda: update_input(win, win.outputEdit))
    win.modelBrowse.pressed.connect(lambda: add_model(win.modelComboBox, count_models))
    win.seg_modelBrowse.pressed.connect(lambda: add_model(win.seg_modelComboBox, seg_models))
    win.startButton.pressed.connect(lambda: start_process(win, count_models, seg_models))
    win.stopButton.pressed.connect(lambda: stop_process(win))


def show_warning(title, message):
    msgbox = QMessageBox()
    msgbox.setIcon(QMessageBox.Warning)
    msgbox.setWindowTitle(title)
    msgbox.setText(message)
    msgbox.setStandardButtons(QMessageBox.Ok)
    msgbox.exec()


def update_input(parent, input_dialog):
    # displays a folder selection dialog and gets selection
    dialog = QFileDialog()
    folder = str(dialog.getExistingDirectory(dialog, "Select Directory"))

    # returns if Dialog was cancelled
    if folder == "":
        return
    
    # updates the input box
    input_dialog.setText(folder)


def update_model_list(combobox, model_list):
    combobox.clear()
    [combobox.addItem(model[1]) for model in model_list]


def add_model(combobox, model_list):
    dialog = QFileDialog()
    file = str(dialog.getOpenFileName(dialog, "Select File")[0])
    filename = path.split(file)[-1]

    # checks the model extension
    if path.splitext(filename)[-1] != ".h5":

        show_warning("File not compatible",
                    'Not a compatible model format!\nPlease select a ".h5" file.')

        return

    model_list.insert(0, [file, filename])

    update_model_list(combobox, model_list)

    # win.modelComboBox

    print(model_list)


def get_models_list(model_folder):
    # model_folder = "./rgcode/models"
    file_list = os.listdir(model_folder)

    complete_paths = [path.join(model_folder, file) for file in file_list]

    model_list = [[file, filename] for file, filename in zip(complete_paths, file_list)]

    return model_list


def start_process(win, count_models, seg_models):

    win.progressLabel.setText("Starting to process files...")

    # Gets the selected count model
    selected_model_index = win.modelComboBox.currentIndex()
    selected_model = count_models[selected_model_index][0]

    # Gets the selected count model
    selected_seg_model_index = win.seg_modelComboBox.currentIndex()
    selected_seg_model = seg_models[selected_model_index][0]


    # User selected angle
    user_angle = 45.0
    if hasattr(win, 'angleBox') and (not win.angleBox.isCheckable() or win.angleBox.isChecked()):
        try:
            user_angle = float(win.angleEdit.text())
        except (ValueError, TypeError):
            user_angle = 45.0

    # Checks options
    input_folder = win.inputEdit.text()
    if not path.isdir(input_folder) or input_folder == "":
        show_warning("Invalid input",
                    "The input doesn't exist or isn't a folder!\nInput a new one.")
        return

    resolution = 0
    if win.resolutionBox.isChecked() is True:
        try:
            resolution = float(win.resolutionEdit.text())
        except:
            pass
    
    threshold = 0.99
    if win.thresholdBox.isChecked() is True:
        try:
            threshold = float(win.thresholdEdit.text())
        except:
            pass

    bw = 150
    if win.bwBox.isChecked() is True:
        try:
            bw = int(win.bwEdit.text())
        except:
            pass

    run_settings = {
        "threshold" : threshold,
        "seg_threshold" : 0.5,
        "resolution" : resolution,
        "no_seg" : not win.checkSegmentation.isChecked(),
        "exp_seg" : False,
        "exp_cent" : False,                                         # ADD OPTION FOR THIS
        "recursive" : win.checkRecursive.isChecked(),
        "overlay" : win.checkOverlay.isChecked(),
        "isodensity" : win.checkIsodensity.isChecked(),
        "bandwidth" : bw,
        "vector" : win.checkSVG.isChecked(),
        "csv" : False,                                                # ADD OPTION FOR THIS
        "user_angle": user_angle,
    }

    run_settings["count_model_path"] = selected_model
    run_settings["seg_model_path"] = selected_seg_model
    run_settings["cmap"] = "magma"
    

    # Checks the custom output
    custom_output = win.outputBox.isChecked()
    output_folder = win.outputEdit.text()
    if not path.isdir(output_folder) and custom_output is True:
        show_warning("Invalid output",
                    "The output doesn't exist or isn't a folder!\nThe input folder will be used instead.")
    output_folder = set_output_path(output_folder, input_folder)

    run_settings["output_folder"] = output_folder
    

    total_progress = len(get_file_list(input_folder))
    win.progressBar.setMaximum(total_progress)

    
    win.process = External(input_folder, run_settings)
    win.process.countChanged.connect(win.onCountChanged)
    win.process.start()

    # enables the stop button
    win.stopButton.setEnabled(True)
    win.startButton.setEnabled(False)


def stop_process(win):
    print("Stopping processing thread...")

    win.process.terminate()

    # restores progress bar
    win.progressBar.setValue(0)
    win.progressLabel.setText("Stopped")

    # disables the stop button
    win.stopButton.setEnabled(False)
    win.startButton.setEnabled(True)

    print("Processing stopped")