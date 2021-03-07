from Environment import TrafficDRL_Env
import numpy as np
import openpyxl
import sys
import os
import time

from PyQt5.QtWidgets import QApplication
from Render_Widget import mainWidget

class fixed_time_system_model():
    def __init__(self):
        '''self.n_steps = 1200
        self.n_train_episodes = 500 # change to 3000 if es=2
        self.n_episode_per_callback = 50 # change to 150 if es=2
        self.save_path = './models3/rf5,es2/ent_coef=0.0/gamma=0.9999/'''

        rf = 5 # Option of 0 ~ 7, each represents different reward function.
               # (0): The negative of the average time of cars staying in the environment, 
               # minus the traffic signal penalty.
               # (1): The negative of the total time of cars staying in the environment, 
               # minus the traffic signal penalty.
               # (2): The negative of the average time of waiting in front of traffic signals, 
               # minus the traffic signal penalty.
               # (3): The negative of the total time of waiting in front of traffic signals, 
               # minus the traffic signal penalty.
               # (4~7): Delta time equivalent of (0~3)

        env_sys = 1 # Option of 1 ~ 3, represents different environment scale.
                # (1): 1 crossroads, 1 master signals, 2 paths. each has a length of 400 meters.
                # (2): 4 crossroads, 4 master signals, 4 paths. each has a length of 600 meters.
                # (3): 9 crossroads, 9 master signals, 6 paths. each has a length of 600 meters.

        self.widget = mainWidget()

        self.env = TrafficDRL_Env(
            reward_function=rf,
            env_sys=env_sys,
            render_scene=self.widget.viewTab.scene
        )

        size = len(self.env.master_signals)
        self.array_0 = np.zeros(size)
        self.array_1 = np.ones(size)

        self.signal_state = 0
        self.number = 0

    def predict(self, red_light_time, green_light_time):
        self.red_light_time = red_light_time/3
        self.green_light_time = green_light_time/3

        if self.signal_state == 0 and self.number == self.red_light_time:
            self.signal_state = 1
            self.number = 0

        if self.signal_state == 1 and self.number == self.green_light_time:
            self.signal_state = 0
            self.number = 0
        
        self.number += 1

        if self.signal_state == 1:
            return self.array_1, 1
        else:
            return self.array_0, 0
    
    def test(self, red_light_time, green_light_time, flow, render=False):
        
        if render:
            self.env.render()
        self.env.reset(fixed_flow=flow, isTest=True)
        self.test_done = False
        while not self.test_done:
                action, _states = self.predict(red_light_time, green_light_time)
                #print(action)
                obs, reward, self.test_done, info = self.env.step(action, 0)
        self.env.render(close=True)
    
    def fixed_time_system_model_collect_data(self, flow):
        all_data_list = []
        tmp_list = []
        tmp_stay_sum = 0
        wb4 = openpyxl.Workbook()
        ws4 = wb4.active

        tmp_list.append(" ")
        for i in range(9):
            tmp_list.append((i+4)*3)

        all_data_list.append(tmp_list)

        for i in range(12, 37, 3):
            tmp_list = []
            tmp_list.append(i)
            for j in range(12, 37, 3):
                print(i)
                print(j)
                tmp_stay_sum = 0
                for k in range(10):
                    fts_app.test(i, j, [15, 5], render=False)
                    tmp_stay_sum += fts_app.env.avg_staying_time
                print(tmp_stay_sum)
                tmp_list.append(tmp_stay_sum/10)
            all_data_list.append(tmp_list)
            

        for data in all_data_list:
            ws4.append(data)
        wb4.save(" fixed_time_system_model_collect_data [15, 5] sys 1.xlsx")

    def collect_action_and_avg_staytime(self, render=False):
        wb5 = openpyxl.Workbook()
        ws5 = wb5.active

        number_list = []
        action_list = []

        for i in range(len(self.env.master_signals)):
            action_list.append([])
        last_avg_stay_list = []
        number = 0

        for i in range(400):
            number_list.append(i+1)

        delay = 0.0
        i = 0
        if render:
            self.env.render()
        obs = self.env.reset(fixed_flow=[10, 10], isTest=True)
        self.test_done = False
        for i in range(400):
            if i == 200:
                self.env.change_flow([20, 0])
            action, _states = self.predict(12, 12)
            obs, reward, self.test_done, info = self.env.step(action, delay)
            print(action)
            for j in range(len(self.env.master_signals)):
                action_list[j].append(action.tolist()[j])
            last_avg_stay_list.append(self.env.get_cur_avg_stay())
            
            i+=1
        print(i)
        self.env.render(close=True)

                
        ws5.append(number_list)
        for data in action_list:
            ws5.append(data)
        ws5.append(last_avg_stay_list)
        wb5.save( "action_and_avg_staytime [10, 10]  [20, 0] sys 1 fixed_time.xlsx")


if __name__ == '__main__':
    app = QApplication(sys.argv)
    fts_app = fixed_time_system_model()
    fts_app.widget.show()
    
    i = 36
    print(i)
    sum_ = 0
    for k in range(12, 37, 3):
        fts_app.test(i,k, [15, 5], render=False)
    
    #fts_app.collect_action_and_avg_staytime()

    #fts_app.fixed_time_system_model_collect_data(flow=[15, 5, 15, 5])

    print("finish")
    
    os._exit(app.exec_())

        