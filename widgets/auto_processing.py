from PySide6.QtWidgets import QFrame, QFileDialog, QPushButton, QListWidget, QStackedLayout, QVBoxLayout, QHBoxLayout, QAbstractItemView, QListWidgetItem, QProgressDialog, QLabel
from PySide6.QtGui import QIcon
from PySide6.QtCore import Qt, QSettings, QCoreApplication, QEventLoop

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

from widgets.data import Data

import os
import datetime

class FunctionItem(QListWidgetItem):
    def __init__(self, label, func=None, params=None, parent=None):
        super().__init__(label, parent)
        self.func = func
        self.params = params

class AutoProcessing(QFrame):

    def __init__(self, parent=None):
        super().__init__(parent)
        self.icon = QIcon("icons/settings.svg")
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

        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("Files to Process"))
        layout.addWidget(self.file_list_widget)

        buttons_layout = QHBoxLayout()
        buttons_layout.addWidget(self.remove_file_btn)
        buttons_layout.addStretch()
        buttons_layout.addWidget(self.add_file_btn)

        layout.addLayout(buttons_layout)

        logs_layout = QHBoxLayout()
        logs_layout.addWidget(self.select_logs_dir)
        logs_layout.addStretch()
        logs_layout.addWidget(self.logs_dir_label)

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

    def logs_dir_dialog(self):
        if not os.path.exists(self.logs_dir_label.text()):
            self.logs_dir_label.setText(os.getcwd())

        temp_dir = QFileDialog.getExistingDirectory(self, "Select Directory", self.logs_dir_label.text())

        if temp_dir is None or len(temp_dir) == 0:
            return

        self.settings.setValue("logs_dir", temp_dir)      
        self.logs_dir = temp_dir
        self.logs_dir_label.setText(f"Logs Directory: {temp_dir}")

    def clear_pipeline(self):
        for item_index in reversed(range(self.pipeline_list.count())):
            self.pipeline_list.takeItem(item_index)
        self.clear_pipeline_btn.setEnabled(False)

    def add_files(self):
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

        if self.file_list_widget.count() != 0 and self.pipeline_list.count() != 0:
            self.apply_button.setEnabled(True)

    def remove_file(self):

        curr_items = self.file_list_widget.selectedItems()
        if curr_items is not None:
            for item in curr_items:
                item_row = self.file_list_widget.row(item)
                self.file_list_widget.takeItem(item_row)
                self.file_list.pop(item_row)

        if self.file_list_widget.count() == 0:
            self.apply_button.setEnabled(False)

    def change_method(self):
        curr_method_index = self.methods_list.currentRow()
        self.methods_layout.setCurrentIndex(curr_method_index)

    def add_to_pipeline(self):

        # Enable apply button only if some file is in the list
        if self.file_list_widget.count() != 0:
            self.apply_button.setEnabled(True)
        self.clear_pipeline_btn.setEnabled(True)

        curr_item = self.methods_list.currentItem()
        curr_item_index = self.methods_list.row(curr_item)
        params_text = self.auto_methods[curr_item_index].params_to_text()
        function_name = self.auto_methods[curr_item_index].function_name()
        params = self.auto_methods[curr_item_index].get_params()
        self.pipeline_list.addItem(FunctionItem(curr_item.text() + (" - " if len(params_text) else "") + params_text, function_name, params))
        
    def remove_from_pipeline(self):
        curr_items = self.pipeline_list.selectedItems()
        if curr_items is not None:
            for item in curr_items:
                item_row = self.pipeline_list.row(item)
                self.pipeline_list.takeItem(item_row)

        if self.pipeline_list.count() == 0:
            self.apply_button.setEnabled(False)
            self.clear_pipeline_btn.setEnabled(False)

    def enable_widgets(self, enable: bool) -> None:
        self.pipeline_list.setEnabled(enable)
        self.file_list_widget.setEnabled(enable)
        self.methods_list.setEnabled(enable)
        self.add_file_btn.setEnabled(enable)
        self.remove_file_btn.setEnabled(enable)
        self.add_to_pipeline_btn.setEnabled(enable)
        self.remove_from_pipeline_btn.setEnabled(enable)
        self.apply_button.setEnabled(enable)
        self.clear_pipeline_btn.setEnabled(enable)

        for method in self.auto_methods:
            method.setEnabled(enable)

    def make_progress_bar(self, maximum):
        
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

    def update_progress(self, val):
        QCoreApplication.processEvents(QEventLoop.ExcludeUserInputEvents, 1000)
        self.progress.setValue(val)
    
    def destroy_progress_bar(self):
        self.enable_widgets(True)
        self.progress.deleteLater()

    def apply_pipeline(self):
        
        logs_file = os.path.join(self.logs_dir, "logs_" + datetime.datetime.now().strftime("%Y-%m-%d_%H%M%S") + ".txt")

        with open(logs_file, "w", encoding="utf-8") as logs:

            steps = len(self.file_list) * self.pipeline_list.count() + 1
            self.make_progress_bar(steps)
            self.update_progress(1)

            for i, file_name in enumerate(self.file_list, 1):
                try:
                    curr_data = Data(file_name)
                    print(curr_data.in_file, file=logs)
                    for item_index in range(self.pipeline_list.count()):
                        # function call
                        print(f"{self.pipeline_list.item(item_index).func}{self.pipeline_list.item(item_index).params}", file=logs)
                        getattr(curr_data, self.pipeline_list.item(item_index).func)(*self.pipeline_list.item(item_index).params)
                        print("OK", file=logs)
                        self.update_progress(self.progress.value() + 1)

                except Exception as e:
                    print(e, file=logs)
                print("---------------------------------", file=logs)

                self.update_progress(i*self.pipeline_list.count())

            # set progress to maximum so that it shows 100 %
            self.update_progress(steps)
            self.destroy_progress_bar()

    def get_string_name(self):
        return "Auto Processing"