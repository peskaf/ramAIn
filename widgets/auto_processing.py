from PySide6.QtWidgets import QFrame, QLabel, QGridLayout, QRadioButton, QFileDialog, QPushButton, QListWidget
from PySide6.QtGui import QIcon
from PySide6.QtCore import Signal, Qt, QSettings

import pyqtgraph as pg
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

        # methods selection
       # self.methods_list = QListWidget(self)


        # methods pipeline

        self.apply_button = QPushButton("Apply")
        self.apply_button.clicked.connect(self.apply_pipeline)

        # common
        
        layout = QGridLayout(self)
        layout.addWidget(self.file_list_widget, 0, 0)
        layout.addWidget(self.add_file_btn, 1, 0)
        layout.addWidget(self.remove_file_btn, 1, 1)

        layout.addWidget(self.apply_button, 7, 0)

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

    def apply_pipeline(self):
        ...

    def get_string_name(self):
        return "Auto Processing"
