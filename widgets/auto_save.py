from PySide6.QtWidgets import QFrame, QGridLayout, QLabel, QPushButton, QFileDialog, QLineEdit
from PySide6.QtGui import QIcon
from PySide6.QtCore import QSettings

from data import Data

import os

class AutoSave(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("method_instance")
        self.icon = QIcon("icons/save.svg")
        self.settings = QSettings()

        self.data_folder = self.settings.value("save_dir", os.getcwd())

        self.change_dir_btn = QPushButton("Change directory")
        self.change_dir_btn.clicked.connect(self.change_folder)

        self.curr_dir = QLabel(f"Directory: {self.data_folder}")

        self.file_tag = QLineEdit("")

        # put windgets into layout
        layout = QGridLayout()
        layout.addWidget(QLabel("Save Data"), 0, 0)
        layout.addWidget(QLabel("Files tag"), 1, 0)
        layout.addWidget(self.file_tag, 1, 1)
        
        layout.addWidget(self.curr_dir, 2, 0)
        layout.addWidget(self.change_dir_btn, 3, 0)
        
        self.setLayout(layout)
    
    def get_params(self) -> tuple[str, str]:
        parameters = (self.data_folder, self.file_tag.text(), )
        return parameters

    def params_to_text(self) -> str:
        return f"folder: {self.data_folder}, tag: {self.file_tag.text()}"

    def change_folder(self):

        if not os.path.exists(self.data_folder):
            self.data_folder = os.getcwd()

        temp_dir = QFileDialog.getExistingDirectory(self, "Select directory", self.data_folder)

        if temp_dir is None or len(temp_dir) == 0:
            return

        self.settings.setValue("save_dir", temp_dir)      

        self.data_folder = temp_dir
        self.curr_dir.setText(f"Directory: {self.data_folder}")

    def reset(self) -> None:
        self.data_folder = os.getcwd()
        self.curr_dir.setText(f"Directory: {self.data_folder}")
        self.file_tag.setText("")

    def function_name(self) -> str:
        return Data.auto_save_data.__name__

    def get_string_name(self):
        return "Save Data"
