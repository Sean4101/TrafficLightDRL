import sys
import os
import time

from PyQt5.QtWidgets import QApplication

from Traffic_Simulator_Environment import Traffic_Simulator_Env
from Traffic_Simulator_Widget import mainWidget
from Test_RL_Model import test_model
from Environment_Objects import Signals

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
        self.trainGroup = self.widget.trainGroup
        self.paramGroup = self.widget.paramGroup
        self.renderGroup = self.widget.renderGroup

        # Settings
        self.autoStepping = False

        self.assignEvents()
        self.scale()

    def reset(self):
        ''' Reset the application. '''
        self.envState = self.env.reset()
        
        self.env.toggleRender(self.renderGroup.renderCheckBox.isChecked(), self.view)
        self.env.scale = self.renderGroup.scalingSpin.spin.value()
        self.env.render()
        
    def assignEvents(self):
        ''' Assign every buttons in widget to a method '''
        self.trainGroup.stepButton.clicked.connect(self.envStep)
        self.trainGroup.autoStepButton.clicked.connect(self.autoStep)
        self.trainGroup.resetButton.clicked.connect(self.resetenv)
        
        self.renderGroup.renderCheckBox.clicked.connect(self.renderCheck)
        self.renderGroup.scalingSpin.spin.valueChanged.connect(self.scale)

    def envStep(self):
        ''' Do one predict and update once. '''
        action = self.model.predict(self.envState)
        self.env.makeAction(action)
        for i in range(10):
            self.env.update()
            self.env.render(onlyNonStatic=True)
            QApplication.processEvents()
            if self.trainGroup.delayCheckBox.isChecked():
                time.sleep(0.01)
        state_, reward, terminal, _ = self.env.getStateAndReward()

    def autoStep(self):
        ''' Toggle auto update. '''
        self.autoStepping = not self.autoStepping
        while self.autoStepping:
            self.envStep()

    def scale(self):
        self.env.scale = self.renderGroup.scalingSpin.spin.value()
        self.env.render()
        
    def resetenv(self):
        self.view.scene.clear()
        self.env.reset()
        self.env.render()

        self.autoStepping = False
        val = self.renderGroup.scalingSpin.spin.minimum()
        self.renderGroup.scalingSpin.spin.setValue(val)

    def renderCheck(self):
        self.env.toggleRender(self.renderGroup.renderCheckBox.isChecked(), self.view)
        self.env.render()

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