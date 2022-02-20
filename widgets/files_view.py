from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QFrame, QPushButton, QHBoxLayout, QVBoxLayout, QLabel, QListWidget, QFileDialog
from PySide6.QtCore import Signal

import os

class FilesView(QFrame):
    folder_changed = Signal(str) # custom signal to tell others that folder has changed

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("files_view")

        # TODO: pro debug nasledujici radka zakomentovana -> rovnou do data file
        # self.data_folder = os.getcwd() # initially set to current working directory
        self.data_folder = os.getcwd() + "\data" # pro debug

        layout = QVBoxLayout()

        # .mat files in given folder
        files = [file for file in os.listdir(self.data_folder) if file.endswith(".mat")]

        self.list = QListWidget()
        self.list.addItems(files)


        self.currFolderWidget = QLabel(f"Current directory: {self.data_folder}") # os.path.basename()

        button = QPushButton("Change directory")
        button.clicked.connect(self.change_folder)

        layout.addWidget(self.list)

        folder_layout = QHBoxLayout()
        folder_layout.addWidget(self.currFolderWidget)
        folder_layout.addStretch()
        folder_layout.addWidget(button)

        layout.addLayout(folder_layout)

        self.setLayout(layout)

    def change_folder(self):
        self.data_folder = QFileDialog.getExistingDirectory(self, "Select directory") # os dialog -> will manage that valid directory will be chosen

        if self.data_folder != "": # no folder selected (user exited dialog without selection)
            self.update_list()
            self.folder_changed.emit(self.data_folder)

    def update_list(self):
        files = [file for file in os.listdir(self.data_folder) if file.endswith(".mat")]
        self.list.clear()
        self.list.addItems(files)
        self.currFolderWidget.setText(f"Current directory: {self.data_folder}")