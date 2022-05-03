from PySide6.QtWidgets import QFrame, QGridLayout, QLabel, QWidget
from PySide6.QtGui import QIcon

from widgets.data import Data

class AutoCRR(QFrame):
    def __init__(self, parent: QWidget = None) -> None:
        super().__init__(parent)
        self.setObjectName("method_instance")
        self.icon = QIcon("icons/signal.svg")

        # put widgets into layout
        layout = QGridLayout()
        layout.addWidget(QLabel("Cosmic Ray Removal"), 0, 0)
        layout.addWidget(QLabel("No parameters to be set."), 1, 0)
        self.setLayout(layout)

    def get_params(self) -> tuple:
        return ()
    
    def params_to_text(self) -> str:
        return f""

    def reset(self) -> None:
        pass

    def function_name(self) -> str:
        return Data.auto_remove_spikes.__name__

    def get_string_name(self) -> str:
        return "Cosmic Ray Removal"
