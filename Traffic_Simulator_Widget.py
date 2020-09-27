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
TITLE_TEXT = "Traffic Simulator"
FONTSIZE = 12


CAR_WIDTH = 2
CAR_HEIGHT = 3

class mainWidget(QWidget):
    def __init__(self, parent=None):
        super (mainWidget, self).__init__(parent)

        self.setGeometry(0, 0, 1500, 900)
        self.setWindowTitle(TITLE_TEXT)
        self.ViewTab = ViewTab()
        self.paramGroup = ParamGroup()
        self.trainGroup = TrainGroup()
        self.renderGroup = RenderGroup()
        self.main_UI()
    
    def main_UI(self):
        mainLayout = QGridLayout()
        mainLayout.addWidget(self.ViewTab, 0, 0, 3, 1)
        mainLayout.addWidget(self.paramGroup, 0, 1, 1, 1)
        mainLayout.addWidget(self.trainGroup, 1, 1, 1, 1)
        mainLayout.addWidget(self.renderGroup, 2, 1, 1, 1)
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
        self.blueBrush = QBrush(Qt.blue)
        self.grayBrush = QBrush(Qt.gray)
        self.blackPen = QPen(Qt.black)
        self.grayPen = QPen(Qt.gray)
        
        self.plot = outputPlotSize(FONTSIZE)

        self.addTab(self.tab1,"Environment")
        self.addTab(self.tab2,"Plot")
        self.Tab1_UI()
        self.Tab2_UI()

        self.intersections = {}
        self.roads = {}
        self.paths = {}
        self.cars = [] 

    def Tab1_UI(self):
        layout = QVBoxLayout()
        layout.addWidget(self.envView)
        self.tab1.setLayout(layout)

    def Tab2_UI(self):
        layout = QVBoxLayout()
        layout.addWidget(self.plot)
        self.tab2.setLayout(layout)

class ParamGroup(QGroupBox):
    
    def __init__(self, parent=None):
        super(ParamGroup, self).__init__(parent)

        self.setGeometry(0, 0, 600, 900)
        self.setTitle("Parameters")
        self.actorlrSpin = spinBlock("Actor Learning Rate", 0, 1, double=True, step=0.001, Decimals=3)
        self.criticlrSpin = spinBlock("Critic Learning Rate", 0, 1, double=True, step=0.001, Decimals=3)
        self.gammaSpin = spinBlock("Gamma (Reward Discount)", 0, 1, double=True, step=0.001, Decimals=3)
        
        layout = QGridLayout()
        layout.addWidget(self.actorlrSpin,0,0,1,1)
        layout.addWidget(self.criticlrSpin,1,0,1,1)
        layout.addWidget(self.gammaSpin,2,0,1,1)
        

        self.setLayout(layout)

class TrainGroup(QGroupBox):

    def __init__(self, parent=None):
        super(TrainGroup, self).__init__(parent)

        self.setTitle("Train Options")
        self.stepButton = QPushButton("1 Step")
        self.step10Button = QPushButton("10 Step")
        self.autoStepButton = QPushButton("Auto Step")
        layout = QGridLayout()
        layout.addWidget(self.stepButton, 0, 0, 1, 1)
        layout.addWidget(self.step10Button, 1, 0, 1, 1)
        layout.addWidget(self.autoStepButton, 2, 0, 1, 1)

        self.setLayout(layout)
 
class RenderGroup(QGroupBox):
    def __init__(self, parent=None):
        super(RenderGroup, self).__init__(parent)

        self.setTitle("Render Options")
        self.resetButton = QPushButton("Reset")

        layout = QGridLayout()

        layout.addWidget(self.resetButton ,0 ,0 ,1 ,1)
        self.scalingSpin = spinBlock("scaling", 1, 10, double=True, step=0.1, Decimals=1)
        layout.addWidget(self.scalingSpin,3,0,1,1)

        self.setLayout(layout)
        


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

class spinBlock(QGroupBox):
    
	def __init__(self, title, minValue, maxValue, double = False, step = 1, Decimals = 2, parent=None):
		super(spinBlock, self).__init__(parent)
		if (double):
			self.spin = QDoubleSpinBox()
			self.spin.setDecimals(Decimals)
		else:
			self.spin = QSpinBox()

		self.spin.setRange(minValue, maxValue)
		self.spin.setSingleStep(step)
		self.setTitle(title)

		layout = QHBoxLayout() 
		layout.addWidget(self.spin)     
		self.setLayout(layout)


if  __name__ == "__main__":
    app = QApplication(sys.argv)
    widget = mainWidget()
    widget.show()
    os._exit(app.exec_())

