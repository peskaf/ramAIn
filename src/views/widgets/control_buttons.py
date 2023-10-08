from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QFrame, QPushButton, QHBoxLayout, QWidget
from PySide6.QtCore import Qt


class ControlButtons(QFrame):
    """
    A widget representing control buttons for collapsing, minimizing/maximizing and exiting
    the main window.

    # NOTE: currently not used, implemented for future needs
    """

    def __init__(self, parent: QWidget = None):
        """
        The constructor for control buttons widget.

        Parameters:
            parent (QWidget): Parent widget of this widget. Default: None.
        """

        super().__init__(parent)

        # name for styling in qss file
        self.setObjectName("control_buttons")

        buttons = [
            QPushButton(icon=QIcon("src/resources/icons/collapse.svg")),
            QPushButton(icon=QIcon("src/resources/icons/maximize.svg")),
            QPushButton(icon=QIcon("src/resources/icons/exit.svg")),
        ]

        layout = QHBoxLayout()

        for button in buttons:
            layout.addWidget(button)

        layout.setContentsMargins(0, 0, 0, 0)
        layout.setAlignment(Qt.AlignTop)

        self.setLayout(layout)
