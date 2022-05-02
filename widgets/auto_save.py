from PySide6.QtWidgets import QFrame, QGridLayout, QLabel, QLineEdit, QRadioButton, QCheckBox, QPushButton, QFileDialog
from PySide6.QtGui import QRegularExpressionValidator, QIcon
from PySide6.QtCore import QSettings

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
        # put windgets into layout
        layout = QGridLayout()
        layout.addWidget(QLabel("Save Data"), 0, 0)
        layout.addWidget(self.curr_dir, 1, 0)
        layout.addWidget(self.change_dir_btn, 2, 0)
        
        self.setLayout(layout)
    
    def get_params(self) -> tuple[str]:
        parameters = (self.data_folder, )
        return parameters

    def params_to_text(self) -> str:
        return f"folder: {self.data_folder}" #TODO

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

    def get_string_name(self):
        return "Save Data"
