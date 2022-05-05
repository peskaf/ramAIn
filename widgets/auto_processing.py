from PySide6.QtWidgets import QFrame, QFileDialog, QPushButton, QListWidget, QStackedLayout, QVBoxLayout, QHBoxLayout, QAbstractItemView, QListWidgetItem, QProgressDialog, QLabel, QWidget
from PySide6.QtGui import QIcon
from PySide6.QtCore import Qt, QSettings, QThread, Signal

from widgets.auto_cropping_absolute import AutoCroppingAbsolute
from widgets.auto_cropping_relative import AutoCroppingRelative
from widgets.auto_crr import AutoCRR
from widgets.auto_bgr_vancouver import AutoBGRVancouver
from widgets.auto_bgr_airpls import AutoBGRairPLS
from widgets.auto_bgr_poly import AutoBGRPoly
from widgets.auto_bgr_math_morpho import AutoBGRMathMorpho
from widgets.auto_linearization import AutoLinearization
from widgets.auto_decomposition_NMF import AutoNMF
from widgets.auto_save import AutoSave
from widgets.auto_export_components import AutoExportComponents

from data import Data

import os
import datetime


class FunctionItem(QListWidgetItem):
    """
    Subclass of `QListWidgetItem`, instance of this class holds name of the function it represents
    and its parameters.
    """

    def __init__(self, label: str, func: str = None, params: tuple = None, parent: QWidget = None) -> None:
        """
        The constructor for FunctionItem widget usable in QListWidget.
  
        Parameters:
            label (str): Text to be displayed in the list.
            func (str): Function on the `Data` obejct that this item represents. Default: None.
            params (tuple): Parameters for the `func` function. Default: None.
            parent (QWidget): Parent widget of this widget. Default: None.
        """

        super().__init__(label, parent)
        self.func = func
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

        self.icon = QIcon("icons/play-circle.svg")

        self.settings = QSettings()

        # file selection widget
        self.file_list_widget = QListWidget(self)
        self.file_list_widget.setObjectName("files_list")
        self.file_list = []
        
        self.add_file_btn = QPushButton("Add file")
        self.add_file_btn.clicked.connect(self.add_files)

        self.remove_file_btn = QPushButton("Remove file")
        self.remove_file_btn.clicked.connect(self.remove_file)

        # logs folder
        self.logs_dir = self.settings.value('logs_dir', os.getcwd())
        self.logs_dir_label = QLabel(f"Logs Directory: {self.logs_dir}")
        self.select_logs_dir = QPushButton("Select Logs Directory")
        self.select_logs_dir.clicked.connect(self.logs_dir_dialog)

        # methods selection
        self.methods_list = QListWidget(self)
        self.methods_list.setObjectName("methods_list")
        self.methods_list.currentItemChanged.connect(self.change_method)

        self.auto_cropping_absolute = AutoCroppingAbsolute(self)
        self.auto_cropping_relative = AutoCroppingRelative(self)
        self.auto_crr = AutoCRR(self)
        self.auto_bgr_vancouver = AutoBGRVancouver(self)
        self.auto_bgr_airpls = AutoBGRairPLS(self)
        self.auto_bgr_poly = AutoBGRPoly(self)
        self.auto_bgr_math_morpho = AutoBGRMathMorpho(self)
        self.auto_linearization = AutoLinearization(self)
        self.auto_NMF = AutoNMF(self)
        self.auto_save = AutoSave(self)
        self.auto_export_components = AutoExportComponents(self)

        self.auto_methods = [
            self.auto_cropping_absolute,
            self.auto_cropping_relative,
            self.auto_crr,
            self.auto_bgr_vancouver,
            self.auto_bgr_airpls,
            self.auto_bgr_poly,
            self.auto_bgr_math_morpho,
            self.auto_linearization,
            self.auto_NMF,
            self.auto_save,
            self.auto_export_components,
        ]

        self.methods_list.setObjectName("methods_list")
        self.methods_list.addItems([auto_method.get_string_name() for auto_method in self.auto_methods])

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

    def logs_dir_dialog(self) -> None:
        """
        A function that shows file dialog for the selection of the directory where to store logs file.
        """

        if not os.path.exists(self.logs_dir_label.text()):
            self.logs_dir_label.setText(os.getcwd())

        temp_dir = QFileDialog.getExistingDirectory(self, "Select Directory", self.logs_dir_label.text())

        if temp_dir is None or len(temp_dir) == 0:
            return

        self.settings.setValue("logs_dir", temp_dir)      
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

        temp_folder = self.settings.value("source_dir", os.getcwd())
        if not os.path.exists(temp_folder):
            temp_folder = os.getcwd()

        file_names, _ = QFileDialog.getOpenFileNames(self, "Select one or more files", temp_folder, "*.mat")

        if file_names is None or len(file_names) == 0:
            return

        self.settings.setValue("source_dir", os.path.dirname(file_names[0]))

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

        # Enable apply button only if some file is in the list
        if self.file_list_widget.count() != 0:
            self.apply_button.setEnabled(True)

        # Enable buttons to remove steps from pipeline
        self.clear_pipeline_btn.setEnabled(True)
        self.remove_from_pipeline_btn.setEnabled(True)

        curr_item = self.methods_list.currentItem()
        curr_item_index = self.methods_list.row(curr_item)
        params_text = self.auto_methods[curr_item_index].params_to_text()
        function_name = self.auto_methods[curr_item_index].function_name()
        params = self.auto_methods[curr_item_index].get_params()

        # make item with function and params, display text version of params
        self.pipeline_list.addItem(FunctionItem(curr_item.text() + (" - " if len(params_text) else "") + params_text, function_name, params))
        
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
        self.progress.setWindowIcon(QIcon("icons/message.svg"))

        self.progress.setWindowTitle("Work in progress")

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
        logs_file = os.path.join(self.auto_proceesing_widget.logs_dir, "logs_" + datetime.datetime.now().strftime("%Y-%m-%d_%H%M%S") + ".txt")

        with open(logs_file, "w", encoding="utf-8") as logs:

            for i, file_name in enumerate(self.auto_proceesing_widget.file_list, 1):
                try:
                    curr_data = Data(file_name)
                    print(curr_data.in_file, file=logs)
                    for item_index in range(self.auto_proceesing_widget.pipeline_list.count()):
                        
                        print(f"{self.auto_proceesing_widget.pipeline_list.item(item_index).func}{self.auto_proceesing_widget.pipeline_list.item(item_index).params}", file=logs)
                        # function call
                        getattr(curr_data, self.auto_proceesing_widget.pipeline_list.item(item_index).func)(*self.auto_proceesing_widget.pipeline_list.item(item_index).params)

                        print("OK", file=logs)
                        self.progress_update.emit((i - 1)*self.auto_proceesing_widget.pipeline_list.count() + item_index + 1)

                except Exception as e:
                    print(f"Error: {e}", file=logs)
                print("---------------------------------", file=logs)

                self.progress_update.emit(i*self.auto_proceesing_widget.pipeline_list.count())

        self.destroy()
