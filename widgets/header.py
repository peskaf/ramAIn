from PySide6.QtWidgets import QFrame, QHBoxLayout
from PySide6.QtCore import Qt

from widgets.title import Title
from widgets.control_buttons import ControlButtons

# OK
class Header(QFrame):
    def __init__(self):
        super(Header, self).__init__()

        # name for styling in qss file
        self.setObjectName("header")

        layout = QHBoxLayout()

        layout.addWidget(Title())

         # fills the area between the widgets (title & constrol btns)
        layout.addStretch()

        layout.addWidget(ControlButtons())

        layout.setAlignment(Qt.AlignLeft)
        layout.setContentsMargins(0,0,0,0)

        self.setLayout(layout)