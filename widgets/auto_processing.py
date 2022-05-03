from PySide6.QtWidgets import QFrame, QLabel, QGridLayout, QRadioButton, QFileDialog, QPushButton, QListWidget, QStackedLayout, QVBoxLayout, QHBoxLayout, QAbstractItemView, QListWidgetItem
from PySide6.QtGui import QIcon
from PySide6.QtCore import Signal, Qt, QSettings

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

import numpy as np
import os

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
        self.file_list = []
        
        self.add_file_btn = QPushButton("Add file")
        self.add_file_btn.clicked.connect(self.add_files)

        self.remove_file_btn = QPushButton("Remove file")
        self.remove_file_btn.clicked.connect(self.remove_file)

        # methods selection
        self.methods_list = QListWidget(self)
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

        self.add_to_pipeline_btn = QPushButton("Add to pipeline")
        self.add_to_pipeline_btn.clicked.connect(self.add_to_pipeline)

        # methods pipeline
        self.pipeline_list = QListWidget(self)
        self.pipeline_list.setDragDropMode(QAbstractItemView.InternalMove)

        # TODO: fill with function and params
        self.pipeline_functions = []
        self.pipeline_params = []

        self.remove_from_pipeline_btn = QPushButton("Remove step")
        self.remove_from_pipeline_btn.clicked.connect(self.remove_from_pipeline)

        self.apply_button = QPushButton("Apply")
        self.apply_button.clicked.connect(self.apply_pipeline)

        # common
        self.log_file = ...
        
        layout = QVBoxLayout(self)
        layout.addWidget(self.file_list_widget)

        buttons_layout = QHBoxLayout()
        buttons_layout.addWidget(self.remove_file_btn)
        buttons_layout.addStretch()
        buttons_layout.addWidget(self.add_file_btn)

        layout.addLayout(buttons_layout)

        methods_list_layout = QHBoxLayout()
        methods_list_layout.addWidget(self.methods_list)
        methods_list_layout.addLayout(self.methods_layout)

        layout.addLayout(methods_list_layout)
        
        add_method_layout = QHBoxLayout()
        add_method_layout.addStretch()
        add_method_layout.addWidget(self.add_to_pipeline_btn)

        layout.addLayout(add_method_layout)

        layout.addWidget(self.pipeline_list)

        remove_btn_layout = QHBoxLayout()
        remove_btn_layout.addStretch()
        remove_btn_layout.addWidget(self.remove_from_pipeline_btn)

        layout.addLayout(remove_btn_layout)
        layout.addWidget(self.apply_button)

        self.setLayout(layout)

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

    def remove_file(self):

        curr_items = self.file_list_widget.selectedItems()
        if curr_items is not None:
            for item in curr_items:
                item_row = self.file_list_widget.row(item)
                self.file_list_widget.takeItem(item_row)
                self.file_list.pop(item_row)

    def change_method(self):
        curr_method_index = self.methods_list.currentRow()
        self.methods_layout.setCurrentIndex(curr_method_index)

    def add_to_pipeline(self):
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

    def apply_pipeline(self):
        #TODO: add progress bar update after each iteration
        for file_name in self.file_list:
            try:
                curr_data = Data(file_name)
                print(curr_data.in_file)
                # TODO: call functions on that data
                for item_index in range(self.pipeline_list.count()):
                    # function call
                    getattr(curr_data, self.pipeline_list.item(item_index).func)(*self.pipeline_list.item(item_index).params)
                    #TODO: some logging that it was OK
                    #TODO: add progress bar update after each iteration
            except Exception as e:
                print(f"{e} ({self.pipeline_list.item(item_index).func}{self.pipeline_list.item(item_index).params})")

    def get_string_name(self):
        return "Auto Processing"
