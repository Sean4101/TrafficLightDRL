import sys
import os

import numpy as np

from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *

from matplotlib.figure import Figure
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt4agg import NavigationToolbar2QT as NavigationToolbar


map_size = 5
TITLE_TEXT = "Traffic DRL Simulator"
FONTSIZE = 12


CAR_WIDTH = 2
CAR_HEIGHT = 3

class mainWidget(QWidget):
    def __init__(self, parent=None):
        super (mainWidget, self).__init__(parent)

        self.setGeometry(0, 0, 1500, 900)
        self.setWindowTitle(TITLE_TEXT)
        self.viewTab = ViewTab()
        self.main_UI()
    
    def main_UI(self):
        mainLayout = QGridLayout()
        mainLayout.addWidget(self.viewTab, 0, 0, 1, 1)
        self.setLayout(mainLayout)

class ViewTab(QTabWidget):
    def __init__(self, parent=None):
        super(ViewTab, self).__init__(parent)

        self.setGeometry(0, 0, 900, 900)
        self.tab1 = QWidget()
        self.tab2 = QWidget()

        self.scene = QGraphicsScene()
        self.envView = QGraphicsView(self.scene, self.tab1)
        self.envView.setGeometry(0, 0, 600, 600)
        self.redBrush = QBrush(Qt.red)
        self.yellowBrush = QBrush(Qt.yellow)
        self.greenBrush = QBrush(Qt.green)
        self.blueBrush = QBrush(Qt.blue)
        self.grayBrush = QBrush(Qt.gray)
        self.blackPen = QPen(Qt.black)
        self.grayPen = QPen(Qt.gray)
        
        self.plot = outputPlotSize(FONTSIZE)

        self.addTab(self.tab1,"Environment")
        self.addTab(self.tab2,"Plot")
        self.Tab1_UI()
        self.Tab2_UI()

    def Tab1_UI(self):
        layout = QVBoxLayout()
        layout.addWidget(self.envView)
        self.tab1.setLayout(layout)

    def Tab2_UI(self):
        layout = QVBoxLayout()
        layout.addWidget(self.plot)
        self.tab2.setLayout(layout)

class outputPlotSize(QWidget):

	def __init__(self, fontsize, parent=None):
		super(outputPlotSize, self).__init__(parent)
		self.figure = Figure(figsize=(6,3))
		self.canvas = FigureCanvas(self.figure)
		self.toolbar = NavigationToolbar(self.canvas, self)
		plt.rcParams.update({'font.size': fontsize})

		layout = QGridLayout()
		layout.addWidget(self.canvas,0,0,1,2)
		layout.addWidget(self.toolbar,1,0,1,1)
		self.setLayout(layout)
		self.ax = self.figure.add_subplot(111)

if  __name__ == "__main__":
    app = QApplication(sys.argv)
    widget = mainWidget()
    widget.show()
    os._exit(app.exec_())