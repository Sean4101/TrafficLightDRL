import numpy as np
import gym

from Environment import TrafficDRL_Env
from stable_baselines3 import SAC, PPO, DDPG, DQN
from stable_baselines3.sac import MlpPolicy

env = TrafficDRL_Env()

model = SAC(MlpPolicy, env, verbose=1, gamma=1-1e-5, train_freq=10, learning_rate=3e-5)
model.learn(total_timesteps=360000, log_interval=1)
model.save("saves\Traffic")

del model # remove to demonstrate saving and loading

model = SAC.load("saves\Traffic")

obs = env.reset()

env.render()
while True:
    action, _states = model.predict(obs, deterministic=True)
    obs, reward, done, info = env.step(action)
    if done:
      obs = env.reset()
