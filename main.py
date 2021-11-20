from PySide6.QtWidgets import QApplication, QMainWindow
from plots import PicPlot

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Spectra Observer")
        self.setCentralWidget(PicPlot("Glenodinium.mat"))

app = QApplication([])
main = MainWindow()
main.show()
app.exec()