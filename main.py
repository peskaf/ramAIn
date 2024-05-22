import sys
import os
from PySide6 import QtGui

from ramain.app import App

basedir = os.path.dirname(__file__)

app = App(sys.argv)
app.setWindowIcon(QtGui.QIcon(os.path.join(basedir, "RamAIn.ico")))
sys.exit(app.exec())
