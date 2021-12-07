from re import X
from PySide6 import QtGui
from PySide6.QtWidgets import QFileDialog, QFrame, QHBoxLayout, QLabel, QLayout, QListWidget, QListWidgetItem, QPushButton, QSizePolicy, QVBoxLayout, QWidget
from PySide6.QtCore import Qt, QSize, Signal
import pyqtgraph as pg

import numpy as np
import os

from data import Data

# PLACEHOLDER
class Color(QFrame): # placeholder widget
    def __init__(self, color, parent=None):
        super().__init__(parent)
        self.setObjectName("color")

        self.setAutoFillBackground(True)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        palette = self.palette()
        palette.setColor(QtGui.QPalette.Window, QtGui.QColor(color))
        self.setPalette(palette)

# MENU
class Menu(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("menu")

        icon = QtGui.QIcon("icons/icon.svg")
        buttons = [
            QPushButton("   Manual Preprocessing", icon=icon), # spaces because of spacing between icon and text
            QPushButton("   Database", icon=icon),
            QPushButton("   Project", icon=icon),
            QPushButton("   Settings", icon=icon),
            QPushButton("   Raman", icon=icon)
        ]

        layout = QVBoxLayout()

        for button in buttons:
            # self.setObjectName("nazev") # pripadne pak pro routing tlacitek
            button.setCursor(QtGui.QCursor(Qt.PointingHandCursor))
            layout.addWidget(button)


        layout.setAlignment(Qt.AlignTop)

        self.setLayout(layout)

# HEADER
class Title(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("title")

        layout = QHBoxLayout()

        icon = QLabel()
        icon.setPixmap(QtGui.QPixmap("icons/icon.svg"))
        layout.addWidget(icon)

        layout.addWidget(QLabel("Raman"))
        layout.setAlignment(Qt.AlignCenter)
        layout.setContentsMargins(0,0,0,0)
        self.setLayout(layout)

class ControlButtons(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("control_buttons")

        buttons = [
            QPushButton(icon=QtGui.QIcon("icons/collapse.svg")),
            QPushButton(icon=QtGui.QIcon("icons/maximize.svg")),
            QPushButton(icon=QtGui.QIcon("icons/exit.svg"))
        ]

        layout = QHBoxLayout()

        for button in buttons:
            layout.addWidget(button)
            # button.setCursor(QtGui.QCursor(Qt.PointingHandCursor))

        layout.setContentsMargins(0,0,0,0)
        layout.setAlignment(Qt.AlignTop)
        self.setLayout(layout)

class Header(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("header")

        layout = QHBoxLayout()

        layout.addWidget(Title(self))
        layout.addWidget(Color(QtGui.QColor(240,240,240)))
        layout.addWidget(ControlButtons(self))

        layout.setAlignment(Qt.AlignLeft)
        layout.setContentsMargins(0,0,0,0)

        self.setLayout(layout)

# FILES
class CollapseButton(QPushButton):
    def __init__(self, to_collapse : QFrame, text="", parent=None):
        super().__init__(parent)

        self.to_collapse = to_collapse
        self.setObjectName("collapse_button")
        self.checked_icon = QtGui.QIcon("icons/chevron_down.svg")
        self.unchecked_icon = QtGui.QIcon("icons/chevron_right.svg")

        self.setCheckable(True)
        self.setIcon(self.checked_icon)
        self.setText(text)
        self.setCursor(QtGui.QCursor(Qt.PointingHandCursor))

        self.clicked.connect(self.collapse_layout)

    def collapse_layout(self):
        if self.isChecked():
            self.setIcon(self.unchecked_icon)
            self.to_collapse.hide()
        else:
            self.setIcon(self.checked_icon)
            self.to_collapse.show()

class FilesView(QFrame):
    folder_changed = Signal(str) # custom signal to tell others that folder has changed

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("files_view")

        self.data_folder = os.getcwd() # initially set to current working directory
        layout = QVBoxLayout()

        # .mat files in given folder
        files = [file for file in os.listdir(self.data_folder) if file.endswith(".mat")]

        self.list = QListWidget()
        self.list.addItems(files)

        self.currFolderWidget = QLabel(f"Current directory: {self.data_folder}") # os.path.basename()

        button = QPushButton("Change directory")
        button.clicked.connect(self.change_folder)

        layout.addWidget(self.list)

        folder_layout = QHBoxLayout()
        folder_layout.addWidget(self.currFolderWidget)
        folder_layout.addStretch()
        folder_layout.addWidget(button)

        layout.addLayout(folder_layout)

        self.setLayout(layout)

    def change_folder(self):
        self.data_folder = QFileDialog.getExistingDirectory(self, "Select directory") # os dialog -> will manage that valid directory will be chosen

        if self.data_folder != "": # no folder selected (user exited dialog without selection)
            self.update_list()
            self.folder_changed.emit(self.data_folder)

    def update_list(self):
        files = [file for file in os.listdir(self.data_folder) if file.endswith(".mat")]
        self.list.clear()
        self.list.addItems(files)
        self.currFolderWidget.setText(f"Current directory: {self.data_folder}")

# PLOTS AND PICTURES
class Plot(QFrame):
    def __init__(self, x, y, parent=None):
        super().__init__(parent)

        self.x_data = x
        self.y_data = y

        self.plot_widget = pg.PlotWidget(self)

        # STYLING
        self.plot_widget.setBackground((240,240,240))
        
        styles = { "font-family" : "montserrat", "color" : "#1A4645", "font-size": "14px" } # to qss TODO: HOW?! # style for labels only

        axis_pen = pg.mkPen(color="#051821")
        plot_pen = pg.mkPen(color="#266867", width=1.1)
        crosshair_pen = pg.mkPen(color="black")
        cm = pg.ColorMap(pos=np.linspace(0.0, 1.0, 2), color=[(38, 104, 103, 0), (38, 104, 103, 50)], mapping="diverging") # color same as for plot but in rgba with opacity going from 50 to 0
        brush = cm.getBrush(span=(np.min(self.y_data), np.max(self.y_data)))
        
        axes = ["top", "left", "bottom"]
        for axis in axes:
            self.plot_widget.getPlotItem().getAxis(axis).setPen(axis_pen)
        self.plot_widget.getPlotItem().getAxis(axis).setTextPen(axis_pen)

        # PLOTTING
        self.line = self.plot_widget.plot(self.x_data, self.y_data, pen=plot_pen, brush=brush, fillLevel=np.min(self.y_data))

        # LABELS
        self.plot_widget.getPlotItem().setLabel("top", f"x = {0000.00}, y = {000.00}", **styles)
        self.plot_widget.getPlotItem().setLabel("left", "Intensity (a.u.)", **styles)
        self.plot_widget.getPlotItem().setLabel("bottom", "Raman shift (1/cm)", **styles) # jednotky ?

        # CROSSHAIR
        self.crosshair_v = pg.InfiniteLine(angle=90, movable=False, pen=crosshair_pen)
        self.plot_widget.addItem(self.crosshair_v, ignoreBounds=True)
        self.mouse_movement_proxy = pg.SignalProxy(self.plot_widget.scene().sigMouseMoved, rateLimit=60, slot=self.update_crosshair)

        # LAYOUT
        layout = QHBoxLayout(self)
        layout.addWidget(self.plot_widget)

    def update_data(self, new_x, new_y):
        self.x_data, self.y_data  = new_x, new_y
        self.line.setData(self.x_data, self.y_data)
        self.plot_widget.getPlotItem().enableAutoRange()

    def update_crosshair(self, event):
        coordinates = event[0]
        mouse_point = self.plot_widget.plotItem.vb.mapSceneToView(coordinates)
        self.crosshair_v.setPos(mouse_point.x())
        # pokud by nestačilo ukazovat nejbližší ale chtělo by to podle hodnoty lin. fce, kterou obsahuje plot mezi dvěma body
        # x_index_1, x_index_2 = np.sort(np.argpartition(np.abs(self.x_data - mouse_point.x()), 1)[0:2])
        self.plot_widget.getPlotItem().setLabel("top", f"x = {mouse_point.x():.2f}, y = {self.y_data[np.argmin(np.abs(self.x_data - mouse_point.x()))]:.2f}")


class Picture(QFrame):
    def __init__(self, data, parent=None):
        super().__init__(parent)
        self.win = pg.GraphicsLayoutWidget()
        
        self.image_view = pg.ImageView()
        self.data = data

        # hide histogram and buttons
        self.image_view.ui.histogram.hide()
        self.image_view.ui.roiBtn.hide()
        self.image_view.ui.menuBtn.hide()

        # matplotlib's viridis colormap (6 colors)
        viridis = [(68.0, 1.0, 84.0), (64.0, 67.0, 135.0), (41.0, 120.0, 142.0), (34.0, 167.0, 132.0), (121.0, 209.0, 81.0), (253.0, 231.0, 36.0)]
        cmap = pg.ColorMap(pos=np.linspace(0.0, 1.0, 6), color=viridis)
        self.image_view.setColorMap(cmap)

        self.image_view.setImage(self.data, autoRange=False)

        self.set_limits() # set limits for image manipulation (scrolling, moving)
        
        self.image_view.getView().setDefaultPadding(0)
        self.image_view.getView().setBackgroundColor(QtGui.QColor(240,240,240))

        # Add crosshair lines.
        self.crosshair_v = pg.InfiniteLine(angle=90, movable=False)
        self.crosshair_h = pg.InfiniteLine(angle=0, movable=False)
        self.image_view.addItem(self.crosshair_v, ignoreBounds=True)
        self.image_view.addItem(self.crosshair_h, ignoreBounds=True)

        self.mouse_movement_proxy = pg.SignalProxy(self.image_view.getView().scene().sigMouseMoved, rateLimit=60, slot=self.update_crosshair)
        # self.mouse_zoom_proxy = pg.SignalProxy(self.image_view.getView().sigRangeChanged, rateLimit=60, slot=self.scrolling)

        layout = QHBoxLayout(self)
        layout.addWidget(self.image_view)

    def update_crosshair(self, event):
        pos = event[0]
        self.mouse_point = self.image_view.getView().mapSceneToView(pos)

        if self.mouse_point.x() >= self.data.shape[0] or self.mouse_point.y() >= self.data.shape[1] or self.mouse_point.x() < 0 or self.mouse_point.y() < 0:
            self.image_view.getView().setMouseEnabled(x=False, y=False) # nedovoli scrollovat, pokud nemiri kurzor do obrazku; nukaze ani crosshair
        else:
            self.image_view.getView().setMouseEnabled(x=True, y=True) # jinak je to ok

        self.crosshair_v.setPos(self.mouse_point.x())
        self.crosshair_h.setPos(self.mouse_point.y())
    
    def scrolling(self, event):
        print(event[1])

    def update_image(self, new_data):
        self.data = new_data
        self.image_view.setImage(self.data)
        self.set_limits()
        self.image_view.getView().enableAutoRange() # reset view zoom if zoomed

    def set_limits(self):
        img = self.image_view.getImageItem()
        offset = np.absolute(img.height()-img.width())/2

        if img.height() > img.width():
            self.image_view.getView().setLimits(xMin=-offset, xMax=img.height()-offset, yMin=0, yMax=img.height())
        else:
            self.image_view.getView().setLimits(xMin=0, xMax=img.width(), yMin=-offset, yMax=img.width()-offset)
            

# MANUAL PREPROCESSING PAGE
class ManualPreprocessing(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)

        # Nothing set yet
        self.curr_folder = None # pak sem nejakou hodit
        self.curr_file = None
        self.curr_data = None

        self.files_view = FilesView(parent=self)

        self.pic = Color("#F0F0F0")
        self.pic.setFixedSize(QSize(700,300))

        self.plot = Color("#F0F0F0")
        self.plot.setFixedSize(QSize(300,300))

        self.files_view.list.currentItemChanged.connect(self.update_file) #change of file -> update picture
        self.files_view.folder_changed.connect(self.update_folder)

        layout = QVBoxLayout()
        layout.addWidget(CollapseButton(self.files_view,"Choose File"))
        layout.addWidget(self.files_view)

        self.pic_plot_layout = QHBoxLayout()
        self.pic_plot_layout.addWidget(self.pic)
        self.pic_plot_layout.addWidget(self.plot)
        self.pic_plot_layout.setAlignment(Qt.AlignHCenter)

        layout.addLayout(self.pic_plot_layout)

        layout.setAlignment(Qt.AlignTop)
        self.setLayout(layout)

    def update_pic(self):
        if isinstance(self.pic, Color): # init state
            self.pic = Picture(self.curr_data.averages, self)
            self.pic.setFixedSize(QSize(300,300))

            self.plot = Plot(self.curr_data.x_axis, self.curr_data.data[0,0], self) # initially show [0,0] data
            self.plot.setFixedSize(QSize(700,300))

            self.pic.image_view.getView().scene().sigMouseClicked.connect(self.update_plot_from_mouse_point) # click on picture -> update plot

            # remove placeholders -> needs to be backwards -> widgets would shift to lower position
            for i in reversed(range(self.pic_plot_layout.count())): 
                self.pic_plot_layout.itemAt(i).widget().setParent(None)

            # insert pic&plot
            self.pic_plot_layout.addWidget(self.plot)
            self.pic_plot_layout.addWidget(self.pic)
        else:
            self.pic.update_image(self.curr_data.averages)
            self.update_plot(0, 0) # initially show [0,0] data

    def update_plot(self, x : int, y : int):
        if x < self.curr_data.averages.shape[0] and x >= 0 and y < self.curr_data.averages.shape[1] and y >= 0:
            self.plot.update_data(self.curr_data.x_axis, self.curr_data.data[x,y])

    def update_plot_from_mouse_point(self): # inter func
        self.update_plot(int(np.floor(self.pic.mouse_point.x())), int(np.floor(self.pic.mouse_point.y())))

    def update_file(self, file : QListWidgetItem):
        self.curr_file = file.text()
        self.curr_data = Data(os.path.join(self.curr_folder, self.curr_file))
        self.update_pic()

    def update_folder(self, new_folder):
        self.curr_folder = new_folder