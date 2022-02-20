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
        self.files_view = FilesView(parent=self)

        self.curr_folder = self.files_view.data_folder
        self.curr_file = None
        self.curr_data = None

        # set placeholders for spectral map and plot
        self.pic = Color("#F0F0F0")
        self.pic.setFixedSize(QSize(700,300)) #TODO: ??

        self.plot = Color("#F0F0F0")
        self.plot.setFixedSize(QSize(300,300)) #TODO: ??

        self.files_view.list.currentItemChanged.connect(self.update_file) # change of file -> update picture
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
        layout.addWidget(self.methods)
        

        layout.setAlignment(Qt.AlignTop)
        self.setLayout(layout)

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

    def send_map_data(self):
        try:
            new_pos = (float(self.methods.cropping.input_map_ULX.text()), float(self.methods.cropping.input_map_ULY.text()))
            new_size = (float(self.methods.cropping.input_map_LRX.text()) - new_pos[0], float(self.methods.cropping.input_map_LRY.text()) - new_pos[1])
            self.pic.update_ROI(new_pos, new_size)
        except ValueError:
            pass

    def update_plot_mode(self, new_mode : QListWidgetItem):
        # nejen plot mode ale celkove vse

        if new_mode.text().lower() == "cropping":
            self.plot.set_mode(PlotMode.CROPPING)
            self.pic.set_mode(PlotMode.CROPPING)
            self.methods.set_current_widget(PlotMode.CROPPING)

            # plot connection to inputs
            self.plot.linear_region.sigRegionChanged.connect(self.methods.cropping.update_crop_plot_region)
            self.methods.cropping.input_plot_start.editingFinished.connect(self.send_new_data)
            self.methods.cropping.input_plot_end.editingFinished.connect(self.send_new_data)

            # send init linear region start and end to input lines
            self.plot.linear_region.sigRegionChanged.emit(self.plot.linear_region)

            # map connection to inputs
            self.pic.ROI.sigRegionChanged.connect(self.methods.cropping.update_crop_pic_region)
            self.methods.cropping.input_map_ULX.editingFinished.connect(self.send_map_data)
            self.methods.cropping.input_map_ULY.editingFinished.connect(self.send_map_data)
            self.methods.cropping.input_map_LRX.editingFinished.connect(self.send_map_data)
            self.methods.cropping.input_map_LRY.editingFinished.connect(self.send_map_data)

            # send init ROI position and size to input lines
            self.pic.ROI.sigRegionChanged.emit(self.pic.ROI)

        elif new_mode.text().lower() == "view":
            self.plot.set_mode(PlotMode.VIEW)
            self.pic.set_mode(PlotMode.VIEW)
            self.methods.set_current_widget(PlotMode.VIEW)
        else:
            pass