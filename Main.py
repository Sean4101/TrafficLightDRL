import sys
import os
import time
import numpy as np

from Environment import TrafficDRL_Env
from Render_Widget import mainWidget
from stable_baselines3 import SAC, PPO
from stable_baselines3.sac import MlpPolicy as MlpPolicySAC
from stable_baselines3.ppo import MlpPolicy as MlpPolicyPPO
from PyQt5.QtWidgets import QApplication

class TrafficDRL():
    def __init__(self):
        self.widget = mainWidget()

        self.env = TrafficDRL_Env(
            render_scene=self.widget.viewTab.scene
        )

        self.n_steps = 1800

        self.model = PPO(
            MlpPolicyPPO,
            self.env,
            verbose=1,
            n_steps=self.n_steps,
            learning_rate=1e-3,
            gamma=1-1e-5,
            ent_coef=1e-2,
            tensorboard_log="./DRL_tensorboard/"
        )
        
        self.episode_cnt = 0
        self.score_history = []
        self.avg_wait_time_history = []
        self.value_loss_history = []
        self.critic_loss_history = []
        self.actor_loss_history = []

    def train(self, episode_cnt=10):
        self.model.learn(self.n_steps*episode_cnt, log_interval=1)

    def test(self, flow=None):
        self.env.render()
        obs = self.env.reset(flow, isTest=True)
        self.test_done = False
        while not self.test_done:
            action, _states = self.model.predict(obs, deterministic=True)
            obs, reward, self.test_done, info = self.env.step(action)
        self.env.render(close=True)

test_flow_sets = [[10, 10, 10, 10],
                  [15, 15, 5, 5],
                  [15, 5, 15, 5],
                  [5, 5, 15, 15],
                  [15, 5, 5, 15],
                  [20, 20, 5, 5],
                  [20, 20, 20, 20]]

if __name__ == '__main__':
    app = QApplication(sys.argv)
    drl_app = TrafficDRL()
    drl_app.widget.show()

    # For Traning
    '''
    drl_app.model.save('C:/Users/seanc/Anaconda3/envs/MachineLearning/DRL_Project/TrafficSignalDRL/saved_models/m0')
    for i in range(10):
        drl_app.train(10)
        drl_app.model.save('C:/Users/seanc/Anaconda3/envs/MachineLearning/DRL_Project/TrafficSignalDRL/saved_models/m' + str(i+1))
    '''

    # For Testing
    '''
    drl_app.model.set_env(drl_app.env)
    for j, flow_set in enumerate(test_flow_sets):
        print("testing flow set "+str(j))
        for i in range(10+1):
            drl_app.model = PPO.load('C:/Users/seanc/Anaconda3/envs/MachineLearning/DRL_Project/TrafficSignalDRL/saved_models/m' + str(i))
            drl_app.test(flow_set)
    '''
    os._exit(app.exec_())