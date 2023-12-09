from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QVBoxLayout,
    QListWidgetItem,
    QMessageBox,
    QProgressDialog,
    QPushButton,
    QFileDialog,
    QWidget,
)
from PySide6.QtCore import QSize, Qt, Signal, QCoreApplication, QEventLoop
from PySide6.QtGui import QIcon, QPixmap

from ..widgets.color import Color
from ..widgets.files_view import FilesView
from ..widgets.collapse_button import CollapseButton
from ..widgets.preprocessing_methods import PreprocessingMethods
from ..widgets.spectral_map import SpectralMapGraph
from ..widgets.spectral_plot import SpectralPlot
from ..widgets.plot_mode import PlotMode

from model.spectal_map import SpectralMap

from utils.settings import SETTINGS

from typing import Callable
import numpy as np
import os


class ManualPreprocessing(QFrame):
    """
    A widget for selection of methods, parameters and methods application for manual preprocessing.
    """

    # signal that progress in progress bar should be updatet
    update_progress = Signal()

    def __init__(self, parent: QWidget = None) -> None:
        """
        The constructor for manual preprocessing menu page that allows selection and application of the methods
        on selected files, and its visualization.

        Parameters:
            parent (QWidget): Parent widget of this widget. Default: None.
        """

        super().__init__(parent)
        self.parent = parent

        self.icon = QIcon("src/resources/icons/monitor.svg")

        # Nothing set yet
        self.files_view = FilesView(format=".mat", parent=self)

        self.curr_folder = self.files_view.data_folder
        self.curr_file = None
        self.curr_data = None

        self.curr_method = None

        self.curr_plot_indices = None

        # set placeholders for spectral map and plot
        self.spectral_map_graph = Color("#F0F0F0", self)
        self.spectral_map_graph.setFixedSize(QSize(700, 300))

        self.plot = Color("#F0F0F0", self)
        self.plot.setFixedSize(QSize(300, 300))

        self.files_view.file_list.currentItemChanged.connect(
            self.update_file
        )  # change of file -> update picture
        self.files_view.folder_changed.connect(self.update_folder)

        self.map_plot_layout = QHBoxLayout()
        self.map_plot_layout.addWidget(self.spectral_map_graph)
        self.map_plot_layout.addWidget(self.plot)
        self.map_plot_layout.setAlignment(Qt.AlignHCenter)

        self.methods = PreprocessingMethods(self)
        self.methods.method_changed.connect(self.update_method)

        self.reload_discard_button = QPushButton("Reload / Discard Changes")
        self.reload_discard_button.clicked.connect(self.discard_changes)
        self.reload_discard_button.setMaximumWidth(400)

        self.save_button = QPushButton("Save File")
        self.save_button.clicked.connect(self.save_file)
        self.save_button.setMaximumWidth(400)

        buttons_layout = QHBoxLayout()
        buttons_layout.addWidget(self.reload_discard_button)
        buttons_layout.addStretch()
        buttons_layout.addWidget(self.save_button)

        # make widgets for params selection
        self.init_cropping()
        self.init_crr()
        self.init_bgr()
        self.init_linearization()
        self.init_smoothing()

        self.init_file_error_widget()

        # disable method selection + buttons until some valid file is selected
        self.methods.list.setEnabled(False)
        self.save_button.setEnabled(False)
        self.reload_discard_button.setEnabled(False)

        layout = QVBoxLayout()
        layout.addWidget(CollapseButton(self.files_view, "Choose File", self))
        layout.addWidget(self.files_view)
        layout.addLayout(self.map_plot_layout)
        layout.addWidget(self.methods)
        layout.addLayout(buttons_layout)
        layout.addStretch()
        layout.setAlignment(Qt.AlignTop)

        self.setLayout(layout)

    def update_spectral_map(self) -> None:  # gets updated on file change
        """
        A function to update spectral map according to `self.curr_data`.
        """

        if self._is_placeholder(self.spectral_map_graph):  # init state
            self.spectral_map_graph = SpectralMapGraph(self.curr_data.averages, self)
            self.spectral_map_graph.setFixedSize(QSize(300, 300))

            # initially show [0,0] data
            self.plot = SpectralPlot(
                self.curr_data.x_axis, self.curr_data.data[0, 0], self
            )
            self.curr_plot_indices = (0, 0)
            self.plot.setFixedSize(QSize(700, 300))

            # update plot on picture click
            self.spectral_map_graph.image_view.getView().scene().sigMouseClicked.connect(
                self._update_plot_from_mouse_point
            )

            # remove placeholder -> needs to be backwards -> widgets would shift to lower position
            for i in reversed(range(self.map_plot_layout.count())):
                self.map_plot_layout.itemAt(i).widget().setParent(None)

            # insert plot and spectral map
            self.map_plot_layout.addWidget(self.plot)
            self.map_plot_layout.addWidget(self.spectral_map_graph)
        else:
            self.spectral_map_graph.update_image(self.curr_data.averages)
            self.update_plot(0, 0)

    def update_plot(self, x: int, y: int) -> None:
        """
        A function to update spectral plot based on provided position in the spectral map.

        Parameters:
            x (int): x coordinate (row) in the spectral map.
            y (int): y coordinate (column) in the spectral map.
        """
        # update plot on valid indices only
        if (
            x < self.curr_data.averages.shape[0]
            and x >= 0
            and y < self.curr_data.averages.shape[1]
            and y >= 0
        ):
            self.plot.update_data(self.curr_data.x_axis, self.curr_data.data[x, y])
            self.curr_plot_indices = (x, y)

            # update also bg line on plot change
            if self.curr_method == self.methods.background_removal:
                self.bgr_update_plot()
            elif self.curr_method == self.methods.smoothing:
                self.smoothing_change_on_plot()

    def _update_plot_from_mouse_point(self) -> None:
        """
        A function to floor mouse point and convert it to correct types, calling
        `update_plot` with converted points afterwadrs.
        """

        self.update_plot(
            int(np.floor(self.spectral_map_graph.mouse_point.x())),
            int(np.floor(self.spectral_map_graph.mouse_point.y())),
        )

    def update_file(self, file: QListWidgetItem) -> None:
        """
        A function to read data from newly selected file and displaying it.
        """

        if file is None:
            return  # do nothing if no file is provided
        else:
            temp_curr_file = file.text()

        try:
            self.curr_data = SpectralMap(os.path.join(self.curr_folder, temp_curr_file))
        except:
            self.file_error.show()
            return

        if not self.methods.list.isEnabled():
            self.methods.list.setEnabled(True)
            self.save_button.setEnabled(True)
            self.reload_discard_button.setEnabled(True)

        self.curr_file = temp_curr_file
        self.update_spectral_map()
        self.methods.reset()
        self.curr_method = self.methods.view

    def update_folder(self, new_folder: str) -> None:
        """
        A function to assign provided `new_folder` to `self.curr_folder`.
        """
        self.curr_folder = new_folder

    def update_method(self, new_method: QFrame) -> None:
        """
        A function to change `self.curr_method` to provided `new_method`, performing
        corresponding actions based on the `new_method` (signals connectiong to the plots, etc.).
        """

        self.curr_method.reset()
        self.curr_method = new_method

        if self.curr_method == self.methods.cropping:
            self.plot.set_mode(PlotMode.CROPPING)
            self.spectral_map_graph.set_mode(PlotMode.CROPPING)

            # plot connection to inputs
            self.plot.linear_region.sigRegionChanged.connect(
                self.methods.cropping.update_crop_plot_inputs
            )

            # send init linear region start and end to input lines
            self.plot.linear_region.sigRegionChanged.emit(self.plot.linear_region)

            # map connection to inputs
            self.spectral_map_graph.ROI.sigRegionChanged.connect(
                self.methods.cropping.update_crop_pic_inputs
            )

            # send init ROI position and size to input lines
            self.spectral_map_graph.ROI.sigRegionChanged.emit(
                self.spectral_map_graph.ROI
            )

        elif self.curr_method == self.methods.cosmic_ray_removal:
            self.plot.set_mode(PlotMode.COSMIC_RAY_REMOVAL)
            self.spectral_map_graph.set_mode(PlotMode.COSMIC_RAY_REMOVAL)

            # show spikes positions to the user
            self.curr_data._calculate_spikes_indices()
            self.spectral_map_graph.scatter_spikes(
                self.curr_data._spike_info["map_indices"]
            )

        elif self.curr_method == self.methods.background_removal:
            self.plot.set_mode(PlotMode.BACKGROUND_REMOVAL)
            self.spectral_map_graph.set_mode(PlotMode.BACKGROUND_REMOVAL)
            # will set poly on plot according to init config of params
            self.bgr_update_plot()

        # TODO: note that the plotting modes are not general enough
        elif self.curr_method == self.methods.smoothing:
            self.plot.set_mode(PlotMode.BACKGROUND_REMOVAL)
            self.spectral_map_graph.set_mode(PlotMode.BACKGROUND_REMOVAL)
            # will set poly on plot according to init config of params
            self.smoothing_change_on_plot()

        else:
            # default (view) on some other method
            self.plot.set_mode(PlotMode.DEFAULT)
            self.spectral_map_graph.set_mode(PlotMode.DEFAULT)

    def cropping_plot_region_change(self) -> None:
        """
        A function to change selection region on the spectral plot based on the inputs in the cropping widget.
        """

        new_region = (
            float(self.methods.cropping.input_plot_start.text()),
            float(self.methods.cropping.input_plot_end.text()),
        )
        self.plot.update_region(new_region)

    def cropping_map_region_change(self) -> None:
        """
        A function to change ROI on the spectral map based on the inputs in the cropping widget.
        """

        new_pos = (
            float(self.methods.cropping.input_map_left.text()),
            float(self.methods.cropping.input_map_top.text()),
        )
        new_size = (
            float(self.methods.cropping.input_map_right.text()) - new_pos[0],
            float(self.methods.cropping.input_map_bottom.text()) - new_pos[1],
        )
        self.spectral_map_graph.update_ROI(new_pos, new_size)

        # ROI does not have to change on invalid input -> send curr ROI info to QLineEdits
        self.spectral_map_graph.ROI.sigRegionChanged.emit(self.spectral_map_graph.ROI)

    def crr_region_change(self) -> None:
        """
        A function to change selection region on the spectral plot based on the inputs in the CRR widget.
        """

        new_region = (
            float(self.methods.cosmic_ray_removal.input_manual_start.text()),
            float(self.methods.cosmic_ray_removal.input_manual_end.text()),
        )
        self.plot.update_region(new_region)

    def crr_show_plot_region(self, show: bool) -> None:
        """
        A funtion to show selection region on crr method. Triggered on manual crr selection.
        """

        if show:
            self.plot.show_selection_region()
            self.plot.hide_crosshair()
            self.plot.linear_region.sigRegionChanged.connect(
                self.methods.cosmic_ray_removal.update_manual_input_region
            )
            self.plot.linear_region.sigRegionChanged.emit(self.plot.linear_region)
        else:
            self.plot.hide_selection_region()
            self.plot.show_crosshair()

    def crr_show_maxima(self, show: bool) -> None:
        """
        A function to display maxima instead of averages on the spectral map.
        """

        self.spectral_map_graph.update_image(
            self.curr_data.maxima if show else self.curr_data.averages
        )

    def init_cropping(self) -> None:
        """
        A function to connect signals to inputs in cropping method parameter selection.
        """

        # connect inputs signals to function slots
        self.methods.cropping.input_plot_start.editingFinished.connect(
            self.cropping_plot_region_change
        )
        self.methods.cropping.input_plot_end.editingFinished.connect(
            self.cropping_plot_region_change
        )
        self.methods.cropping.input_map_left.editingFinished.connect(
            self.cropping_map_region_change
        )
        self.methods.cropping.input_map_top.editingFinished.connect(
            self.cropping_map_region_change
        )
        self.methods.cropping.input_map_right.editingFinished.connect(
            self.cropping_map_region_change
        )
        self.methods.cropping.input_map_bottom.editingFinished.connect(
            self.cropping_map_region_change
        )
        self.methods.cropping.apply_clicked.connect(self.cropping_apply)

    def init_crr(self) -> None:
        """
        A function to connect signals to inputs in CRR method parameter selection.
        """

        # connect inputs signals to function slots
        self.methods.cosmic_ray_removal.input_manual_start.editingFinished.connect(
            self.crr_region_change
        )
        self.methods.cosmic_ray_removal.input_manual_end.editingFinished.connect(
            self.crr_region_change
        )
        self.methods.cosmic_ray_removal.manual_removal_toggled.connect(
            self.crr_show_plot_region
        )
        self.methods.cosmic_ray_removal.show_maxima_toggled.connect(
            self.crr_show_maxima
        )
        self.methods.cosmic_ray_removal.apply_clicked.connect(self.crr_apply)

    def init_bgr(self) -> None:
        """
        A function to connect signals to inputs in background removal method parameter selection.
        """

        # connect inputs signals to function slots
        self.methods.background_removal.poly_deg_changed.connect(
            self.bgr_change_poly_on_plot
        )
        self.methods.background_removal.ignore_water_band_toggled.connect(
            self.bgr_update_plot
        )
        self.methods.background_removal.math_morpho_toggled.connect(
            self.bgr_update_plot
        )
        self.methods.background_removal.apply_clicked.connect(self.bgr_apply)

    def init_linearization(self) -> None:
        """
        A function to connect signals to inputs in linearization method parameter selection.
        """

        # connect inputs signals to function slots
        self.methods.linearization.apply_clicked.connect(self.linearization_apply)

    def init_smoothing(self) -> None:
        """
        A function to connect signals to inputs in smoothing method parameter selection.
        """

        # connect inputs signals to function slots
        self.methods.smoothing.poly_order_changed.connect(self.smoothing_change_on_plot)
        self.methods.smoothing.diff_changed.connect(self.smoothing_change_on_plot)
        self.methods.smoothing.lambda_changed.connect(self.smoothing_change_on_plot)
        self.methods.smoothing.window_length_changed.connect(
            self.smoothing_change_on_plot
        )
        self.methods.smoothing.savgol_toggled.connect(self.smoothing_change_on_plot)
        self.methods.smoothing.apply_clicked.connect(self.smoothing_apply)

    def cropping_apply(self) -> None:
        """
        A function to apply cropping method on the data.
        Triggered by clicking on the corresponding `apply` button.
        """
        cropping_params = self.methods.cropping.get_params()
        self.curr_data.crop_spectra_absolute(*cropping_params[:2])
        self.curr_data.crop_spectral_map(*cropping_params[2:])

        self.spectral_map_graph.update_image(self.curr_data.averages)
        # go back to (0,0) coordinates as prev coordinates may not exist anymore
        self.update_plot(0, 0)
        # reconnect plot and map for sizes adjusting
        self.update_method(self.methods.cropping)

    def linearization_apply(self) -> None:
        """
        A function to apply linearization method on the data.
        Triggered by clicking on the corresponding `apply` button.
        """

        self.curr_data.linearization(self.methods.linearization.get_params()[0])
        self.update_plot(self.curr_plot_indices[0], self.curr_plot_indices[1])
        self.spectral_map_graph.update_image(self.curr_data.averages)

        self.update_method(self.methods.linearization)

    def crr_apply(self) -> None:
        """
        A function to apply CRR method on the data.
        Triggered by clicking on the corresponding `apply` button.
        """

        auto_removal = self.methods.cosmic_ray_removal.auto_removal_btn.isChecked()

        if auto_removal:
            self.curr_data.auto_spike_removal()
        else:  # manual
            self.curr_data.interpolate_withing_range(
                self.curr_plot_indices[0],
                self.curr_plot_indices[1],
                *self.methods.cosmic_ray_removal.get_params()[:2]
            )

        self.update_plot(self.curr_plot_indices[0], self.curr_plot_indices[1])
        self.spectral_map_graph.update_image(self.curr_data.averages)

        self.update_method(self.methods.cosmic_ray_removal)

    def bgr_apply(self) -> None:
        """
        A function to apply background removal method on the data.
        Triggered by clicking on the corresponding `apply` button.
        """

        math_morpho = self.methods.background_removal.math_morpho_btn.isChecked()
        poly_deg, ignore_water = self.methods.background_removal.get_params()
        # steps for progress bar
        steps = np.multiply(*self.curr_data.data.shape[:2])

        if math_morpho:
            self.progress_bar_function(
                steps,
                self.curr_data.background_removal_math_morpho,
                ignore_water,
                self.update_progress,
            )
        else:
            self.progress_bar_function(
                steps,
                self.curr_data.background_removal_imodpoly,
                poly_deg,
                ignore_water,
                self.update_progress,
            )

        self.update_plot(self.curr_plot_indices[0], self.curr_plot_indices[1])
        self.spectral_map_graph.update_image(self.curr_data.averages)

        self.update_method(self.methods.background_removal)

    def bgr_change_poly_on_plot(self, degree: int) -> None:
        """
        A function to change (and display) a polynom on the spectral plot.
        Is in sep. function as it is a slot for a signal.
        """

        ignore_water = self.methods.background_removal.ignore_water_band.isChecked()
        curr_spectrum = self.curr_data.data[
            self.curr_plot_indices[0], self.curr_plot_indices[1], :
        ]
        poly_bg = self.curr_data.background_removal_imodpoly(
            degree, ignore_water, one_spectrum=curr_spectrum
        )
        self.plot.plot_background(poly_bg)

    def bgr_update_plot(self) -> None:
        """
        A function to update a bakground line on the spectral plot.
        """

        if self.methods.background_removal.math_morpho_btn.isChecked():
            ignore_water = self.methods.background_removal.ignore_water_band.isChecked()
            curr_spectrum = self.curr_data.data[
                self.curr_plot_indices[0], self.curr_plot_indices[1], :
            ]
            mm_bg = self.curr_data.background_removal_math_morpho(
                ignore_water, one_spectrum=curr_spectrum
            )
            self.plot.plot_background(mm_bg)
        else:
            # emit degree of poly that is currently set in line edit -> it will trigger `bgr_change_poly_on_plot` with right params
            self.methods.background_removal.emit_poly_deg_changed()

    def smoothing_apply(self) -> None:
        """
        A function to apply smoothing method on the data.
        Triggered by clicking on the corresponding `apply` button.
        """
        savgol = self.methods.smoothing.savgol_btn.isChecked()
        lam, diff, wl, po = self.methods.smoothing.get_params()

        if savgol:
            self.curr_data.smoothing_savgol(wl, po)
        else:
            self.curr_data.smoothing_whittaker(lam, diff)

        self.update_plot(self.curr_plot_indices[0], self.curr_plot_indices[1])
        self.spectral_map_graph.update_image(self.curr_data.averages)

        self.update_method(self.methods.smoothing)

    def smoothing_change_on_plot(self) -> None:
        """
        A function to change (and display) smoothed spectrum on plot.
        Is in sep. function as it is a slot for a signal.
        """

        savgol = self.methods.smoothing.savgol_btn.isChecked()
        lam, diff, wl, po = self.methods.smoothing.get_params()
        curr_spectrum = self.curr_data.data[
            self.curr_plot_indices[0], self.curr_plot_indices[1], :
        ]
        if savgol:
            smoothed = self.curr_data.smoothing_savgol(
                wl, po, one_spectrum=curr_spectrum
            )
        else:
            smoothed = self.curr_data.smoothing_whittaker(
                lam, diff, one_spectrum=curr_spectrum
            )
        # TODO: change to some general function
        self.plot.plot_background(smoothed)

    def _is_placeholder(self, object: object) -> bool:
        """
        A function to test whether given `object` is instance of `Color` class, i.e. is a placeholder.

        Parameters:
            object (object): Object to be tested if it is a placeholder.

        Returns:
            is_placeholer (bool): Info whether given `object` is a placeholder.

        """
        return isinstance(object, Color)

    def init_file_error_widget(self) -> None:
        """
        A function initialize and show a file error widget.
        """

        self.file_error = QMessageBox()
        self.file_error.setIconPixmap(QPixmap("icons/x-circle.svg"))
        self.file_error.setText("File has invalide structure and cannot be loaded.")
        self.file_error.setInformativeText(
            "RamAIn currently supports only .mat files originally produced by WITec spectroscopes. Sorry :("
        )
        self.file_error.setWindowTitle("Invalid file structure")
        self.file_error.setWindowIcon(QIcon("src/resources/icons/message.svg"))
        self.file_error.setStandardButtons(QMessageBox.Ok)

    def enable_widgets(self, enable: bool) -> None:
        """
        A function to enable/disable widgets in ManulPreprocessing instance.

        Parameters:
            enable (bool): Whether widgets should be enabled or disabled.
        """

        self.files_view.setEnabled(enable)
        self.methods.setEnabled(enable)
        self.save_button.setEnabled(enable)
        self.reload_discard_button.setEnabled(enable)
        self.parent.setEnabled(enable)

    def make_progress_bar(self, maximum: int) -> None:
        """
        A function to make a progress bar dialog with `maximum` steps.

        Parameters:
            maximum (int): A number of steps that has to be reached so that 100 % is displayed.
        """

        self.enable_widgets(False)

        self.progress = QProgressDialog("Progress", "...", 0, maximum)
        self.progress.setValue(0)
        self.progress.setCancelButton(None)

        # style for progress bar that is inside progress dialog must be set here for some reason
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
        self.progress.setWindowFlags(
            Qt.WindowTitleHint
        )  # Qt.Dialog | Qt.FramelessWindowHint | Qt.WindowTitleHint
        self.progress.setWindowIcon(QIcon("src/resources/icons/message.svg"))

        self.progress.setWindowTitle("Work in progress")
        self.update_progress.connect(self.set_progress)

        self.progress.forceShow()

    def set_progress(self) -> None:
        """
        A function to increment progress in the progress bar dialog.
        """

        # process another events that are not user inputs
        QCoreApplication.processEvents(QEventLoop.ExcludeUserInputEvents)
        val = self.progress.value()
        self.progress.setValue(val + 1)

    def destroy_progress_bar(self) -> None:
        """
        A function to destroy progress bar dialog and disconnect its signals.
        """

        self.enable_widgets(True)
        self.update_progress.disconnect()
        self.progress.deleteLater()

    def progress_bar_function(
        self, progress_steps: int, function: Callable, *args, **kwargs
    ) -> None:
        """
        A wrapper for function that requires progress bar to be shown and is able to emit signal to update progress.
        """

        self.make_progress_bar(progress_steps)
        function(*args, **kwargs)
        self.destroy_progress_bar()

    def update_file_list(self) -> None:
        """
        A function to silently update the file list without any signals emitting.
        """

        # do not update file on curr item change in the list -> item will be changed to the same one, no need for loading again
        self.files_view.file_list.currentItemChanged.disconnect()
        # update file list so that new file is visible
        self.files_view.update_list()
        # set that required file is visually selected
        if self.curr_file is not None:
            self.files_view.set_curr_file(self.curr_file)
        # connect again
        self.files_view.file_list.currentItemChanged.connect(self.update_file)

    def save_file(self) -> None:
        """
        A function to show file dialog for data file saving + save function calling.
        """

        data_dir = SETTINGS.value("save_dir", self.files_view.data_folder)
        if not os.path.exists(data_dir):
            data_dir = os.getcwd()

        file_name, _ = QFileDialog.getSaveFileName(
            self, "Save Data", data_dir, filter="*.mat"
        )

        # user did not select any file and exited the dialog
        if file_name is None or len(file_name) == 0:
            return

        dir_name, file_name = os.path.split(file_name)

        self.curr_data.save_matlab(dir_name, file_name=file_name)

        SETTINGS.setValue("save_dir", dir_name)

        self.files_view.data_folder = dir_name
        self.update_folder(dir_name)

        self.update_file_list()

    def discard_changes(self) -> None:
        """
        A function to load current file once again.
        This action discards changes and forces plots and maps loading once again.
        """

        self.update_file(self.files_view.file_list.currentItem())

    def get_string_name(self) -> None:
        """
        A function to return name of this widget as a string.

        Returns:
            widget_name (str): Name of the widget so that it can be recognized by the user.
        """

        return "Manual Preprocessing"
