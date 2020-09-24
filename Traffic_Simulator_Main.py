import sys
import os
import time

from PyQt5.QtWidgets import QApplication

from Traffic_Simulator_Environment import Traffic_Simulator_Env
from Traffic_Simulator_Widget import mainWidget
from Test_RL_Model import test_model
class Traffic_Simulator():

    def __init__(self):

        # Assign the objects
        self.model = test_model(3, 3)
        self.env = Traffic_Simulator_Env()
        self.widget = mainWidget()

        # Initialize the env for rendering
        self.env.setView(self.widget.ViewTab)

        # Reference the groups in widget
        self.view = self.widget.ViewTab
        self.train = self.widget.trainGroup

        # Settings
        self.autoStepping = False

        self.assignButtons()
#        self.widget.mapSize()
    def assignButtons(self):
        ''' Assign every buttons in widget to a method '''
        self.train.stepButton.clicked.connect(self.envStep)
        self.train.step10Button.clicked.connect(self.step10)
        self.train.autoStepButton.clicked.connect(self.autoStep)

    def reset(self):
        ''' Reset the environment. '''
        self.env.render()
        self.envState = self.env.reset()

    def envStep(self):
        ''' Do one predict and update once. '''
        action = self.model.predict(self.envState)
        state_, reward, terminal, _ = self.env.step(action)

    def step10(self):
        ''' Update ten times. '''
        for i in range(10):
            self.envStep()
            QApplication.processEvents()
            time.sleep(0.1)

    def autoStep(self):
        ''' Toggle auto update. '''
        self.autoStepping = not self.autoStepping
        while self.autoStepping:
            self.envStep()
            QApplication.processEvents()
            time.sleep(0.1)
    def mapbig(self):
        self.ALL_SIZE += 0.1
    def mapsmall(self):
        self.ALL_SIZE -= 0.1
    
#    def mapsize(self):
   #     self.widget.mainWidget.mapsize()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ts = Traffic_Simulator()
    ts.widget.show()
    ts.reset()
    os._exit(app.exec_())