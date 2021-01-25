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

        self.model = PPO(
            MlpPolicyPPO,
            self.env,
            verbose=1,
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
        self.model.learn(self.env.step_per_epi*episode_cnt, log_interval=1)

    def test(self):
        self.env.render()
        obs = self.env.reset()
        self.test_done = False
        while not self.test_done:
            action, _states = self.model.predict(obs, deterministic=True)
            obs, reward, self.test_done, info = self.env.step(action)
            #print(obs)
        self.env.render(close=True)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    drl_app = TrafficDRL()
    drl_app.widget.show()
    for i in range(100):
        drl_app.test()
        drl_app.train(episode_cnt=5)
        drl_app.test()
    os._exit(app.exec_())