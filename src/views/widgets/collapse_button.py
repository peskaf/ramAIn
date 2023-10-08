from PySide6.QtGui import QIcon, QCursor
from PySide6.QtWidgets import QFrame, QPushButton, QWidget
from PySide6.QtCore import Qt


class CollapseButton(QPushButton):
    """
    Subclass of `QPushButton` that collapses given `QFrame` when clicked.
    """

    def __init__(self, frame: QFrame, label: str = "", parent: QWidget = None):
        """
        The constructor for button that collapses/expands given `frame` on click.

        Parameters:
            frame (QFrame): QFrame to be collapsed.
            parent (QWidget): Parent widget of this widget. Default: None.
        """

        super().__init__(parent)

        # name for qss styling
        self.setObjectName("collapse_button")

        # frame to be collapsed/expanded on button click
        self.frame = frame

        # icons
        self.checked_icon = QIcon("src/resources/icons/chevron_down.svg")
        self.unchecked_icon = QIcon("src/resources/icons/chevron_right.svg")

        self.setIcon(self.checked_icon)

        # this button has two states, alternating on click
        self.setCheckable(True)

        self.setText(label)

        # cursor on button hover
        self.setCursor(QCursor(Qt.PointingHandCursor))

        # connect function that is to be executed on btn click
        self.clicked.connect(self.collapse_layout)

    def collapse_layout(self) -> None:
        """
        A function to change the icon of the button and to hide/show the frame it is responsible for.
        """

        if self.isChecked():
            self.setIcon(self.unchecked_icon)
            self.frame.hide()
        else:
            self.setIcon(self.checked_icon)
            self.frame.show()
