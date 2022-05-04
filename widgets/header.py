from PySide6.QtWidgets import QFrame, QHBoxLayout, QWidget
from PySide6.QtCore import Qt

from widgets.title import Title
# NOTE: import currently unsued, will be used in future versions
from widgets.control_buttons import ControlButtons


class Header(QFrame):
    """
    A widget for application header (section above the main section and the menu).
    """

    def __init__(self, parent: QWidget = None) -> None:
        super().__init__(parent)

        # name for styling in qss file
        self.setObjectName("header")

        layout = QHBoxLayout()

        layout.addWidget(Title())

        # fills the area between the widgets (title & constrol btns)
        layout.addStretch()

        # control buttons for frameless version
        # NOTE: for the future app styling
        # layout.addWidget(ControlButtons())

        layout.setAlignment(Qt.AlignLeft)
        layout.setContentsMargins(0,0,0,0)

        self.setLayout(layout)
