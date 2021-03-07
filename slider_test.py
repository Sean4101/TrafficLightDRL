import sys
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

class slider(QWidget):
   def __init__(self, parent = None):
      super(slider, self).__init__(parent)

      layout = QVBoxLayout()
      
      QLabel(l1)
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
      self.setWindowTitle("SpinBox demo")

   def valuechange_1(self):
      value = self.sl1.value()
      self.l1.setText("Path 1       " + str(value))

   def valuechange_2(self):
      value = self.sl2.value()
      self.l2.setText("Path 2       " + str(value))

   def valuechange_3(self):
      value = self.sl3.value()
      self.l3.setText("Path 3       " + str(value))

   def valuechange_4(self):
      value = self.sl4.value()
      self.l4.setText("Path 4       " + str(value))
		

   
	
if __name__ == '__main__':
   app = QApplication(sys.argv)
   ex = slider()
   ex.show()
   sys.exit(app.exec_())