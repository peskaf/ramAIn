from PySide6.QtWidgets import QFrame

class View(QFrame):

    def __init__(self, parent=None):
        super().__init__(parent)

    def reset(self):
        ...

    def get_string_name(self):
        return "View"