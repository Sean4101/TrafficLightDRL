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
        self.model = test_model(3, 3)       # A deep reinforcement model, which controls the signals
                                            # in the environment also gets info from it.

        self.env = Traffic_Simulator_Env()  # A environment contains cars, roads, traffic signals and
                                            # calculates how they behave.

        self.widget = mainWidget()          # A GUI window with buttons and spinboxes for training,
                                            # also render the environment. 

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
        self.env.enableRender(self.view)
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

    # This will create a Traffic_Simulator object. It contains a widget
    # object which creates a GUI window, and a environment object which
    # creates and calculates what happen in the simulated traffic system.
    ts = Traffic_Simulator()

    # Show window.
    ts.widget.show()

    #Rreset the environment and configures whether to render or not.
    ts.reset()

    # Exit app.
    os._exit(app.exec_())