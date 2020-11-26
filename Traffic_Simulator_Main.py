import sys
import os
import time
import numpy as np

from PyQt5.QtWidgets import QApplication

from Traffic_Simulator_Environment import Traffic_Simulator_Env
from Traffic_Simulator_Widget import mainWidget
from SAC_Agent import Agent

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
        self.max_step = 3600
        self.assignEvents()
        self.scale()

    def initialize(self):
        ''' Initialize the application. '''
        #self.agent.save_models()
        self.agent.load_models()
        self.env.toggleRender(self.renderGroup.renderCheckBox.isChecked(), self.view)
        self.env.scale = self.renderGroup.scalingSpin.spin.value()
        self.episode_cnt = 0
        self.score_history = []
        self.value_loss_history = []
        self.critic_loss_history = []
        self.actor_loss_history = []
        self.reset()
        
    def assignEvents(self):
        ''' Assign every buttons in widget to a method '''
        self.trainGroup.stepButton.clicked.connect(self.envStep)
        self.trainGroup.autoStepButton.clicked.connect(self.autoStep)
        self.trainGroup.resetButton.clicked.connect(self.reset)
         
        self.renderGroup.renderCheckBox.clicked.connect(self.renderCheck)
        self.renderGroup.scalingSpin.spin.valueChanged.connect(self.scale)
        
    def reset(self):
        self.episode_cnt += 1
        self.env.clearCarItems()
        self.envState = self.env.reset()
        self.env.render()

        self.autoStepping = False
        val = self.renderGroup.scalingSpin.spin.minimum()
        self.renderGroup.scalingSpin.spin.setValue(val)

        self.step_cnt = 0
        self.score = 0
        self.value_loss = 0
        self.critic_loss = 0
        self.actor_loss = 0
        self.value_loss_cnt = 0
        self.critic_loss_cnt = 0
        self.actor_loss_cnt = 0

        self.update_episode_cnt()
        self.update_step_cnt()
        self.update_timer()


    def envStep(self):

        self.step_cnt += 1
        self.update_step_cnt()
        action = self.agent.choose_action(self.envState)
        self.env.makeAction(action)
        for i in range(10):
            self.env.update()
            self.env.render(onlyNonStatic=True)
            QApplication.processEvents()
            if self.trainGroup.delayCheckBox.isChecked():
                time.sleep(0.01)
            self.update_timer()
        state_, reward, terminal, _ = self.env.getStateAndReward()
        self.score += reward
        
        self.agent.remember(self.envState, action, reward, state_, terminal)
        vloss, closs, aloss = self.agent.learn()
        self.envState = state_

        self.value_loss = (self.value_loss * self.value_loss_cnt + vloss)/(self.value_loss_cnt + 1)
        self.critic_loss = (self.critic_loss * self.critic_loss_cnt + closs)/(self.critic_loss_cnt + 1)
        self.actor_loss = (self.actor_loss * self.actor_loss_cnt + aloss)/(self.actor_loss_cnt + 1)
        self.value_loss_cnt += 1
        self.critic_loss_cnt += 1
        self.actor_loss_cnt += 1


        if self.step_cnt >= self.max_step:
            self.episode_end()

    def episode_end(self):
        
        self.score_history.append(self.score)
        self.value_loss_history.append(self.value_loss)
        self.critic_loss_history.append(self.critic_loss)
        self.actor_loss_history.append(self.actor_loss)
        episode_avg_waiting_time = self.env.avg_waiting_time

        self.agent.save_models()
        
        print('episode ', self.episode_cnt, 'avg waiting time %.2f' % self.env.avg_waiting_time)

        cnt_list = list(range(1, self.episode_cnt+1))
        self.view.plot.ax.cla()
        self.view.plot.ax.plot(cnt_list, self.value_loss_history, 'r')

        self.view.plot.canvas.draw()
        
        self.reset()
        self.autoStep()

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

    def update_timer(self):
        secs = int(self.env.timer)
        mins = int(secs / 60)
        secs %= 60
        hours = str(int(mins / 60))
        mins %= 60
        if secs < 10:
            secs = "0"+str(secs)
        else:
            secs = str(secs)
        if mins < 10:
            mins = "0"+str(mins)
        else:
            mins = str(mins)
        timer = "Timer: "+hours+":"+mins+":"+secs
        self.widget.trainGroup.timer_label.setText(timer)

    def update_step_cnt(self):
        self.widget.trainGroup.step_label.setText("steps: "+str(self.step_cnt))

    def update_episode_cnt(self):
        self.widget.trainGroup.episode_label.setText("episodes: "+str(self.episode_cnt))

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