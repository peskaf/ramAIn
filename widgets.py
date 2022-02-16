from re import X
from PySide6 import QtGui
from PySide6.QtWidgets import QFileDialog, QFrame, QGraphicsSceneHoverEvent, QGridLayout, QHBoxLayout, QLabel, QLineEdit, QListWidget, QListWidgetItem, QPushButton, QSizePolicy, QStackedLayout, QVBoxLayout, QGraphicsRectItem
from PySide6.QtCore import QRectF, Qt, QSize, Signal
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

        layout.addWidget(QLabel("RamAIn"))
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

        # TODO: pro debug nasledujici radka zakomentovana -> rovnou do data file
        # self.data_folder = os.getcwd() # initially set to current working directory
        self.data_folder = os.getcwd() + "\data" # pro debug

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
class PlotMode():
    NONE = 0
    CROPPING = 1
    COSMIC_RAY_REMOVAL = 2
    BACKGROUND_REMOVAL = 3

class Plot(QFrame):
    region_changed = Signal(str, str) # region x and y changed

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

        # CLICKING MODES
        self.mode = PlotMode.NONE

    def update_data(self, new_x, new_y):
        self.x_data, self.y_data  = new_x, new_y
        self.line.setData(self.x_data, self.y_data)
        self.plot_widget.getPlotItem().enableAutoRange()

    def update_crosshair(self, event):
        coordinates = event[0]
        mouse_point = self.plot_widget.plotItem.vb.mapSceneToView(coordinates)
        self.crosshair_v.setPos(mouse_point.x())
        self.plot_widget.getPlotItem().setLabel("top", f"x = {mouse_point.x():.2f}, y = {self.y_data[np.argmin(np.abs(self.x_data - mouse_point.x()))]:.2f}")

    def hide_crosshair(self):
        self.crosshair_v.hide()
        self.mouse_movement_proxy.blockSignal = True
    
    def show_crosshair(self):
        self.crosshair_v.show()
        self.mouse_movement_proxy.blockSignal = False

    def change_mode(self, new_mode):
        if new_mode == self.mode: # no change
            return

        if new_mode == PlotMode.CROPPING:
            self.hide_crosshair()
            self.add_selection_region()
        elif new_mode == PlotMode.NONE:
            # TODO: checknout jestli opravdu item linear region neni uz reomved a jestli crosshair uz neni ukazany
            self.show_crosshair()
            self.plot_widget.removeItem(self.linear_region)
        else:
            pass

        self.mode = new_mode
    
    def add_selection_region(self):
        # PENS AND BRUSHES
        brush = pg.mkBrush(color=(38,104,103,50))
        hoverBrush = pg.mkBrush(color=(38,104,103,70))
        pen = pg.mkPen(color="#051821")
        hoverPen = pg.mkPen(color="#F58800")

        self.linear_region = pg.LinearRegionItem(
            values=[self.x_data[0], self.x_data[-1]], # min and max from x data (x data is sorted)
            bounds=[self.x_data[0], self.x_data[-1]],
            brush=brush,
            pen=pen,
            hoverBrush=hoverBrush,
            hoverPen=hoverPen)

        self.plot_widget.addItem(self.linear_region)
    
    def update_region(self, new_region):
        self.linear_region.setRegion(new_region)

# TODO: overridovat i region linearni -> menit kurzory; toto se momentalne nepouziva, ale bylo by to mnohem lepsi
class RectRegion(QGraphicsRectItem):
    def mousePressEvent(self, event):
        self.setCursor(Qt.ClosedHandCursor)
        QGraphicsRectItem.mousePressEvent(self, event)

    def mouseReleaseEvent(self, event):
        self.setCursor(Qt.OpenHandCursor)
        QGraphicsRectItem.mouseReleaseEvent(self, event)
    

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

        layout = QHBoxLayout(self)
        layout.addWidget(self.image_view)

        # CLICKING MODES
        self.mode = PlotMode.NONE

    def update_crosshair(self, event):
        pos = event[0]
        self.mouse_point = self.image_view.getView().mapSceneToView(pos)

        self.crosshair_v.setPos(self.mouse_point.x())
        self.crosshair_h.setPos(self.mouse_point.y())

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
    
    def hide_crosshair(self):
        self.crosshair_v.hide()
        self.crosshair_h.hide()
        # cannot block proxy signal here -> needed for x y mousepoint update
    
    def show_crosshair(self):
        self.crosshair_v.show()
        self.crosshair_h.show()

    def change_mode(self, new_mode):
        if new_mode == self.mode: # no change
            return

        if new_mode == PlotMode.CROPPING:
            self.hide_crosshair()
            self.add_selection_region()
        elif new_mode == PlotMode.NONE:
            # TODO: checknout jestli opravdu dany item neni uz removed a jestli crosshair uz neni ukazany
            self.show_crosshair()
            self.image_view.removeItem(self.ROI)
        else:
            pass

        self.mode = new_mode

    def add_selection_region(self):
        # prozatim odkomentovana verze s ROI, pak chci zmenit na RectRegion
        brush = pg.mkBrush(color=(38,104,103,50))
        hoverBrush = pg.mkBrush(color=(38,104,103,70))
        pen = pg.mkPen(color="#F58800")
        hoverPen = pg.mkPen(color="#F8BC24")
        """
        self.rectangle = RectRegion(0, 0, self.image_view.getImageItem().width(), self.image_view.getImageItem().height())
        self.rectangle.setFlag(self.rectangle.ItemIsMovable)
        #self.rectangle.setFlag(self.rectangle.ItemIsFocusable)
        self.rectangle.setCursor(Qt.OpenHandCursor)
        self.rectangle.setPen(pg.mkPen(color="#F58800"))
        self.rectangle.setBrush(pg.mkBrush(color=(245, 136, 0, 50)))

        self.image_view.addItem(self.rectangle)
        self.hide_crosshair()
        """

        self.ROI = pg.RectROI(
            pos=(0,0),
            size=(self.image_view.getImageItem().width(), self.image_view.getImageItem().height()),
            maxBounds=QRectF(0, 0, self.image_view.getImageItem().width(), self.image_view.getImageItem().height()),
            sideScalers=True,
            pen=pen,
            hoverPen=hoverPen)

        self.image_view.addItem(self.ROI)

# METHODS
class Methods(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.setObjectName("methods")

        layout = QHBoxLayout()


        methods = ["View", "Cropping", "Cosmic Ray Removal", "Background Removal"]

        self.list = QListWidget()
        self.list.setObjectName("methods_list") # nastavit velikost pevnou
        self.list.addItems(methods)
        self.list.setCurrentItem(self.list.item(0))
        self.list.setSortingEnabled(False) # do not sort list items (methods)

        self.cropping = Cropping()
        
        self.methods_layout = QStackedLayout()
        self.methods_layout.addWidget(Color(QtGui.QColor(240,240,240)))
        self.methods_layout.addWidget(self.cropping)
        self.methods_layout.setCurrentIndex(0)

        layout.addWidget(self.list)
        layout.addLayout(self.methods_layout)

        self.setLayout(layout)
    
    def set_current_widget(self, mode):
        if mode == PlotMode.CROPPING:
            self.methods_layout.setCurrentIndex(1)
        elif mode == PlotMode.NONE:
            self.methods_layout.setCurrentIndex(0)
        # TODO: dopsat lepe


class Cropping(QFrame):
    plot_x_changed = Signal(str)
    plot_y_changed = Signal(str)
    def __init__(self, parent=None):
        super().__init__(parent)

        layout = QGridLayout()

        text_pic = QLabel("Picture Cropping")
        text_plot = QLabel("Plot Cropping")

        text1 = QLabel("Upper left corner")
        text2 = QLabel("Lower right corner")
        text3 = QLabel("X")
        text4 = QLabel("Y")

        self.inputULX = QLineEdit("0")
        self.inputLRX = QLineEdit("0")
        self.inputULY = QLineEdit("0")
        self.inputLRY = QLineEdit("0")

        text5 = QLabel("X")
        text6 = QLabel("Y")

        self.inputX = QLineEdit("0")
        self.inputY = QLineEdit("0")

        self.button = QPushButton("Apply")

        layout.addWidget(text_pic, 0, 0)

        layout.addWidget(text1, 2, 0)
        layout.addWidget(text2, 3, 0)
        layout.addWidget(text3, 1, 1)
        layout.addWidget(text4, 1, 2)
        layout.addWidget(self.inputULX, 2, 1)
        layout.addWidget(self.inputULY, 2, 2)
        layout.addWidget(self.inputLRX, 3, 1)
        layout.addWidget(self.inputLRY, 3, 2)

        layout.addWidget(text_plot, 4, 0)

        layout.addWidget(text5, 5, 0)
        layout.addWidget(text6, 6, 0)
        layout.addWidget(self.inputX, 5, 1)
        layout.addWidget(self.inputY, 6, 1)

        layout.addWidget(self.button, 6, 2)

        self.setLayout(layout)

        # TODO: pridat validovani inputu apod. !!! (min a max by nemely byt nutne, to se nastavi samo podle bounds)

    def update_region(self, new_region): # set changed values to given line edits
        lo, hi = new_region.getRegion()
        self.inputX.setText(f"{lo:.2f}")
        self.inputY.setText(f"{hi:.2f}")

# MANUAL PREPROCESSING PAGE
class ManualPreprocessing(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)

        # Nothing set yet
        self.files_view = FilesView(parent=self)

        self.curr_folder = self.files_view.data_folder
        self.curr_file = None
        self.curr_data = None


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

        self.methods = Methods()
        self.methods.list.currentItemChanged.connect(self.update_plot_mode)
        layout.addWidget(self.methods)
        

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
            self.update_plot(0, 0)

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

    def send_new_data(self):
        new_region = (float(self.methods.cropping.inputX.text()), float(self.methods.cropping.inputY.text()))
        self.plot.update_region(new_region)

    def update_plot_mode(self, new_mode : QListWidgetItem):
        # nejen plot mode ale celkove vse

        if new_mode.text() == "Cropping":
            # napad! TODO: region vlastne nemazat ale jen schovat na jiné Z aby nebyl vidět -> pak se za vezme dopředu -> takto tam muze byt celou dobu propojeny uz od vytvoreni
            self.plot.change_mode(PlotMode.CROPPING)
            self.pic.change_mode(PlotMode.CROPPING)
            self.methods.set_current_widget(PlotMode.CROPPING)

            self.plot.linear_region.sigRegionChanged.connect(self.methods.cropping.update_region)
            self.methods.cropping.inputX.editingFinished.connect(self.send_new_data)
            self.methods.cropping.inputY.editingFinished.connect(self.send_new_data)

            self.plot.linear_region.sigRegionChanged.emit(self.plot.linear_region) # send curr region to inputs

        elif new_mode.text() == "View":
            self.plot.change_mode(PlotMode.NONE)
            self.pic.change_mode(PlotMode.NONE)
            self.methods.set_current_widget(PlotMode.NONE)
        else:
            pass