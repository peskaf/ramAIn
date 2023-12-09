from PySide6.QtWidgets import (
    QFrame,
    QPushButton,
    QHBoxLayout,
    QVBoxLayout,
    QLabel,
    QListWidget,
    QFileDialog,
    QWidget,
)
from PySide6.QtCore import Signal, Qt, QSettings
from PySide6.QtGui import QCursor

from utils.settings import SETTINGS

import os


class FilesView(QFrame):
    """
    A widget for visualization of files from selected folder.
    """

    folder_changed = Signal(str)  # custom signal that folder has changed

    def __init__(self, format: str, parent: QWidget = None) -> None:
        """
        The constructor for file list widget that allows selection of the file folder.

        Parameters:
            format (str): Format (extension) of the files to be displayed.
            parent (QWidget): Parent widget of this widget. Default: None.
        """

        super().__init__()  # NOTE: parent is missing here due to the bug in the library

        # name for qss styling
        self.setObjectName("files_view")

        self.format = format

        # folder where to look for the data files
        self.data_folder = SETTINGS.value("source_dir", os.getcwd())
        if not os.path.exists(self.data_folder):
            self.data_folder = os.getcwd()

        # .mat files in curr data folder
        self.file_list = QListWidget(self)

        # widget to display
        self.curr_directory = QLabel(f"Current directory: {self.data_folder}")

        # .mat files in given folder
        files = [
            file for file in os.listdir(self.data_folder) if file.endswith(self.format)
        ]
        self.file_list.addItems(files)

        button = QPushButton("Change directory")
        button.setCursor(QCursor(Qt.PointingHandCursor))

        # connect action to be made when button is clicked
        button.clicked.connect(self.change_folder)

        # layout with curr folder and button to change it
        folder_layout = QHBoxLayout()

        folder_layout.addWidget(self.curr_directory)

        # fill the area between the widgets
        folder_layout.addStretch()
        folder_layout.addWidget(button)

        # main layout
        layout = QVBoxLayout()

        layout.addWidget(self.file_list)
        layout.addLayout(folder_layout)

        self.setLayout(layout)

    def change_folder(self) -> None:
        """
        A function to provide OS file dialog that will manage that valid directory will be chosen.
        """

        temp_data_folder = QFileDialog.getExistingDirectory(
            self, "Select directory", self.data_folder
        )

        # some folder selected
        if temp_data_folder is not None and len(temp_data_folder) != 0:
            self.data_folder = temp_data_folder
            self.update_list()
            self.folder_changed.emit(self.data_folder)
            SETTINGS.setValue("source_dir", self.data_folder)

    def update_list(self) -> None:
        """
        A function to update the list of visible files.
        """

        # get .mat files in curr data folder
        files = [
            file for file in os.listdir(self.data_folder) if file.endswith(self.format)
        ]
        # remove everything that was present before
        self.file_list.clear()
        self.file_list.addItems(files)
        self.curr_directory.setText(f"Current directory: {self.data_folder}")

    def set_curr_file(self, name: str) -> None:
        """
        A finction to set currently selected file in the list to file with given `name`.
        """

        for i in range(self.file_list.count()):
            if self.file_list.item(i).text() == name:
                self.file_list.setCurrentItem(self.file_list.item(i))
