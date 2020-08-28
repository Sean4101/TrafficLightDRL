from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget
import sys

class test_window(QMainWindow):
    def __init__(self):
        super(test_window, self).__init__()
        self.setGeometry(200, 200, 800, 600)
        self.setWindowTitle("Traffic Simulator Environment")
        self.initUI()
    
    def initUI(self):
        self.label = QtWidgets.QLabel(self)
        self.label.setText("qwe")
        self.label.move(50, 50)

        self.b1 = QtWidgets.QPushButton(self)
        self.b1.setText("Hello")
        self.b1.clicked.connect(self.bruh)
    
    def bruh(self):
        self.label.setText("eww")
        self.update()

    def update(self):
        self.label.adjustSize()



def window():
    app = QApplication(sys.argv)
    win = test_window()


    win.show()
    sys.exit(app.exec_())

window()
