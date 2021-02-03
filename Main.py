import sys
import os
import time
import numpy as np

from Environment import TrafficDRL_Env
from Render_Widget import mainWidget
from stable_baselines3 import SAC, PPO
from stable_baselines3.sac import MlpPolicy as MlpPolicySAC
from stable_baselines3.ppo import MlpPolicy as MlpPolicyPPO
from stable_baselines3.common.callbacks import CheckpointCallback
from PyQt5.QtWidgets import QApplication

class TrafficDRL():
    def __init__(self):
        self.widget = mainWidget()

        self.n_steps = 3600
        self.n_episode_per_callback = 200
        self.save_path = './a_logs/'

        self.env = TrafficDRL_Env(
            render_scene=self.widget.viewTab.scene,
            n_steps=self.n_steps
        )

        self.checkpoint_callback = CheckpointCallback(save_freq=self.n_steps*self.n_episode_per_callback, save_path=self.save_path,
                                         name_prefix='a_')

        self.model = PPO(
            MlpPolicyPPO,
            self.env,
            verbose=1,
            n_steps=self.n_steps,
            learning_rate=3e-3,
            gamma=1-1e-5,
            tensorboard_log="./DRL_tensorboard/"
        )
        
        self.episode_cnt = 0
        self.score_history = []
        self.avg_wait_time_history = []
        self.value_loss_history = []
        self.critic_loss_history = []
        self.actor_loss_history = []

    def test(self, flow=None):
        self.env.render()
        obs = self.env.reset(flow, isTest=True)
        self.test_done = False
        while not self.test_done:
            action, _states = self.model.predict(obs, deterministic=True)
            obs, reward, self.test_done, info = self.env.step(action)
            print(action)
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

    # For
    
    #drl_app.model = PPO.load('C:/Users/seanc/Anaconda3/envs/MachineLearning/DRL_Project/TrafficSignalDRL/saved_models/a20')
    #drl_app.model.set_env(drl_app.env)
    '''
    drl_app.model.save(drl_app.save_path+'/a__0_steps')
    drl_app.model.learn(5000*drl_app.n_steps, drl_app.checkpoint_callback)
    '''

    # For Testing
    
    drl_app.model.set_env(drl_app.env)
    model = '/a__12240000_steps.zip'
    drl_app.model = PPO.load(drl_app.save_path + str(model))
    drl_app.test(flow=test_flow_sets[5])
    
    os._exit(app.exec_())