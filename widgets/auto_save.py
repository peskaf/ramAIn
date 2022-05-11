from PySide6.QtWidgets import QFrame, QGridLayout, QLabel, QPushButton, QFileDialog, QLineEdit, QWidget, QVBoxLayout, QHBoxLayout
from PySide6.QtGui import QIcon
from PySide6.QtCore import QSettings, Qt

from data import Data

import os


class AutoSave(QFrame):
    """
    A widget for parameters selection for saving the data in tha automatic pipeline.
    """

    def __init__(self, parent: QWidget = None) -> None:
        """
        The constructor for auto saving parameters selection widget.
  
        Parameters:
            parent (QWidget): Parent widget of this widget. Default: None.
        """

        super().__init__(parent)

        self.setObjectName("method_instance")
        self.icon = QIcon("icons/save.svg")

        self.settings = QSettings()

        self.data_folder = self.settings.value("save_dir", os.getcwd())
        if not os.path.exists(self.data_folder):
            self.data_folder = os.getcwd()

        self.change_dir_btn = QPushButton("Change Directory")
        self.change_dir_btn.clicked.connect(self.change_folder)

        self.curr_dir = QLabel(f"Directory: {self.data_folder}")

        # tag to append to the data file name
        self.file_tag = QLineEdit("")

        # put windgets into layout
        layout = QVBoxLayout()

        grid_layout = QGridLayout()

        grid_layout.addWidget(QLabel("Save Data"), 0, 0)

        grid_layout.addWidget(QLabel("Files Tag"), 1, 0)
        grid_layout.addWidget(self.file_tag, 1, 1)

        grid_layout.setColumnStretch(grid_layout.columnCount(), 1)
        grid_layout.setAlignment(Qt.AlignVCenter)

        layout.addLayout(grid_layout)

        layout.addWidget(self.curr_dir)

        change_btn_layout = QHBoxLayout()
        change_btn_layout.addWidget(self.change_dir_btn)
        change_btn_layout.addStretch()

        layout.addLayout(change_btn_layout)

        self.setLayout(layout)

    def change_folder(self) -> None:
        """
        A function to display file dialog so that folder where to save the data can be selected.
        """

        if not os.path.exists(self.data_folder):
            self.data_folder = os.getcwd()

        temp_dir = QFileDialog.getExistingDirectory(self, "Select directory", self.data_folder)

        if temp_dir is None or len(temp_dir) == 0:
            return

        self.settings.setValue("save_dir", temp_dir)      

        self.data_folder = temp_dir
        self.curr_dir.setText(f"Directory: {self.data_folder}")
    
    def get_params(self) -> tuple[str, str]:
        """
        A function to return parameters of the method with the correct types.

        Returns:
            parameters (tuple): Tuple of method's parameters.
        """

        parameters = (self.data_folder, self.file_tag.text(), )
        return parameters

    def params_to_text(self) -> str:
        """
        A function to return parameters as strings with corresponding meanings.

        Returns:
            str_parameters (str): String of parameters and their meaning.
        """

        str_parameters = f"folder: {self.data_folder}, tag: {self.file_tag.text()}"
        return str_parameters
    
    def function_name(self) -> str:
        """
        A function to return name of the function that this widget represents.

        Returns:
            function_name (str): Name of the function that the parameters from this widget are for.
        """

        return Data.auto_save_data.__name__

    def get_string_name(self) -> str:
        """
        A function to return name of this widget as a string.

        Returns:
            widget_name (str): Name of the widget so that it can be recognized by the user.
        """

        return "Save Data"
