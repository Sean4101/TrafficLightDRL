import sys
import os
import time
import numpy as np

from PyQt5.QtWidgets import QApplication

from Traffic_Simulator_Environment import Traffic_Simulator_Env
from Traffic_Simulator_Widget import mainWidget
# from Test_RL_Model import test_model
from SAC_Agent import Agent
from Environment_Objects import Signals

class Traffic_Simulator():

    def __init__(self):

        # Assign the objects
        self.env : Traffic_Simulator_Env = Traffic_Simulator_Env()  # A environment contains cars, roads, traffic signals and
                                            # calculates how they behave.

        self.widget = mainWidget()          # A GUI window with buttons and spinboxes for training,
                                            # also render the environment. 

        self.agent = Agent(input_dims=self.env.observation_space_shape, env=self.env, n_actions=self.env.n_action)

        # Reference the groups in widget
        self.view = self.widget.ViewTab
        self.trainGroup = self.widget.trainGroup
        self.paramGroup = self.widget.paramGroup
        self.renderGroup = self.widget.renderGroup

        # Settings
        self.autoStepping = False

        self.assignEvents()
        self.scale()

    def initialize(self):
        ''' Initialize the application. '''
        self.env.toggleRender(self.renderGroup.renderCheckBox.isChecked(), self.view)
        self.env.scale = self.renderGroup.scalingSpin.spin.value()
        self.reset()
        
    def assignEvents(self):
        ''' Assign every buttons in widget to a method '''
        self.trainGroup.stepButton.clicked.connect(self.envStep)
        self.trainGroup.autoStepButton.clicked.connect(self.autoStep)
        self.trainGroup.resetButton.clicked.connect(self.reset)
         
        self.renderGroup.renderCheckBox.clicked.connect(self.renderCheck)
        self.renderGroup.scalingSpin.spin.valueChanged.connect(self.scale)
        
    def reset(self):
        self.env.clearCarItems()
        self.envState = self.env.reset()
        self.env.render()

        self.autoStepping = False
        val = self.renderGroup.scalingSpin.spin.minimum()
        self.renderGroup.scalingSpin.spin.setValue(val)

        self.score = 0

    def envStep(self):

        action = self.agent.choose_action(self.envState)
        print(action)
        self.env.update_reward = 0
        self.env.makeAction(action)
        for i in range(10):
            self.env.update()
            self.env.render(onlyNonStatic=True)
            QApplication.processEvents()
            if self.trainGroup.delayCheckBox.isChecked():
                time.sleep(0.01)
        state_, reward, terminal, _ = self.env.getStateAndReward()

        self.score += reward
        self.envState = state_

    def autoStep(self):
        ''' Toggle auto update. '''
        self.autoStepping = not self.autoStepping
        while self.autoStepping:
            self.envStep()

    def scale(self):
        self.env.scale = self.renderGroup.scalingSpin.spin.value()
        self.env.render()

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
    ts.initialize()

    # Exit app.
    os._exit(app.exec_())