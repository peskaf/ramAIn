from PySide6.QtWidgets import QFrame, QVBoxLayout, QListWidgetItem, QMessageBox, QScrollArea, QSizePolicy
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QIcon, QPixmap

from widgets.files_view import FilesView
from widgets.collapse_button import CollapseButton
from widgets.decomposition_methods import DecompositionMethods
from widgets.component import Component

from widgets.data import Data

import os

class SpectraDecomposition(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.icon = QIcon("icons/view.svg") #TODO: change

        # files
        self.files_view = FilesView()

        self.curr_folder = self.files_view.data_folder
        self.curr_file = None
        self.curr_data = None

        self.files_view.file_list.currentItemChanged.connect(self.update_file) # change of file -> update picture
        self.files_view.folder_changed.connect(self.update_folder)

        # TODO: method selection + params
        self.methods = DecompositionMethods()

        # TODO: results visualization
        self.components_area = QScrollArea()
        self.components_area.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.components_frame = QFrame(self.components_area)
        self.components = QVBoxLayout()
        self.components_area.setWidgetResizable(True)

        self.components_frame.setLayout(self.components)
        self.components_frame.setMouseTracking(True)

        self.components_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.components_area.setWidgetResizable(True)

        self.components_area.setWidget(self.components_frame)

        # misc
        self.init_file_error_widget()

        layout = QVBoxLayout()
        layout.addWidget(CollapseButton(self.files_view, "Choose File"))
        layout.addWidget(self.files_view)
        layout.addWidget(CollapseButton(self.methods, "Choose Method"))
        layout.addWidget(self.methods)
        layout.addWidget(self.components_area)
        layout.setAlignment(Qt.AlignTop)

        self.setLayout(layout)

    def update_file(self, file: QListWidgetItem) -> None:
        
        temp_curr_file = file.text()
        try:
            self.curr_data = Data(os.path.join(self.curr_folder, temp_curr_file))
        except:
            self.file_error.show()
            return

        # TODO: predelat na metody dekompozice
        """
        if not self.methods.list.isEnabled():
            self.methods.list.setEnabled(True)
        self.methods.reset()
        """

        self.curr_file = temp_curr_file
        self.components.addWidget(Component(self.curr_data.x_axis, self.curr_data.data[0,0,:], self.curr_data.averages, self.components_frame))

    def update_folder(self, new_folder_name: str):
        # TODO: vyrasit jak se ma widget chovat pri zmene adresare k novemu souboru aktualnimu
        self.curr_folder = new_folder_name

    def init_file_error_widget(self):
        self.file_error = QMessageBox()
        self.file_error.setIconPixmap(QPixmap("icons/x-circle.svg"))
        self.file_error.setText("File has invalide structure and cannot be loaded.")
        self.file_error.setInformativeText("RamAIn currently supports only .mat files originally produced by WITec spectroscopes. Sorry :(")
        self.file_error.setWindowTitle("Invalid file structure")
        self.file_error.setWindowIcon(QIcon("icons/message.svg"))
        self.file_error.setStandardButtons(QMessageBox.Ok)

    def get_string_name(self):
        return "Spectra Decomposition"