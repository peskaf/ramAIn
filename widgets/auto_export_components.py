from PySide6.QtWidgets import QFrame, QGridLayout, QLabel, QPushButton, QFileDialog, QComboBox, QLineEdit, QWidget
from PySide6.QtGui import QIcon
from PySide6.QtCore import QSettings

from data import Data

import os


class AutoExportComponents(QFrame):
    """
    A widget for parameters selection for automatic spectra exporting.
    """

    def __init__(self, parent: QWidget = None) -> None:
        """
        The constructor for auto exporting parameters selection widget.
  
        Parameters:
            parent (QWidget): Parent widget of this widget. Default: None.
        """

        super().__init__(parent)

        self.setObjectName("method_instance")
        self.icon = QIcon("icons/export.svg")

        # app settings for obtaining user's prefered folders
        self.settings = QSettings()

        self.data_folder = self.settings.value("export_dir", os.getcwd())

        self.change_dir_btn = QPushButton("Change directory")
        self.change_dir_btn.clicked.connect(self.change_folder)

        self.curr_dir = QLabel(f"Directory: {self.data_folder}")

        # format of the exported file (components)
        supported_formats = ["png", "pdf", "ps", "eps", "svg"]
        self.format = QComboBox(self)
        self.format.addItems(supported_formats)

        # tag to be appended to data file name
        self.file_tag = QLineEdit("")

        # put windgets into layout
        layout = QGridLayout()
        layout.addWidget(QLabel("Export Components"), 0, 0)

        layout.addWidget(QLabel("Output Format"), 1, 0)
        layout.addWidget(self.format, 1, 1)

        layout.addWidget(QLabel("Files tag"), 2, 0)
        layout.addWidget(self.file_tag, 2, 1)

        layout.addWidget(self.curr_dir, 3, 0)

        layout.addWidget(self.change_dir_btn, 4, 0)
        
        self.setLayout(layout)
    

    def get_params(self) -> tuple[str, str, str]:
        """
        A function to return parameters of the method with the correct types.

        Returns:
            parameters (tuple): Tuple of method's parameters.
        """

        parameters = (self.data_folder, self.file_tag.text(), self.format.currentText(), )
        return parameters

    def params_to_text(self) -> str:
        """
        A function to return parameters as strings with corresponding meanings.

        Returns:
            str_parameters (str): String of parameters and their meaning.
        """

        str_parameters = f"folder: {self.data_folder}, tag: {self.file_tag.text()}, format: {self.format.currentText()}"
        return str_parameters

    def change_folder(self):
        """
        A function to show file dialog so that user can choose directory where to store the output.
        """

        # default is CWD
        if not os.path.exists(self.data_folder):
            self.data_folder = os.getcwd()

        temp_dir = QFileDialog.getExistingDirectory(self, "Select directory", self.data_folder)

        if temp_dir is None or len(temp_dir) == 0:
            return

        self.settings.setValue("export_dir", temp_dir)  

        self.data_folder = temp_dir
        self.curr_dir.setText(f"Directory: {self.data_folder}")


    def function_name(self) -> str:
        """
        A function to return name of the function that this widget represents.

        Returns:
            function_name (str): Name of the function that the parameters from this widget are for.
        """

        return Data.auto_export.__name__

    def get_string_name(self) -> str:
        """
        A function to return name of this widget as a string.

        Returns:
            widget_name (str): Name of the widget so that it can be recognized by the user.
        """

        return "Export Components"
