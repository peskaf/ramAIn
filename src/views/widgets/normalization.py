from PySide6.QtWidgets import (
    QFrame,
    QWidget,
    QGridLayout,
    QPushButton,
)
from PySide6.QtGui import QIcon
from PySide6.QtCore import Signal


class Normalization(QFrame):
    """
    A widget for parameters selection for the normalization method.
    """

    apply_clicked = Signal()

    def __init__(self, parent: QWidget = None) -> None:
        """
        The constructor for manual normalization parameters selection widget.

        Parameters:
            parent (QWidget): Parent widget of this widget. Default: None.
        """

        super().__init__(parent)

        self.setObjectName("method_instance")
        self.icon = QIcon("src/resources/icons/normalize.svg")

        self.apply_button = QPushButton("Apply")
        self.apply_button.clicked.connect(self.apply_clicked.emit)

        # put windgets into layout
        layout = QGridLayout()

        layout.addWidget(self.apply_button, 1, 3)

        layout.setColumnStretch(2, 1)

        self.setLayout(layout)

    def reset(self) -> None:
        """
        A function to reset the widget to its default state.
        """

        pass

    def get_string_name(self) -> str:
        """
        A function to return name of this widget as a string.

        Returns:
            widget_name (str): Name of the widget so that it can be recognized by the user.
        """

        return "Water Normalization"
