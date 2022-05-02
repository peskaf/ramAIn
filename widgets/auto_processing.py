from PySide6.QtWidgets import QFrame, QLabel, QGridLayout, QRadioButton, QFileDialog, QPushButton, QListWidget, QStackedLayout, QVBoxLayout, QHBoxLayout, QAbstractItemView
from PySide6.QtGui import QIcon
from PySide6.QtCore import Signal, Qt, QSettings

from widgets.auto_cropping import AutoCropping
from widgets.auto_crr import AutoCRR
from widgets.auto_bgr_vancouver import AutoBGRVancouver
from widgets.auto_bgr_airpls import AutoBGRairPLS
from widgets.auto_bgr_poly import AutoBGRPoly
from widgets.auto_bgr_math_morpho import AutoBGRMathMorpho
from widgets.auto_linearization import AutoLinearization
from widgets.auto_decomposition_NMF import AutoNMF
from widgets.auto_save import AutoSave

import numpy as np
import os

class AutoProcessing(QFrame):
    # ... = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.icon = QIcon("icons/settings.svg")
        
        # file selection widget
        self.file_list_widget = QListWidget(self)
        self.file_list = []
        
        self.add_file_btn = QPushButton("Add file")
        self.add_file_btn.clicked.connect(self.add_files)

        self.remove_file_btn = QPushButton("Remove file")
        self.remove_file_btn.clicked.connect(self.remove_file)

        # TODO: methods selection
        self.methods_list = QListWidget(self)
        self.methods_list.currentItemChanged.connect(self.change_method)

        self.auto_cropping = AutoCropping(self)
        self.auto_crr = AutoCRR(self)
        self.auto_bgr_vancouver = AutoBGRVancouver(self)
        self.auto_bgr_airpls = AutoBGRairPLS(self)
        self.auto_bgr_poly = AutoBGRPoly(self)
        self.auto_bgr_math_morpho = AutoBGRMathMorpho(self)
        self.auto_linearization = AutoLinearization(self)
        self.auto_NMF = AutoNMF(self)
        self.auto_save = AutoSave(self)

        self.auto_methods = [
            self.auto_cropping,
            self.auto_crr,
            self.auto_bgr_vancouver,
            self.auto_bgr_airpls,
            self.auto_bgr_poly,
            self.auto_bgr_math_morpho,
            self.auto_linearization,
            self.auto_NMF,
            self.auto_save,

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

        # TODO: methods pipeline + drag & drop reordering!
        self.pipeline_list = QListWidget(self)
        self.pipeline_list.setDragDropMode(QAbstractItemView.InternalMove)


        self.apply_button = QPushButton("Apply")
        self.apply_button.clicked.connect(self.apply_pipeline)

        # common
        
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

        layout.addWidget(self.apply_button)

        self.setLayout(layout)

    def add_files(self):
        file_names, _ = QFileDialog.getOpenFileNames(self, "Select one or more files", os.getcwd(), "*.mat")

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
        # TODO: napsat poradne
        self.pipeline_list.addItem(self.methods_list.currentItem().text())
        

    def apply_pipeline(self):
        ...

    

    def get_string_name(self):
        return "Auto Processing"

    
