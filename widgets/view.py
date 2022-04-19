from PySide6.QtWidgets import QFrame

class View(QFrame):

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("method_instance")

    def reset(self):
        ...

    def get_string_name(self):
        return "View"