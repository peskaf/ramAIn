from PySide6.QtWidgets import QFrame
from PySide6.QtGui import QIcon

class NMF(QFrame):

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("method_instance")
        self.icon = QIcon("icons/view.svg") #TODO: change

    def reset(self):
        ...

    def get_string_name(self):
        return "NMF"