import sys
import os
import time
import numpy as np

from Environment import TrafficDRL_Env
from Render_Widget import mainWidget
from stable_baselines3 import PPO
from stable_baselines3.ppo import MlpPolicy
from stable_baselines3.common.callbacks import CheckpointCallback
from PyQt5.QtWidgets import QApplication

class TrafficDRL():
    def __init__(self):
        self.widget = mainWidget()

        self.n_steps = 1200
        self.n_train_episodes = 500
        self.n_episode_per_callback = 50
        self.save_path = './a_logs/'
        rf = 0 # Option of 0 ~ 3, each represents different reward function.
               # (0): The negative of the average time of cars staying in the environment, 
               # minus the traffic signal penalty.
               # (1): The negative of the total time of cars staying in the environment, 
               # minus the traffic signal penalty.
               # (2): The negative of the average time of waiting in front of traffic signals, 
               # minus the traffic signal penalty.
               # (3): The negative of the total time of waiting in front of traffic signals, 
               # minus the traffic signal penalty.

        env_sys = 3 # Option of 1 ~ 3, represents different environment scale.
                # (1): 1 crossroads, 1 master signals, 2 paths. each has a length of 400 meters.
                # (2): 4 crossroads, 4 master signals, 4 paths. each has a length of 600 meters.
                # (3): 9 crossroads, 9 master signals, 6 paths. each has a length of 600 meters.

        self.env = TrafficDRL_Env(
            reward_function=rf,
            env_sys=env_sys,
            render_scene=self.widget.viewTab.scene,
            n_steps=self.n_steps
        )

        self.checkpoint_callback = CheckpointCallback(save_freq=self.n_steps*self.n_episode_per_callback, save_path=self.save_path,
                                         name_prefix='a_')

        self.model = PPO(
            MlpPolicy,
            self.env,
            verbose=1,
            n_steps=self.n_steps,
            learning_rate=3e-4,
            ent_coef=0.5,
            gamma=0.95,
            tensorboard_log="./tensorboard/"
        )

    def test(self, flow=None):
        self.env.render()
        obs = self.env.reset(flow, isTest=True)
        self.test_done = False
        while not self.test_done:
            action, _states = self.model.predict(obs, deterministic=True)
            obs, reward, self.test_done, info = self.env.step(action)
            print(reward)
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

    # For Training
    '''
    drl_app.model.save(drl_app.save_path+'/a__0_steps')
    drl_app.model.learn(self.n_train_episodes*drl_app.n_steps, drl_app.checkpoint_callback)
    '''

    # For Testing
    
    drl_app.model.set_env(drl_app.env)
    #model = '/a__0_steps.zip'
    #drl_app.model = PPO.load(drl_app.save_path + str(model))
    drl_app.test(flow=[5, 0, 0, 0, 10, 10])
    
    
    os._exit(app.exec_())