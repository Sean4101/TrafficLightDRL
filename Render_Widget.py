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

#from Environment import flow_1, flow_2, flow_3, flow_4

flow_1 = 0
flow_2 = 0
flow_3 = 0
flow_4 = 0

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
        self.slider = slider()
        self.main_UI()
    
    def main_UI(self):
        mainLayout = QGridLayout()
        mainLayout.addWidget(self.viewTab, 0, 0, 5, 1)
        mainLayout.addWidget(self.slider, 0, 1, 2, 3)
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

class slider(QWidget):
    def __init__(self, parent = None):
        super(slider, self).__init__(parent)

        layout = QVBoxLayout()
        
        self.l0 = QLabel("step dalay   0.0")
        self.l0.setAlignment(Qt.AlignLeft)
        layout.addWidget(self.l0)
        self.sl0 = QSlider(Qt.Horizontal )
        self.sl0.setMinimum(0)
        self.sl0.setMaximum(100)
        self.sl0.setValue(0)
        self.sl0.setTickPosition(QSlider.TicksBelow)
        self.sl0.setTickInterval(5)
        layout.addWidget(self.sl0)
        self.sl0.valueChanged.connect(self.valuechange_0)

        self.l1 = QLabel("Path 1       0")
        self.l1.setAlignment(Qt.AlignLeft)
        layout.addWidget(self.l1)
        self.sl1 = QSlider(Qt.Horizontal )
        self.sl1.setMinimum(0)
        self.sl1.setMaximum(20)
        self.sl1.setValue(0)
        self.sl1.setTickPosition(QSlider.TicksBelow)
        self.sl1.setTickInterval(5)
        layout.addWidget(self.sl1)
        self.sl1.valueChanged.connect(self.valuechange_1)

        self.l2 = QLabel("Path 2       0")
        self.l2.setAlignment(Qt.AlignLeft)
        layout.addWidget(self.l2)
        self.sl2 = QSlider(Qt.Horizontal )
        self.sl2.setMinimum(0)
        self.sl2.setMaximum(20)
        self.sl2.setValue(0)
        self.sl2.setTickPosition(QSlider.TicksBelow)
        self.sl2.setTickInterval(5)
        layout.addWidget(self.sl2)
        self.sl2.valueChanged.connect(self.valuechange_2)

        self.l3 = QLabel("Path 3       0")
        self.l3.setAlignment(Qt.AlignLeft)
        layout.addWidget(self.l3)
        self.sl3 = QSlider(Qt.Horizontal )
        self.sl3.setMinimum(0)
        self.sl3.setMaximum(20)
        self.sl3.setValue(0)
        self.sl3.setTickPosition(QSlider.TicksBelow)
        self.sl3.setTickInterval(5)
        layout.addWidget(self.sl3)
        self.sl3.valueChanged.connect(self.valuechange_3)

        self.l4 = QLabel("Path 4       0")
        self.l4.setAlignment(Qt.AlignLeft)
        layout.addWidget(self.l4)
        self.sl4 = QSlider(Qt.Horizontal )
        self.sl4.setMinimum(0)
        self.sl4.setMaximum(20)
        self.sl4.setValue(0)
        self.sl4.setTickPosition(QSlider.TicksBelow)
        self.sl4.setTickInterval(5)
        layout.addWidget(self.sl4)
        self.sl4.valueChanged.connect(self.valuechange_4)

        self.setLayout(layout)
        self.setWindowTitle("SpinBox")

    def valuechange_0(self):
        value = self.sl0.value()
        self.l0.setText("step dalay   " + str(value/1000))
        print("change 0")

    def valuechange_1(self):
        value = self.sl1.value()
        self.l1.setText("Path 1       " + str(value))
        flow_1 = value
        print("change 1")

    def valuechange_2(self):
        value = self.sl2.value()
        self.l2.setText("Path 2       " + str(value))
        flow_2 = value
        print("change 2")

    def valuechange_3(self):
        value = self.sl3.value()
        self.l3.setText("Path 3       " + str(value))
        flow_3 = value
        print("change 3")

    def valuechange_4(self):
        value = self.sl4.value()
        self.l4.setText("Path 4       " + str(value))
        flow_4 = value
        print("change 4")

    def get_realtime_flow(self):
        flow = [self.sl1.value(), self.sl2.value(), self.sl3.value(), self.sl4.value()]
        return flow
    
    def get_step_sleep(self):
        delay_time = self.sl0.value()
        return delay_time/1000
        

if  __name__ == "__main__":
    app = QApplication(sys.argv)
    widget = mainWidget()
    widget.show()
    os._exit(app.exec_())