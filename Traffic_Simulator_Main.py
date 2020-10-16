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
        self.train = self.widget.trainGroup
        self.param = self.widget.paramGroup
        self.render = self.widget.renderGroup

        #env
        self.scale = self.env.renderScale
        # Settings
        self.autoStepping = False

        self.assignEvents()
        
    def assignEvents(self):
        ''' Assign every buttons in widget to a method '''
        self.train.stepButton.clicked.connect(self.envStep)
        self.train.step10Button.clicked.connect(self.step10)
        self.train.autoStepButton.clicked.connect(self.autoStep)
        self.train.trafficLightButton.clicked.connect(self.trafficlight)

        
        self.render.scalingSpin.spin.valueChanged.connect(self.scale)

        self.render.resetButton.clicked.connect(self.resetenv)

    def reset(self):
        ''' Reset the environment. '''
        self.env.enableRender(self.view)
        self.envState = self.env.reset()

    def envStep(self):
        ''' Do one predict and update once. '''
        action = self.model.predict(self.envState)
        state_, reward, terminal, _ = self.env.step(action)
        self.env.renderUpdate(self.render.scalingSpin.spin.value())

    def step10(self):
        ''' Update ten times. '''
        for i in range(10):
            self.envStep()
            QApplication.processEvents()
            time.sleep(0.01)

    def autoStep(self):
        ''' Toggle auto update. '''
        self.autoStepping = not self.autoStepping
        while self.autoStepping:
            self.envStep()
            QApplication.processEvents()
            time.sleep(0.01)

    def trafficlight(self):
        #test
        if self.env.sig1.signal == Signals.RED:
            self.env.sig1.signal = Signals.GREEN
        elif self.env.sig1.signal == Signals.GREEN:
            self.env.sig1.signal = Signals.RED
        self.env.tsRender(self.render.scalingSpin.spin.value())


    def scale(self):
        self.env.render(self.render.scalingSpin.spin.value())
        
    def resetenv(self):
        self.view.scene.clear()
        self.env.reset()
        self.autoStepping = False
        val = self.render.scalingSpin.spin.minimum()
        self.render.scalingSpin.spin.setValue(val)

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