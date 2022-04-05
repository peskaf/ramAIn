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

        self.curr_mode = None

        self.curr_plot_indices = None

        # set placeholders for spectral map and plot
        self.pic = Color("#F0F0F0")
        self.pic.setFixedSize(QSize(700,300)) #TODO: ??

        self.plot = Color("#F0F0F0")
        self.plot.setFixedSize(QSize(300,300)) #TODO: ??

        self.files_view.file_list.currentItemChanged.connect(self.update_file) # change of file -> update picture
        self.files_view.folder_changed.connect(self.update_folder)

        layout = QVBoxLayout()
        layout.addWidget(CollapseButton(self.files_view, "Choose File"))
        layout.addWidget(self.files_view)

        self.pic_plot_layout = QHBoxLayout()
        self.pic_plot_layout.addWidget(self.pic)
        self.pic_plot_layout.addWidget(self.plot)
        self.pic_plot_layout.setAlignment(Qt.AlignHCenter)

        layout.addLayout(self.pic_plot_layout)

        self.methods = Methods()
        self.methods.list.currentItemChanged.connect(self.update_plot_mode)
        # on manual CRR -> show LR on plot
        self.methods.cosmic_ray_removal.manual_removal_toggled.connect(self.display_linear_region)
        self.methods.cosmic_ray_removal.show_maxima_sig.connect(self.display_maxima)

        layout.addWidget(self.methods)
        
        layout.setAlignment(Qt.AlignTop)
        self.setLayout(layout)

        ##
        self.methods.cropping.apply_clicked.connect(self.crop)
        self.methods.cosmic_ray_removal.apply_clicked.connect(self.remove_spikes)



    def update_pic(self):
        if isinstance(self.pic, Color): # init state
            self.pic = SpectralMap(self.curr_data.averages, self)
            self.pic.setFixedSize(QSize(300,300)) # TODO: ??

            # initially show [0,0] data
            self.plot = SpectralPlot(self.curr_data.x_axis, self.curr_data.data[0,0], self)
            self.plot.setFixedSize(QSize(700,300)) # TODO: ??

            # click on picture -> update plot
            self.pic.image_view.getView().scene().sigMouseClicked.connect(self.update_plot_from_mouse_point)

            # remove placeholders -> needs to be backwards -> widgets would shift to lower position
            for i in reversed(range(self.pic_plot_layout.count())): 
                self.pic_plot_layout.itemAt(i).widget().setParent(None)

            # insert pic&plot
            self.pic_plot_layout.addWidget(self.plot)
            self.pic_plot_layout.addWidget(self.pic)
        else:
            self.pic.update_image(self.curr_data.averages)
            self.update_plot(0, 0)

    def update_plot(self, x : int, y : int):
        if x < self.curr_data.averages.shape[0] and x >= 0 and y < self.curr_data.averages.shape[1] and y >= 0:
            self.plot.update_data(self.curr_data.x_axis, self.curr_data.data[x,y])
            self.curr_plot_indices = (x, y)

    def update_plot_from_mouse_point(self): # inter func
        self.update_plot(int(np.floor(self.pic.mouse_point.x())), int(np.floor(self.pic.mouse_point.y())))

    def update_file(self, file : QListWidgetItem):
        self.curr_file = file.text()
        self.curr_data = Data(os.path.join(self.curr_folder, self.curr_file))
        self.update_pic()
        self.methods.reset()
        self.update_plot_mode(self.methods.list.currentItem())

    def update_folder(self, new_folder):
        self.curr_folder = new_folder

    # TODO: rename
    def send_new_data(self):
        try:
            new_region = (float(self.methods.cropping.input_plot_start.text()), float(self.methods.cropping.input_plot_end.text()))
            self.plot.update_region(new_region)
        except ValueError:
            pass
    
    def send_crr_new_data(self):
        try:
            new_region = (float(self.methods.cosmic_ray_removal.input_man_start.text()), float(self.methods.cosmic_ray_removal.input_man_end.text()))
            self.plot.update_region(new_region)
        except ValueError:
            pass

    def send_map_data(self):
        try:
            new_pos = (float(self.methods.cropping.input_map_left.text()), float(self.methods.cropping.input_map_top.text()))
            new_size = (float(self.methods.cropping.input_map_right.text()) - new_pos[0], float(self.methods.cropping.input_map_bottom.text()) - new_pos[1])
            self.pic.update_ROI(new_pos, new_size)
            self.pic.ROI.sigRegionChanged.emit(self.pic.ROI) # ROI does not have to change on invalid input -> send curr ROI info to QLineEdits
        except ValueError:
            pass
    
    # TODO rename
    def change_threshold(self, value):
        if self.curr_mode == "cosmic ray removal":
            self.pic.scatter_spikes(self.curr_data.get_spikes_positions(threshold=value))

    def update_plot_mode(self, new_mode : QListWidgetItem):
        # TODO: mode change only if some plot and map present -> if placeholder -> do nothing
        # nejen plot mode ale celkove vse

        if isinstance(self.pic, Color): # no file selected yet
            return

        if self.curr_mode == "cosmic ray removal":
            self.methods.cosmic_ray_removal.reset()

        if new_mode.text().lower() == "cropping":
            self.plot.set_mode(PlotMode.CROPPING)
            self.pic.set_mode(PlotMode.CROPPING)
            self.methods.set_current_widget(PlotMode.CROPPING)

            # plot connection to inputs
            self.plot.linear_region.sigRegionChanged.connect(self.methods.cropping.update_crop_plot_inputs)
            self.methods.cropping.input_plot_start.editingFinished.connect(self.send_new_data)
            self.methods.cropping.input_plot_end.editingFinished.connect(self.send_new_data)

            # send init linear region start and end to input lines
            self.plot.linear_region.sigRegionChanged.emit(self.plot.linear_region)

            # map connection to inputs
            self.pic.ROI.sigRegionChanged.connect(self.methods.cropping.update_crop_pic_inputs)
            self.methods.cropping.input_map_left.editingFinished.connect(self.send_map_data)
            self.methods.cropping.input_map_top.editingFinished.connect(self.send_map_data)
            self.methods.cropping.input_map_right.editingFinished.connect(self.send_map_data)
            self.methods.cropping.input_map_bottom.editingFinished.connect(self.send_map_data)

            # send init ROI position and size to input lines
            self.pic.ROI.sigRegionChanged.emit(self.pic.ROI)

        elif new_mode.text().lower() == "view":
            self.plot.set_mode(PlotMode.VIEW)
            self.pic.set_mode(PlotMode.VIEW)
            self.methods.set_current_widget(PlotMode.VIEW)

        elif new_mode.text().lower() == "cosmic ray removal":
            self.plot.set_mode(PlotMode.COSMIC_RAY_REMOVAL)
            self.pic.set_mode(PlotMode.COSMIC_RAY_REMOVAL)
            self.curr_data._calculate_Z_scores() # get new Z scores (in case something has changed, won't be recalculated until this mode is exited)
            self.pic.scatter_spikes(self.curr_data.get_spikes_positions(threshold=10)) # TODO add init threshold value
            self.methods.set_current_widget(PlotMode.COSMIC_RAY_REMOVAL)
            self.methods.cosmic_ray_removal.slider_slided.connect(self.change_threshold)
        
        elif new_mode.text().lower() == "background removal":
            self.plot.set_mode(PlotMode.BACKGROUND_REMOVAL)
            self.pic.set_mode(PlotMode.BACKGROUND_REMOVAL)
            self.methods.set_current_widget(PlotMode.BACKGROUND_REMOVAL)

        else:
            pass

        self.curr_mode = new_mode.text().lower()

    def display_linear_region(self, show):
        if show:
            self.plot.show_selection_region()
            self.plot.hide_crosshair()
    
            self.plot.linear_region.sigRegionChanged.connect(self.methods.cosmic_ray_removal.update_manual_input_region)
            self.methods.cosmic_ray_removal.input_man_start.editingFinished.connect(self.send_crr_new_data)
            self.methods.cosmic_ray_removal.input_man_end.editingFinished.connect(self.send_crr_new_data)
            self.plot.linear_region.sigRegionChanged.emit(self.plot.linear_region)
        else:
            self.plot.hide_selection_region()
            self.plot.show_crosshair()
    
    def display_maxima(self, show):
        if show:
            self.pic.update_image(self.curr_data.maxima)
        else:
            self.pic.update_image(self.curr_data.averages)
    
    def crop(self):
        self.curr_data.crop(*self.methods.cropping.get_params())
        self.pic.update_image(self.curr_data.averages)
        self.update_plot(0, 0)
        # TODO: jinak idealne
        self.update_plot_mode(QListWidgetItem("view"))
        self.update_plot_mode(QListWidgetItem("cropping"))
    
    def remove_spikes(self):
        if self.methods.cosmic_ray_removal.manual:
            self.curr_data.remove_manual(self.curr_plot_indices[0], self.curr_plot_indices[1], *self.methods.cosmic_ray_removal.get_params())
            self.update_plot(self.curr_plot_indices[0], self.curr_plot_indices[1])
        else: # automatic
            self.curr_data.remove_spikes(*self.methods.cosmic_ray_removal.get_params())
            self.update_plot(0, 0)

        self.pic.update_image(self.curr_data.averages)

        # needed ??
        self.update_plot_mode(QListWidgetItem("view"))
        self.update_plot_mode(QListWidgetItem("cosmic ray removal"))