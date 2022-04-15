from PySide6.QtWidgets import QFrame, QHBoxLayout, QVBoxLayout, QListWidgetItem
from PySide6.QtCore import QSize, Qt

from widgets.color import Color
from widgets.files_view import FilesView
from widgets.collapse_button import CollapseButton
from widgets.methods import Methods
from widgets.spectral_map import SpectralMap
from widgets.spectral_plot import SpectralPlot
from widgets.plot_mode import PlotMode

from widgets.data import Data

import numpy as np
import os

class ManualPreprocessing(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)

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

        self.methods = Methods()
        self.methods.method_changed.connect(self.update_method)

        self.init_cropping()
        self.init_crr()
        self.init_bgr()

        # disable method selection until some valid file is selected
        self.methods.list.setEnabled(False)

        layout.addWidget(self.methods)
        
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

    def _update_plot_from_mouse_point(self) -> None:
        self.update_plot(int(np.floor(self.spectral_map.mouse_point.x())), int(np.floor(self.spectral_map.mouse_point.y())))

    def update_file(self, file: QListWidgetItem):
        
        temp_curr_file = file.text()
        try:
            self.curr_data = Data(os.path.join(self.curr_folder, temp_curr_file))
        except:
            print("EXCEPTION IN UPDATE_FILE")
            ... # TODO: show pop-up window that file has invalid structure
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

    def update_method(self, new_method: QFrame): #TODO: dat sem toho spolecneho predka vsech metod!

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
            # TODO: polynom update

        else:
            # default (view) on some other method
            print("DEFAULT CASE MET, SOLVE IT.") # TODO
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
        if show:
            self.spectral_map.update_image(self.curr_data.maxima)
        else:
            self.spectral_map.update_image(self.curr_data.averages)
    
    def cropping_apply(self):
        self.curr_data.crop(*self.methods.cropping.get_params())
        self.spectral_map.update_image(self.curr_data.averages)
        # go back to (0,0) coordinates as prev coordinates may not exist anymore
        self.update_plot(0, 0)
        # reconnect plot and map for sizes adjusting
        self.update_method(self.methods.cropping)
    
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
        ...

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
        self.methods.cosmic_ray_removal.threshold_changed.connect(self.crr_change_threshold_on_map)
        self.methods.cosmic_ray_removal.input_manual_start.editingFinished.connect(self.crr_region_change)
        self.methods.cosmic_ray_removal.input_manual_end.editingFinished.connect(self.crr_region_change)
        self.methods.cosmic_ray_removal.manual_removal_toggled.connect(self.crr_show_plot_region)
        self.methods.cosmic_ray_removal.show_maxima_toggled.connect(self.crr_show_maxima)
        self.methods.cosmic_ray_removal.threshold_changed.connect(self.crr_change_threshold_on_map)
        self.methods.cosmic_ray_removal.apply_clicked.connect(self.crr_apply)

    def init_bgr(self):
        # TODO: dopsat
        """
        self.methods.background_removal.poly_deg_changed.connect(...)
        self.methods.background_removal.ignore_water_band_toggled.connect(...)
        """

    def _is_placeholder(self, object) -> bool: # return if passed object is placeholder
        return isinstance(object, Color)
