import sys
import os

from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt4agg import NavigationToolbar2QT as NavigationToolbar

from Traffic_Simulator_Environment import Traffic_Simulator_Env


TITLE_TEXT = "Traffic Simulator"
FONTSIZE = 12

class mainWidget(QWidget):
    def __init__(self, parent=None):
        super (mainWidget, self).__init__(parent)

        self.setGeometry(0, 0, 1500, 900)
        self.setWindowTitle(TITLE_TEXT)
        self.env = Traffic_Simulator_Env()
        self.ViewTab = ViewTab(self.env)
        self.paramGroup = ParamGroup()
        self.trainGroup = TrainGroup()
        self.main_UI()
        self.set_action()
    
    def main_UI(self):
        mainLayout = QGridLayout()
        mainLayout.addWidget(self.ViewTab, 0, 0, 2, 1)
        mainLayout.addWidget(self.paramGroup, 0, 1, 1, 1)
        mainLayout.addWidget(self.trainGroup, 1, 1, 1, 1)
        
        self.setLayout(mainLayout)

    def set_action(self):
        self.step()

    def step(self):
        self.trainGroup.stepButton.clicked.connect(self.ViewTab.moveCar)

class ViewTab(QTabWidget):
    def __init__(self, env, parent=None):
        super(ViewTab, self).__init__(parent)

        self.env = env

        self.setGeometry(0, 0, 900, 900)
        self.tab1 = QWidget()
        self.tab2 = QWidget()

        self.scene = QGraphicsScene()
        self.envView = QGraphicsView(self.scene, self.tab1)
        self.envView.setGeometry(0, 0, 600, 600)
        self.redBrush = QBrush(Qt.red)
        self.blueBruch = QBrush(Qt.blue)
        self.blackPen = QPen(Qt.black)
        
        self.plot = outputPlotSize(FONTSIZE)

        self.addTab(self.tab1,"Environment")
        self.addTab(self.tab2,"Plot")
        self.Tab1_UI()
        self.Tab2_UI()
        self.addCar()

    def Tab1_UI(self):
        layout = QVBoxLayout()
        layout.addWidget(self.envView)
        self.tab1.setLayout(layout)

    def Tab2_UI(self):
        layout = QVBoxLayout()
        layout.addWidget(self.plot)
        self.tab2.setLayout(layout)

    def addCar(self):
        self.rect = self.scene.addRect(0, 0, 30, 40, self.blackPen, self.redBrush)
        self.rect.setFlag(QGraphicsItem.ItemIsMovable)
        self.path = self.env.paths[0]
        self.stage = 0
        self.progress = 0

    def moveCar(self):
        if self.progress >= 100:
            self.progress = 0
            self.stage += 1
        self.progress += 10
        
        start = self.path[self.stage][0]
        end = self.path[self.stage][1]

        startCord = self.env.intersections.get(start)
        endCord = self.env.intersections.get(end)
        xpos = (startCord[0]*(100-self.progress)/100 + endCord[0]*self.progress/100)
        ypos = (startCord[1]*(100-self.progress)/100 + endCord[1]*self.progress/100)

        self.rect.setPos(xpos, ypos)
        print(self.rect.x())

class ParamGroup(QGroupBox):
    
    def __init__(self, parent=None):
        super(ParamGroup, self).__init__(parent)

        self.setGeometry(0, 0, 600, 900)
        self.setTitle("Parameters")
        self.actorlrSpin = spinBlock("Actor Learing Rate", 0, 1, double=True, step=0.001, Decimals=3)
        self.criticlrSpin = spinBlock("Critic Learing Rate", 0, 1, double=True, step=0.001, Decimals=3)
        self.gammaSpin = spinBlock("Gamma (Reward Discount)", 0, 1, double=True, step=0.001, Decimals=3)

        layout = QGridLayout()
        layout.addWidget(self.actorlrSpin,0,0,1,1)
        layout.addWidget(self.criticlrSpin,1,0,1,1)
        self.setLayout(layout)

class TrainGroup(QGroupBox):

    def __init__(self, parent=None):
        super(TrainGroup, self).__init__(parent)

        self.setTitle("Train Options")
        self.stepButton = QPushButton("1 Step")

        layout = QGridLayout()
        layout.addWidget(self.stepButton, 0, 0, 1, 1)
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

if __name__ == '__main__':
    app = QApplication(sys.argv)
    main = mainWidget()
    main.show()
    os._exit(app.exec_())