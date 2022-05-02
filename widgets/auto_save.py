from PySide6.QtWidgets import QFrame, QGridLayout, QLabel, QLineEdit, QRadioButton, QCheckBox, QPushButton
from PySide6.QtGui import QRegularExpressionValidator, QIcon
from PySide6.QtCore import Signal

class AutoSave(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("method_instance")
        self.icon = QIcon("icons/save.svg")

        # put windgets into layout
        layout = QGridLayout()
        layout.addWidget(QLabel("Save output"), 0, 0)
        layout.addWidget(QLabel("Folder"), 1, 0)
        # TODO: insert button that triggers dialog and label that displays selected folder
      
        self.setLayout(layout)
    
    def get_params(self) -> tuple[str]:
        parameters = (..., )
        return parameters

    def reset(self) -> None:
        ...

    def get_string_name(self):
        return "Save Output"
