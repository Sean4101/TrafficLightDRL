import sys
import os

from PyQt5.QtWidgets import QApplication

from Traffic_Simulator_Environment import Traffic_Simulator_Env
from Traffic_Simulator_Widget import mainWidget
from Test_RL_Model import test_model


class Traffic_Simulator():

    def __init__(self):

        self.model = test_model(3, 3)
        self.env = Traffic_Simulator_Env()
        self.widget = mainWidget()

        self.env.setView(self.widget.ViewTab)

        self.view = self.widget.ViewTab
        self.train = self.widget.trainGroup

        self.assignButtons()

    def assignButtons(self):
        self.train.stepButton.clicked.connect(self.envStep)

    def envStep(self):
        self.env.step(1)
        

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ts = Traffic_Simulator()
    ts.env.render()
    ts.env.reset()
    ts.widget.show()
    os._exit(app.exec_())