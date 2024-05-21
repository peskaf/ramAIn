from PySide6.QtWidgets import (
    QFrame,
    QFileDialog,
    QPushButton,
    QListWidget,
    QStackedLayout,
    QVBoxLayout,
    QHBoxLayout,
    QAbstractItemView,
    QListWidgetItem,
    QProgressDialog,
    QLabel,
    QWidget,
)
from PySide6.QtGui import QIcon
from PySide6.QtCore import Qt, QThread, Signal

from typing import List, Callable

from ramain.views.widgets.auto_method import AutoMethod

# TODO: not a widget
from ramain.views.widgets.input_widget_specifier import InputWidgetSpecifier, WidgetType

from ramain.model.spectal_map import SpectralMap

from ramain.utils import validators
from ramain.utils.settings import SETTINGS

import os
import datetime


class FunctionItem(QListWidgetItem):
    """
    Subclass of `QListWidgetItem`, instance of this class holds the function it represents
    and its parameters.
    """

    def __init__(
        self,
        label: str,
        function: Callable = None,
        params: List = None,
        parent: QWidget = None,
    ) -> None:
        """
        The constructor for FunctionItem widget usable in QListWidget.

        Parameters:
            label (str): Text to be displayed in the list.
            function (Callable): Function that this objects represents. Default: None.
            params (List): Parameters for the `function` function. Default: None.
            parent (QWidget): Parent widget of this widget. Default: None.
        """

        super().__init__(label, parent)
        self.function = function
        self.params = params


class AutoProcessing(QFrame):
    """
    A widget for creation of pipeline for batch of files for automatic data processing.
    """

    def __init__(self, parent: QWidget = None) -> None:
        """
        The constructor for automatic processing widget.

        Parameters:
            parent (QWidget): Parent widget of this widget. Default: None.
        """

        super().__init__(parent)
        self.parent = parent

        self.icon = QIcon("ramain/resources/icons/play-circle.svg")

        # file selection widget
        self.file_list_widget = QListWidget(self)
        self.file_list_widget.setObjectName("files_list")
        self.file_list = []

        self.add_file_btn = QPushButton("Add File")
        self.add_file_btn.clicked.connect(self.add_files)

        self.remove_file_btn = QPushButton("Remove File")
        self.remove_file_btn.clicked.connect(self.remove_file)

        # logs folder
        self.logs_dir = SETTINGS.value("logs_dir", os.getcwd())
        self.logs_dir_label = QLabel(f"Logs Directory: {self.logs_dir}")
        self.select_logs_dir = QPushButton("Select Logs Directory")
        self.select_logs_dir.clicked.connect(self.logs_dir_dialog)

        # methods selection
        self.methods_list = QListWidget(self)
        self.methods_list.setObjectName("methods_list")
        self.methods_list.currentItemChanged.connect(self.change_method)

        self.auto_methods = self._make_auto_methods_widgets()

        self.methods_list.setObjectName("methods_list")
        self.methods_list.addItems(
            [f"{auto_method.name}" for i, auto_method in enumerate(self.auto_methods)]
        )

        self.methods_layout = QStackedLayout()

        for method in self.auto_methods:
            self.methods_layout.addWidget(method)

        for i in range(self.methods_list.count()):
            self.methods_list.item(i).setIcon(self.auto_methods[i].icon)

        self.methods_list.setCurrentItem(self.methods_list.item(0))
        self.methods_layout.setCurrentIndex(0)

        self.add_to_pipeline_btn = QPushButton("Add to Pipeline")
        self.add_to_pipeline_btn.clicked.connect(self.add_to_pipeline)

        # methods pipeline
        self.pipeline_list = QListWidget(self)
        self.pipeline_list.setObjectName("pipeline")
        self.pipeline_list.setDragDropMode(QAbstractItemView.InternalMove)

        self.remove_from_pipeline_btn = QPushButton("Remove Step")
        self.remove_from_pipeline_btn.clicked.connect(self.remove_from_pipeline)

        self.clear_pipeline_btn = QPushButton("Clear Pipeline")
        self.clear_pipeline_btn.clicked.connect(self.clear_pipeline)

        self.apply_button = QPushButton("Apply")
        self.apply_button.clicked.connect(self.apply_pipeline)
        self.apply_button.setEnabled(False)

        self.progress = None
        self.pipeline_worker = PipelineWorker(self)
        self.pipeline_worker.progress_update.connect(self.update_progress)

        # put everything into layout
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("Files to Process"))
        layout.addWidget(self.file_list_widget)

        buttons_layout = QHBoxLayout()
        buttons_layout.addWidget(self.remove_file_btn)
        buttons_layout.addStretch()
        buttons_layout.addWidget(self.add_file_btn)

        layout.addLayout(buttons_layout)

        logs_layout = QHBoxLayout()
        logs_layout.addWidget(self.logs_dir_label)
        logs_layout.addStretch()
        logs_layout.addWidget(self.select_logs_dir)

        layout.addLayout(logs_layout)

        layout.addWidget(QLabel("Methods Selection"))

        methods_list_layout = QHBoxLayout()
        methods_list_layout.addWidget(self.methods_list)
        methods_list_layout.addLayout(self.methods_layout)

        layout.addLayout(methods_list_layout)

        add_method_layout = QHBoxLayout()
        add_method_layout.addStretch()
        add_method_layout.addWidget(self.add_to_pipeline_btn)

        layout.addLayout(add_method_layout)

        layout.addWidget(QLabel("Pipeline"))

        layout.addWidget(self.pipeline_list)

        pipeline_btns_layout = QHBoxLayout()
        pipeline_btns_layout.addWidget(self.remove_from_pipeline_btn)
        pipeline_btns_layout.addStretch()
        pipeline_btns_layout.addWidget(self.clear_pipeline_btn)

        layout.addLayout(pipeline_btns_layout)
        layout.addWidget(self.apply_button)

        self.setLayout(layout)

    def _make_auto_methods_widgets(self) -> List:
        auto_methods = []

        auto_cropping_absolute = AutoMethod(
            name="Spectral Plot Cropping - Absolute",
            icon=QIcon("ramain/resources/icons/cut.svg"),
            input_widget_specifiers={
                "Start Position (1/cm)": InputWidgetSpecifier(
                    widget_type=WidgetType.TEXT,
                    init_value=0,
                    output_type=float,
                    text_validator=validators.REAL_VALIDATOR,
                    parameter_order=0,
                ),
                "End Position (1/cm)": InputWidgetSpecifier(
                    widget_type=WidgetType.TEXT,
                    init_value=0,
                    output_type=float,
                    text_validator=validators.REAL_VALIDATOR,
                    parameter_order=1,
                ),
            },
            callback=SpectralMap.crop_spectra_absolute,
            parent=self,
        )
        auto_methods.append(auto_cropping_absolute)

        auto_cropping_relative = AutoMethod(
            name="Spectral Plot Cropping - Relative",
            icon=QIcon("ramain/resources/icons/cut.svg"),
            input_widget_specifiers={
                "Start Position": InputWidgetSpecifier(
                    widget_type=WidgetType.TEXT,
                    init_value=0,
                    output_type=int,
                    text_validator=validators.POSITIVE_INT_VALIDATOR,
                    parameter_order=0,
                ),
                "End Position": InputWidgetSpecifier(
                    widget_type=WidgetType.TEXT,
                    init_value=0,
                    output_type=int,
                    text_validator=validators.POSITIVE_INT_VALIDATOR,
                    parameter_order=1,
                ),
            },
            callback=SpectralMap.crop_spectra_relative,
            parent=self,
        )
        auto_methods.append(auto_cropping_relative)

        auto_crr = AutoMethod(
            name="Cosmic Ray Removal",
            icon=QIcon("ramain/resources/icons/signal.svg"),
            callback=SpectralMap.auto_spike_removal,
            parent=self,
        )
        auto_methods.append(auto_crr)

        auto_bgr_imodpoly = AutoMethod(
            name="Background Removal - I-ModPoly",
            icon=QIcon("ramain/resources/icons/background.svg"),
            input_widget_specifiers={
                "Ignore Water Band": InputWidgetSpecifier(
                    widget_type=WidgetType.CHECKBOX,
                    init_value=True,
                    output_type=bool,
                    parameter_order=1,
                ),
                "Polynom Degree": InputWidgetSpecifier(
                    widget_type=WidgetType.TEXT,
                    init_value=5,
                    range=(1, 15),
                    text_validator=validators.POSITIVE_INT_VALIDATOR,
                    output_type=int,
                    parameter_order=0,
                ),
            },
            callback=SpectralMap.background_removal_imodpoly,
            parent=self,
        )
        auto_methods.append(auto_bgr_imodpoly)

        auto_bgr_airpls = AutoMethod(
            name="Background Removal - airPLS",
            icon=QIcon("ramain/resources/icons/background.svg"),
            input_widget_specifiers={
                "Lambda": InputWidgetSpecifier(
                    widget_type=WidgetType.TEXT,
                    init_value=10000,
                    output_type=int,
                    text_validator=validators.POSITIVE_INT_VALIDATOR,
                    parameter_order=0,
                ),
            },
            callback=SpectralMap.background_removal_airpls,
            parent=self,
        )
        auto_methods.append(auto_bgr_airpls)

        auto_bgr_poly = AutoMethod(
            name="Background Removal - Polynom Interpolation",
            icon=QIcon("ramain/resources/icons/background.svg"),
            input_widget_specifiers={
                "Ignore Water Band": InputWidgetSpecifier(
                    widget_type=WidgetType.CHECKBOX,
                    init_value=True,
                    output_type=bool,
                    parameter_order=1,
                ),
                "Polynom Degree": InputWidgetSpecifier(
                    widget_type=WidgetType.TEXT,
                    init_value=5,
                    range=(1, 15),
                    text_validator=validators.POSITIVE_INT_VALIDATOR,
                    output_type=int,
                    parameter_order=0,
                ),
            },
            callback=SpectralMap.background_removal_poly,
            parent=self,
        )
        auto_methods.append(auto_bgr_poly)

        auto_bgr_math_morpho = AutoMethod(
            name="Background Removal - Mathematical Morphology",
            icon=QIcon("ramain/resources/icons/background.svg"),
            input_widget_specifiers={
                "Ignore Water Band": InputWidgetSpecifier(
                    widget_type=WidgetType.CHECKBOX,
                    init_value=True,
                    output_type=bool,
                    parameter_order=0,
                ),
            },
            callback=SpectralMap.background_removal_math_morpho,
            parent=self,
        )
        auto_methods.append(auto_bgr_math_morpho)

        auto_bgr_bubblefill = AutoMethod(
            name="Background Removal - BubbleFill",
            icon=QIcon("ramain/resources/icons/background.svg"),
            input_widget_specifiers={
                "Non-Water Bubble Size": InputWidgetSpecifier(
                    widget_type=WidgetType.TEXT,
                    init_value=100,
                    range=(1, 1000),
                    text_validator=validators.POSITIVE_INT_VALIDATOR,
                    output_type=int,
                    parameter_order=0,
                ),
                "Water Bubble Size": InputWidgetSpecifier(
                    widget_type=WidgetType.TEXT,
                    init_value=700,
                    range=(1, 1000),
                    text_validator=validators.POSITIVE_INT_VALIDATOR,
                    output_type=int,
                    parameter_order=1,
                ),
            },
            callback=SpectralMap.background_removal_bubblefill,
            parent=self,
        )
        auto_methods.append(auto_bgr_bubblefill)

        auto_smt_whittaker = AutoMethod(
            name="Smoothing - Whittaker",
            icon=QIcon("ramain/resources/icons/RamAIn_logo_R_f8bc24.svg"),
            input_widget_specifiers={
                "Lambda": InputWidgetSpecifier(
                    widget_type=WidgetType.TEXT,
                    init_value=1600,
                    range=(1, 2000),
                    text_validator=validators.POSITIVE_INT_VALIDATOR,
                    output_type=int,
                    parameter_order=0,
                ),
                "Diff": InputWidgetSpecifier(
                    widget_type=WidgetType.TEXT,
                    init_value=2,
                    range=(1, 5),
                    text_validator=validators.POSITIVE_INT_VALIDATOR,
                    output_type=int,
                    parameter_order=1,
                ),
            },
            callback=SpectralMap.smoothing_whittaker,
            parent=self,
        )
        auto_methods.append(auto_smt_whittaker)

        auto_smt_savgol = AutoMethod(
            name="Smoothing - SavGol",
            icon=QIcon("ramain/resources/icons/RamAIn_logo_R_f8bc24.svg"),
            input_widget_specifiers={
                "Window Length": InputWidgetSpecifier(
                    widget_type=WidgetType.TEXT,
                    init_value=5,
                    range=(3, 20),
                    text_validator=validators.POSITIVE_INT_VALIDATOR,
                    output_type=int,
                    parameter_order=0,
                ),
                "Poly Order": InputWidgetSpecifier(
                    widget_type=WidgetType.TEXT,
                    init_value=2,
                    range=(1, 6),
                    text_validator=validators.POSITIVE_INT_VALIDATOR,
                    output_type=int,
                    parameter_order=1,
                ),
            },
            callback=SpectralMap.smoothing_savgol,
            parent=self,
        )
        auto_methods.append(auto_smt_savgol)

        auto_linearization = AutoMethod(
            name="X-axis Linearization",
            icon=QIcon("ramain/resources/icons/equal.svg"),
            input_widget_specifiers={
                "Step (1/cm)": InputWidgetSpecifier(
                    widget_type=WidgetType.TEXT,
                    init_value=1,
                    range=(0.1, 5),
                    output_type=float,
                    text_validator=validators.POSITIVE_REAL_VALIDATOR,
                    parameter_order=0,
                ),
            },
            callback=SpectralMap.linearization,
            parent=self,
        )
        auto_methods.append(auto_linearization)

        auto_water_norm = AutoMethod(
            name="Water Normalization",
            icon=QIcon("ramain/resources/icons/equal.svg"),
            callback=SpectralMap.water_normalization,
            parent=self,
        )
        auto_methods.append(auto_water_norm)

        auto_NMF = AutoMethod(
            name="Decomposition - NMF",
            icon=QIcon("ramain/resources/icons/pie.svg"),
            input_widget_specifiers={
                "Number of Components": InputWidgetSpecifier(
                    widget_type=WidgetType.TEXT,
                    init_value=5,
                    range=(2, 10),
                    output_type=int,
                    text_validator=validators.POSITIVE_INT_VALIDATOR,
                    parameter_order=0,
                ),
            },
            callback=SpectralMap.decomposition_NMF,
            parent=self,
        )
        auto_methods.append(auto_NMF)

        auto_PCA = AutoMethod(
            name="Decomposition - PCA",
            icon=QIcon("ramain/resources/icons/pie.svg"),
            input_widget_specifiers={
                "Number of Components": InputWidgetSpecifier(
                    widget_type=WidgetType.TEXT,
                    init_value=5,
                    range=(2, 10),
                    output_type=int,
                    text_validator=validators.POSITIVE_INT_VALIDATOR,
                    parameter_order=0,
                ),
            },
            callback=SpectralMap.decomposition_PCA,
            parent=self,
        )
        auto_methods.append(auto_PCA)

        auto_save = AutoMethod(
            name="Save Data",
            icon=QIcon("ramain/resources/icons/save.svg"),
            input_widget_specifiers={
                "Files Tag": InputWidgetSpecifier(
                    widget_type=WidgetType.TEXT,
                    output_type=str,
                    parameter_order=1,
                ),
                "Directory": InputWidgetSpecifier(
                    widget_type=WidgetType.DIRECTORY_SELECTION,
                    output_type=str,
                    dir_registry_value="save_dir",
                    parameter_order=0,
                ),
            },
            callback=SpectralMap.save_matlab,
            parent=self,
        )
        auto_methods.append(auto_save)

        auto_export_components_graphics = AutoMethod(
            name="Export Components - Graphics",
            icon=QIcon("ramain/resources/icons/export.svg"),
            input_widget_specifiers={
                "Output Format": InputWidgetSpecifier(
                    widget_type=WidgetType.COMBO_BOX,
                    output_type=str,
                    choices=["png", "pdf", "ps", "eps", "svg"],
                    init_value="png",
                    parameter_order=0,
                ),
                "Files Tag": InputWidgetSpecifier(
                    widget_type=WidgetType.TEXT,
                    output_type=str,
                    parameter_order=2,
                ),
                "Directory": InputWidgetSpecifier(
                    widget_type=WidgetType.DIRECTORY_SELECTION,
                    output_type=str,
                    dir_registry_value="export_dir",
                    parameter_order=1,
                ),
            },
            callback=SpectralMap.export_to_graphics,
            parent=self,
        )
        auto_methods.append(auto_export_components_graphics)

        auto_export_components_txt = AutoMethod(
            name="Export Components - Text",
            icon=QIcon("ramain/resources/icons/export.svg"),
            input_widget_specifiers={
                "Files Tag": InputWidgetSpecifier(
                    widget_type=WidgetType.TEXT,
                    output_type=str,
                    parameter_order=1,
                ),
                "Directory": InputWidgetSpecifier(
                    widget_type=WidgetType.DIRECTORY_SELECTION,
                    output_type=str,
                    dir_registry_value="export_dir",
                    parameter_order=0,
                ),
            },
            callback=SpectralMap.export_to_text,
            parent=self,
        )
        auto_methods.append(auto_export_components_txt)

        # NOTE: new methods belong here (or between the similar ones in the code above in this function)

        return auto_methods

    def logs_dir_dialog(self) -> None:
        """
        A function that shows file dialog for the selection of the directory where to store logs file.
        """

        if not os.path.exists(self.logs_dir_label.text()):
            self.logs_dir_label.setText(os.getcwd())

        temp_dir = QFileDialog.getExistingDirectory(
            self, "Select Directory", self.logs_dir_label.text()
        )

        if temp_dir is None or len(temp_dir) == 0:
            return

        SETTINGS.setValue("logs_dir", temp_dir)
        self.logs_dir = temp_dir
        self.logs_dir_label.setText(f"Logs Directory: {temp_dir}")

    def clear_pipeline(self) -> None:
        """
        A function to clear whole pipeline.
        """

        # NOTE: removing in reversed order -> items index decreases during deletion
        for item_index in reversed(range(self.pipeline_list.count())):
            self.pipeline_list.takeItem(item_index)
        self.clear_pipeline_btn.setEnabled(False)

    def add_files(self) -> None:
        """
        A function to show file dialog so that file can be added to the list of files
        that are to be processed.
        """

        temp_folder = SETTINGS.value("source_dir", os.getcwd())
        if not os.path.exists(temp_folder):
            temp_folder = os.getcwd()

        file_names, _ = QFileDialog.getOpenFileNames(
            self, "Select one or more files", temp_folder, "*.mat"
        )

        if file_names is None or len(file_names) == 0:
            return

        SETTINGS.setValue("source_dir", os.path.dirname(file_names[0]))

        for file_name in file_names:
            self.file_list_widget.addItem(os.path.basename(file_name))
            self.file_list.append(file_name)

        # allow user to remove files
        self.remove_file_btn.setEnabled(True)

        # if there is something in the pipeline and in the file list -> pipeline can be applied
        if self.file_list_widget.count() != 0 and self.pipeline_list.count() != 0:
            self.apply_button.setEnabled(True)

    def remove_file(self) -> None:
        """
        A function for removing of currently selected file(s).
        """

        curr_items = self.file_list_widget.selectedItems()
        if curr_items is not None:
            for item in curr_items:
                item_row = self.file_list_widget.row(item)
                self.file_list_widget.takeItem(item_row)
                self.file_list.pop(item_row)

        if self.file_list_widget.count() == 0:
            self.apply_button.setEnabled(False)
            self.remove_file_btn.setEnabled(False)

    def change_method(self) -> None:
        """
        A function to change visible widget in the `methods_layout` according to selected
        item in the `self.method_list`.
        """

        curr_method_index = self.methods_list.currentRow()
        self.methods_layout.setCurrentIndex(curr_method_index)

    def add_to_pipeline(self) -> None:
        """
        A function to add currently selected method to the pipeline.
        """

        # Enable apply button only if a file is in the list
        if self.file_list_widget.count() != 0:
            self.apply_button.setEnabled(True)

        # Enable buttons to remove steps from pipeline
        self.clear_pipeline_btn.setEnabled(True)
        self.remove_from_pipeline_btn.setEnabled(True)

        curr_item = self.methods_list.currentItem()
        curr_item_index = self.methods_list.row(curr_item)
        params_text = self.auto_methods[curr_item_index].params_to_text()
        function = self.auto_methods[curr_item_index].callback
        params = self.auto_methods[curr_item_index].get_params()

        # make item with function and params, display text version of params
        self.pipeline_list.addItem(
            FunctionItem(
                curr_item.text() + (" - " if len(params_text) else "") + params_text,
                function,
                params,
            )
        )

    def remove_from_pipeline(self) -> None:
        """
        A function to remove currently selected method from the pipeline
        """

        curr_items = self.pipeline_list.selectedItems()
        if curr_items is not None:
            for item in curr_items:
                item_row = self.pipeline_list.row(item)
                self.pipeline_list.takeItem(item_row)

        # disable some buttons if no method is left in the list
        if self.pipeline_list.count() == 0:
            self.apply_button.setEnabled(False)
            self.clear_pipeline_btn.setEnabled(False)
            self.remove_from_pipeline_btn.setEnabled(False)

    def enable_widgets(self, enable: bool) -> None:
        """
        A function to enable/disable all possible widgets on the page.

        Parameters:
            enable (bool): Whether to enable or disable the widgets.
        """

        self.pipeline_list.setEnabled(enable)
        self.file_list_widget.setEnabled(enable)
        self.methods_list.setEnabled(enable)
        self.add_file_btn.setEnabled(enable)
        self.remove_file_btn.setEnabled(enable)
        self.add_to_pipeline_btn.setEnabled(enable)
        self.remove_from_pipeline_btn.setEnabled(enable)
        self.apply_button.setEnabled(enable)
        self.clear_pipeline_btn.setEnabled(enable)
        self.select_logs_dir.setEnabled(enable)
        self.parent.setEnabled(enable)

        for method in self.auto_methods:
            method.setEnabled(enable)

    def make_progress_bar(self, maximum: int) -> None:
        """
        A function to make progress bar dialog with `maximum` steps.

        Parameters:
            maximum (int): Number of steps to be made to display 100 %.
        """

        self.enable_widgets(False)

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
        self.progress.setWindowFlags(Qt.WindowTitleHint)
        self.progress.setWindowIcon(QIcon("ramain/resources/icons/message.svg"))
        self.progress.setWindowTitle("Work in progress")
        self.progress.forceShow()

    def update_progress(self, val: int) -> None:
        """
        A function to set progress value to `val`.

        Parameters:
            val (int): Value to which to set the progress in the progress bar.
        """
        self.progress.setValue(val)

    def destroy_progress_bar(self) -> None:
        """
        A function to destroy the progress bar object.
        """
        self.enable_widgets(True)
        self.progress.deleteLater()
        self.progress = None

    def apply_pipeline(self):
        """
        A function to apply the pipeline on the batch of files by calling the worker.
        """

        steps = len(self.file_list) * self.pipeline_list.count()
        self.make_progress_bar(steps)
        self.pipeline_worker.start()

    def get_string_name(self) -> str:
        """
        A function to return name of this widget as a string.

        Returns:
            widget_name (str): Name of the widget so that it can be recognized by the user.
        """

        return "Auto Processing"


class PipelineWorker(QThread):
    """
    A worker in another thread for the automatic pipeline as it may take some time.
    """

    progress_update = Signal(int)

    def __init__(self, auto_processing_widget: AutoProcessing) -> None:
        """
        The constructor `AutoProcessing` PipelineWorker. Its job is to run the pipeline in another thread.

        Parameters:
            auto_processing_widget (AutoProcessing): AutoProcessing widget on which this worker operates.
        """

        QThread.__init__(self)
        self.auto_proceesing_widget = auto_processing_widget

    def destroy(self) -> None:
        """
        Function to quit the thread and to destroy the progress bar.
        """

        self.quit()
        if self.auto_proceesing_widget.progress is not None:
            self.auto_proceesing_widget.destroy_progress_bar()

    def run(self) -> None:
        """
        A function to run the work in the pipeline while logging it and updating the progress bar.
        """

        # log file has name according to current time
        logs_file = os.path.join(
            self.auto_proceesing_widget.logs_dir,
            "logs_" + datetime.datetime.now().strftime("%Y-%m-%d_%H%M%S") + ".txt",
        )

        with open(logs_file, "w", encoding="utf-8") as logs:
            files_count = len(self.auto_proceesing_widget.file_list)
            steps_count = self.auto_proceesing_widget.pipeline_list.count()

            for i, file_name in enumerate(self.auto_proceesing_widget.file_list, 1):
                print(f"[FILE {i}/{files_count}]: {file_name}", file=logs)
                try:
                    curr_data = SpectralMap(file_name)
                    for item_index in range(steps_count):
                        curr_function = self.auto_proceesing_widget.pipeline_list.item(
                            item_index
                        ).function
                        curr_step_text = self.auto_proceesing_widget.pipeline_list.item(
                            item_index
                        ).text()
                        curr_params = self.auto_proceesing_widget.pipeline_list.item(
                            item_index
                        ).params
                        print(
                            f"[STEP {item_index + 1}/{steps_count}]: {curr_step_text}; function: {curr_function.__name__}",
                            file=logs,
                        )

                        # function call
                        curr_function(curr_data, *curr_params)

                        print("[SUCCESS]", file=logs)
                        self.progress_update.emit(
                            (i - 1) * self.auto_proceesing_widget.pipeline_list.count()
                            + item_index
                            + 1
                        )

                except Exception as e:
                    print(f"[ERROR]: {e}", file=logs)
                print(file=logs)

        self.destroy()
