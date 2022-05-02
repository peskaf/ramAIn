from PySide6.QtWidgets import QFrame, QPushButton, QHBoxLayout, QVBoxLayout, QLabel, QListWidget, QFileDialog, QWidget
from PySide6.QtCore import Signal, Qt
from PySide6.QtGui import QCursor

import os

# OK
class FilesView(QFrame):
    folder_changed = Signal(str) # custom signal that folder has changed

    def __init__(self, parent: QWidget = None):
        super().__init__() # note that missing parent here

        # name for qss styling
        self.setObjectName("files_view")

        # folder where to look for the data files
        self.data_folder = os.getcwd() + "\data" # TODO: look at \data folder -> it does not have to be there, here for debug only
        # .mat files in curr data folder
        self.file_list = QListWidget(self)

        # widget to display 
        self.currFolderWidget = QLabel(f"Current directory: {self.data_folder}") # os.path.basename()

        # .mat files in given folder
        files = [file for file in os.listdir(self.data_folder) if file.endswith(".mat")]
        self.file_list.addItems(files)

        button = QPushButton("Change directory")
        button.setCursor(QCursor(Qt.PointingHandCursor))
        # connect action to be made when button is clicked
        button.clicked.connect(self.change_folder)

        # layout with curr folder and button to change it
        folder_layout = QHBoxLayout()
        
        folder_layout.addWidget(self.currFolderWidget)
        # fill the area between the widgets
        folder_layout.addStretch()
        folder_layout.addWidget(button)

        # main layout
        layout = QVBoxLayout()

        layout.addWidget(self.file_list)
        layout.addLayout(folder_layout)

        self.setLayout(layout)

    def change_folder(self):
        # os dialog -> will manage that valid directory will be chosen
        self.data_folder = QFileDialog.getExistingDirectory(self, "Select directory")

        # some folder selected
        if self.data_folder:
            self.update_list()
            self.folder_changed.emit(self.data_folder)

    def update_list(self) -> None:
        # get .mat files in cw dir
        files = [file for file in os.listdir(self.data_folder) if file.endswith(".mat")]
        self.file_list.clear()
        self.file_list.addItems(files)
        self.currFolderWidget.setText(f"Current directory: {self.data_folder}")

    def set_curr_file(self, name: str) -> None:
        for i in range(self.file_list.count()):
            if self.file_list.item(i).text() == name:
                self.file_list.setCurrentItem(self.file_list.item(i))