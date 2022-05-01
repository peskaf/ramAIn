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
        self.file_list = QListWidget()
        
        self.add_file_btn = QPushButton("Add file")
        self.add_file_btn.clicked.connect(self.add_files)

        self.remove_file_btn = QPushButton("Remove file")
        self.remove_file_btn.clicked.connect(self.remove_file)
        
        layout = QGridLayout()
        layout.addWidget(self.add_file_btn, 1, 0)
        layout.addWidget(self.remove_file_btn, 1, 1)
        layout.addWidget(self.file_list, 0, 0)

        self.setLayout(layout)

    def add_files(self):
        file_names, _ = QFileDialog.getOpenFileNames(self, "Select one or more files", os.getcwd(), "*.mat")

        for file_name in file_names:
            self.file_list.addItem(os.path.basename(file_name))

    def remove_file(self):

        curr_items = self.file_list.selectedItems()
        if curr_items is not None:
            for item in curr_items:
                self.file_list.takeItem(self.file_list.row(item))

    def get_string_name(self):
        return "Auto Processing"
