from PySide6.QtWidgets import QFrame, QHBoxLayout, QVBoxLayout, QListWidgetItem, QMessageBox, QProgressDialog, QPushButton, QFileDialog
from PySide6.QtCore import QSize, Qt, Signal, QCoreApplication, QEventLoop
from PySide6.QtGui import QIcon, QPixmap

from widgets.color import Color
from widgets.files_view import FilesView
from widgets.collapse_button import CollapseButton
from widgets.preprocessing_methods import PreprocessingMethods
from widgets.spectral_map import SpectralMap
from widgets.spectral_plot import SpectralPlot
from widgets.plot_mode import PlotMode

from widgets.data import Data

from typing import Callable
import numpy as np
import os

class ManualPreprocessing(QFrame):
    update_progress = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)

        self.icon = QIcon("icons/view.svg") #TODO: change

        # Nothing set yet
        self.files_view = FilesView()

        self.curr_folder = self.files_view.data_folder
        self.curr_file = None
        self.curr_data = None

        self.curr_method = None

        self.curr_plot_indices = None

        # set placeholders for spectral map and plot
        self.spectral_map = Color("#F0F0F0")
        self.spectral_map.setFixedSize(QSize(700,300)) #TODO: ??

        self.plot = Color("#F0F0F0")
        self.plot.setFixedSize(QSize(300,300)) #TODO: ??

        self.files_view.file_list.currentItemChanged.connect(self.update_file) # change of file -> update picture
        self.files_view.folder_changed.connect(self.update_folder)

        layout = QVBoxLayout()
        layout.addWidget(CollapseButton(self.files_view, "Choose File"))
        layout.addWidget(self.files_view)

        self.map_plot_layout = QHBoxLayout()
        self.map_plot_layout.addWidget(self.spectral_map)
        self.map_plot_layout.addWidget(self.plot)
        self.map_plot_layout.setAlignment(Qt.AlignHCenter)

        layout.addLayout(self.map_plot_layout)

        self.methods = PreprocessingMethods()
        self.methods.method_changed.connect(self.update_method)

        self.save_button = QPushButton("Save")
        self.save_button.clicked.connect(self.save_file)
        self.save_button.setMaximumWidth(200)

        self.init_cropping()
        self.init_crr()
        self.init_bgr()
        self.init_linearization()

        self.init_file_error_widget()

        # disable method selection until some valid file is selected
        self.methods.list.setEnabled(False)

        layout.addWidget(self.methods)
        layout.addWidget(self.save_button)
        layout.addStretch()
        layout.setAlignment(Qt.AlignTop)

        self.setLayout(layout)

    def update_spectral_map(self): # gets updated on file change
        if self._is_placeholder(self.spectral_map): # init state
            self.spectral_map = SpectralMap(self.curr_data.averages, self)
            self.spectral_map.setFixedSize(QSize(300,300)) # TODO: ??

            # initially show [0,0] data
            self.plot = SpectralPlot(self.curr_data.x_axis, self.curr_data.data[0,0], self)
            self.curr_plot_indices = (0, 0)
            self.plot.setFixedSize(QSize(700,300)) # TODO: ??

            # update plot on picture click
            self.spectral_map.image_view.getView().scene().sigMouseClicked.connect(self._update_plot_from_mouse_point)

            # remove placeholder -> needs to be backwards -> widgets would shift to lower position
            for i in reversed(range(self.map_plot_layout.count())): 
                self.map_plot_layout.itemAt(i).widget().setParent(None)

            # insert plot and spectral map
            self.map_plot_layout.addWidget(self.plot)
            self.map_plot_layout.addWidget(self.spectral_map)
        else:
            self.spectral_map.update_image(self.curr_data.averages)
            self.update_plot(0, 0)

    def update_plot(self, x: int, y: int) -> None:
        # update plot on valid indices only
        if x < self.curr_data.averages.shape[0] and x >= 0 and y < self.curr_data.averages.shape[1] and y >= 0:
            self.plot.update_data(self.curr_data.x_axis, self.curr_data.data[x,y])
            self.curr_plot_indices = (x, y)

            # update also bg line on plot change
            if self.curr_method == self.methods.background_removal:
                self.bgr_update_plot()

    def _update_plot_from_mouse_point(self) -> None:
        self.update_plot(int(np.floor(self.spectral_map.mouse_point.x())), int(np.floor(self.spectral_map.mouse_point.y())))

    def update_file(self, file: QListWidgetItem) -> None:

        if file is None:
            # do nothing if no file is provided
            return
        else:
            temp_curr_file = file.text()

        try:
            self.curr_data = Data(os.path.join(self.curr_folder, temp_curr_file))
        except:
            self.file_error.show()
            return

        if not self.methods.list.isEnabled():
            self.methods.list.setEnabled(True)

        self.curr_file = temp_curr_file
        self.update_spectral_map()
        self.methods.reset()
        self.curr_method = self.methods.view

    def update_folder(self, new_folder):
        self.curr_folder = new_folder

    def cropping_plot_region_change(self):
        new_region = (float(self.methods.cropping.input_plot_start.text()), float(self.methods.cropping.input_plot_end.text()))
        self.plot.update_region(new_region)

    def crr_region_change(self):
        new_region = (float(self.methods.cosmic_ray_removal.input_manual_start.text()), float(self.methods.cosmic_ray_removal.input_manual_end.text()))
        self.plot.update_region(new_region)

    def cropping_map_region_change(self):
        new_pos = (float(self.methods.cropping.input_map_left.text()), float(self.methods.cropping.input_map_top.text()))
        new_size = (float(self.methods.cropping.input_map_right.text()) - new_pos[0], float(self.methods.cropping.input_map_bottom.text()) - new_pos[1])
        self.spectral_map.update_ROI(new_pos, new_size)

        # ROI does not have to change on invalid input -> send curr ROI info to QLineEdits
        self.spectral_map.ROI.sigRegionChanged.emit(self.spectral_map.ROI)

    def crr_change_threshold_on_map(self, value):
        self.spectral_map.scatter_spikes(self.curr_data.get_spikes_positions(threshold=value))

    def update_method(self, new_method: QFrame) -> None:

        self.curr_method.reset()
        self.curr_method = new_method

        if self.curr_method == self.methods.cropping:
            self.plot.set_mode(PlotMode.CROPPING)
            self.spectral_map.set_mode(PlotMode.CROPPING)

            # plot connection to inputs
            self.plot.linear_region.sigRegionChanged.connect(self.methods.cropping.update_crop_plot_inputs)

            # send init linear region start and end to input lines
            self.plot.linear_region.sigRegionChanged.emit(self.plot.linear_region)

            # map connection to inputs
            self.spectral_map.ROI.sigRegionChanged.connect(self.methods.cropping.update_crop_pic_inputs)

            # send init ROI position and size to input lines
            self.spectral_map.ROI.sigRegionChanged.emit(self.spectral_map.ROI)
    
        elif self.curr_method == self.methods.cosmic_ray_removal:
            self.plot.set_mode(PlotMode.COSMIC_RAY_REMOVAL)
            self.spectral_map.set_mode(PlotMode.COSMIC_RAY_REMOVAL)

            self.curr_data._calculate_Z_scores() # get new Z scores (in case something has changed, won't be recalculated until this mode is exited)
            self.spectral_map.scatter_spikes(self.curr_data.get_spikes_positions(threshold=10)) # TODO add init threshold value
        
        elif self.curr_method == self.methods.background_removal:
            self.plot.set_mode(PlotMode.BACKGROUND_REMOVAL)
            self.spectral_map.set_mode(PlotMode.BACKGROUND_REMOVAL)
            # will set poly on plot according to init config of params
            self.bgr_update_plot()

        else:
            # default (view) on some other method
            self.plot.set_mode(PlotMode.DEFAULT)
            self.spectral_map.set_mode(PlotMode.DEFAULT)
            

    def crr_show_plot_region(self, show):
        if show:
            self.plot.show_selection_region()
            self.plot.hide_crosshair()
            self.plot.linear_region.sigRegionChanged.connect(self.methods.cosmic_ray_removal.update_manual_input_region)
            self.plot.linear_region.sigRegionChanged.emit(self.plot.linear_region)
        else:
            self.plot.hide_selection_region()
            self.plot.show_crosshair()
    
    def crr_show_maxima(self, show):
        self.spectral_map.update_image(self.curr_data.maxima if show else self.curr_data.averages)

    def cropping_apply(self):
        self.curr_data.crop(*self.methods.cropping.get_params())
        self.spectral_map.update_image(self.curr_data.averages)
        # go back to (0,0) coordinates as prev coordinates may not exist anymore
        self.update_plot(0, 0)
        # reconnect plot and map for sizes adjusting
        self.update_method(self.methods.cropping)

    def linearization_apply(self):
        self.curr_data.linearize(self.methods.linearization.get_params()[0])
        self.spectral_map.update_image(self.curr_data.averages)
        self.update_plot(0, 0)

        self.update_method(self.methods.linearization)
    
    def crr_apply(self):
        auto_removal = self.methods.cosmic_ray_removal.auto_removal_btn.isChecked()

        if auto_removal:
            self.curr_data.remove_spikes(*self.methods.cosmic_ray_removal.get_params()[2:])
        else: # manual
            self.curr_data.remove_manual(self.curr_plot_indices[0], self.curr_plot_indices[1], *self.methods.cosmic_ray_removal.get_params()[:2])

        self.update_plot(self.curr_plot_indices[0], self.curr_plot_indices[1])
        self.spectral_map.update_image(self.curr_data.averages)

        self.update_method(self.methods.cosmic_ray_removal)

    def bgr_apply(self):
        math_morpho = self.methods.background_removal.math_morpho_btn.isChecked()
        ignore_water = self.methods.background_removal.ignore_water_band.isChecked()
        steps = np.multiply(*self.curr_data.data.shape[:2])

        if math_morpho:
            self.progress_bar_function(steps, self.curr_data.mm_algo_spectrum, ignore_water, self.update_progress)
        else:
            poly_deg = self.methods.background_removal.get_params()[0]
            self.progress_bar_function(steps, self.curr_data.vancouver, poly_deg, ignore_water, self.update_progress)

        self.update_plot(self.curr_plot_indices[0], self.curr_plot_indices[1])
        self.spectral_map.update_image(self.curr_data.averages)

        self.update_method(self.methods.background_removal)

    def init_cropping(self):
        # connect inputs signals to function slots
        self.methods.cropping.input_plot_start.editingFinished.connect(self.cropping_plot_region_change)
        self.methods.cropping.input_plot_end.editingFinished.connect(self.cropping_plot_region_change)
        self.methods.cropping.input_map_left.editingFinished.connect(self.cropping_map_region_change)
        self.methods.cropping.input_map_top.editingFinished.connect(self.cropping_map_region_change)
        self.methods.cropping.input_map_right.editingFinished.connect(self.cropping_map_region_change)
        self.methods.cropping.input_map_bottom.editingFinished.connect(self.cropping_map_region_change)
        self.methods.cropping.apply_clicked.connect(self.cropping_apply)

    def init_crr(self):
        # connect inputs signals to function slots
        self.methods.cosmic_ray_removal.threshold_changed.connect(self.crr_change_threshold_on_map)
        self.methods.cosmic_ray_removal.input_manual_start.editingFinished.connect(self.crr_region_change)
        self.methods.cosmic_ray_removal.input_manual_end.editingFinished.connect(self.crr_region_change)
        self.methods.cosmic_ray_removal.manual_removal_toggled.connect(self.crr_show_plot_region)
        self.methods.cosmic_ray_removal.show_maxima_toggled.connect(self.crr_show_maxima)
        self.methods.cosmic_ray_removal.threshold_changed.connect(self.crr_change_threshold_on_map)
        self.methods.cosmic_ray_removal.apply_clicked.connect(self.crr_apply)

    def init_bgr(self):
        # connect inputs signals to function slots
        self.methods.background_removal.poly_deg_changed.connect(self.bgr_change_poly_on_plot)
        self.methods.background_removal.ignore_water_band_toggled.connect(self.bgr_update_plot)
        self.methods.background_removal.math_morpho_toggled.connect(self.bgr_update_plot)
        self.methods.background_removal.apply_clicked.connect(self.bgr_apply)

    def init_linearization(self):
        # connect inputs signals to function slots
        self.methods.linearization.apply_clicked.connect(self.linearization_apply)

    def bgr_change_poly_on_plot(self, degree: int) -> None:
        ignore_water = self.methods.background_removal.ignore_water_band.isChecked()
        curr_spectrum = self.curr_data.data[self.curr_plot_indices[0], self.curr_plot_indices[1], :]
        poly_bg = self.curr_data.vancouver_poly_bg(curr_spectrum, degree, ignore_water)
        self.plot.plot_background(poly_bg)

    def bgr_update_plot(self) -> None:
        if self.methods.background_removal.math_morpho_btn.isChecked():
            ignore_water = self.methods.background_removal.ignore_water_band.isChecked()
            curr_spectrum = self.curr_data.data[self.curr_plot_indices[0], self.curr_plot_indices[1], :]
            mm_bg = self.curr_data._mm_aaa(curr_spectrum, ignore_water)
            self.plot.plot_background(mm_bg)
        else:
            # emit degree of poly that is currently set in line edit -> it will trigger `bgr_change_poly_on_plot` with right params
            self.methods.background_removal.emit_poly_deg_changed()

    def _is_placeholder(self, object) -> bool: # return if passed object is placeholder
        return isinstance(object, Color)

    def init_file_error_widget(self):
        self.file_error = QMessageBox()
        self.file_error.setIconPixmap(QPixmap("icons/x-circle.svg"))
        self.file_error.setText("File has invalide structure and cannot be loaded.")
        self.file_error.setInformativeText("RamAIn currently supports only .mat files originally produced by WITec spectroscopes. Sorry :(")
        self.file_error.setWindowTitle("Invalid file structure")
        self.file_error.setWindowIcon(QIcon("icons/message.svg"))
        self.file_error.setStandardButtons(QMessageBox.Ok)

    def make_progress_bar(self, maximum):
        self.files_view.setEnabled(False)
        self.methods.setEnabled(False)

        self.progress = QProgressDialog("Progress", "...", 0, maximum)
        self.progress.setValue(0)
        self.progress.setCancelButton(None)

        # style for progress bar that is inside progress dialog must be set here for some reason...
        self.progress.setStyleSheet(
            """
            QProgressBar {
                border: 1px solid;
                border-radius: 5px;
                text-align: center;
            }

            QProgressBar::chunk {
                background-color: rgb(248, 188, 36);
                width: 1px;
            }
            """
        )

        # hide borders, title and "X" in the top right corner
        self.progress.setWindowFlags(Qt.WindowTitleHint) # Qt.Dialog | Qt.FramelessWindowHint | Qt.WindowTitleHint
        self.progress.setWindowIcon(QIcon("icons/message.svg"))

        self.progress.setWindowTitle("Work in progress")
        self.update_progress.connect(self.set_progress)

    def set_progress(self):
        QCoreApplication.processEvents(QEventLoop.ExcludeUserInputEvents)
        val = self.progress.value()
        self.progress.setValue(val + 1)
    
    def destroy_progress_bar(self):
        self.files_view.setEnabled(True)
        self.methods.setEnabled(True)
        self.update_progress.disconnect()
        self.progress.deleteLater()

    # wrapper
    def progress_bar_function(self, progress_steps: int, function: Callable, *args, **kwargs):
        self.make_progress_bar(progress_steps)
        function(*args, **kwargs)
        self.destroy_progress_bar()

    def save_file(self):
        file_name, _ = QFileDialog.getSaveFileName(self, "Save Data", self.files_view.data_folder, filter="*.mat")
        self.curr_data.save_data(file_name)
        folder, file_name = os.path.split(file_name)

        
        self.files_view.data_folder = folder
        self.update_folder(folder)

        # do not update file on curr item change in the list -> item will be changed to the same one, no need for loading again
        self.files_view.file_list.currentItemChanged.disconnect()
        # update file list so that new file is visible
        self.files_view.update_list()
        # set that required file is visually selected
        self.files_view.set_curr_file(file_name)
        # connect again
        self.files_view.file_list.currentItemChanged.connect(self.update_file)

    def get_string_name(self):
        return "Manual Preprocessing"
