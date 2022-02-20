from PySide6.QtGui import QIcon, QFontDatabase
from PySide6.QtWidgets import QApplication, QHBoxLayout, QMainWindow, QWidget, QVBoxLayout

from widgets.menu import Menu
from widgets.header import Header
from widgets.manual_preprocessing import ManualPreprocessing

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("  " + "RamAIn")
        self.setWindowIcon(QIcon("icons/icon.svg"))

        # self.setWindowFlag(Qt.FramelessWindowHint) # hide windows frame

        # tell how the whole app will look like
        layout = QVBoxLayout()
        layout.addWidget(Header(self))

        layout2 = QHBoxLayout()
        layout2.addWidget(Menu(self))

        # sem pak widget layout kde jsou za sebou ta okna a poradi se meni pomoci tlacitek v menu
        layout2.addWidget(ManualPreprocessing(self))

        layout.addLayout(layout2)
    
        widget = QWidget()
        widget.setLayout(layout)
        self.setCentralWidget(widget)

        QFontDatabase.addApplicationFont("fonts/montserrat.ttf")

        with open("themes/light_style.qss") as f:
            self.setStyleSheet(f.read())


if __name__ == "__main__":
    app = QApplication([])
    main = MainWindow()
    main.show()
    app.exec()