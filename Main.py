import sys
import os
import time
import numpy as np
import openpyxl

from Environment import TrafficDRL_Env
from Render_Widget import mainWidget
from stable_baselines3 import PPO
from stable_baselines3.ppo import MlpPolicy
from stable_baselines3.common.callbacks import CheckpointCallback
from PyQt5.QtWidgets import QApplication
from Environment import  all_stay_data, all_wait_data


class TrafficDRL():
    def __init__(self):
        self.widget = mainWidget()

        self.n_steps = 1200
        self.n_train_episodes = 3000 # change to 3000 if es=2
        self.n_episode_per_callback = 150 # change to 150 if es=2
        self.save_path = './models2/rf7/es2/models_pen=10/'
        #self.excel_save_path = './models2/rf5/es2/excel/'

        rf = 7 # Option of 0 ~ 7, each represents different reward function.
               # (0): The negative of the average time of cars staying in the environment, 
               # minus the traffic signal penalty.
               # (1): The negative of the total time of cars staying in the environment, 
               # minus the traffic signal penalty.
               # (2): The negative of the average time of waiting in front of traffic signals, 
               # minus the traffic signal penalty.
               # (3): The negative of the total time of waiting in front of traffic signals, 
               # minus the traffic signal penalty.
               # (4~7): Delta time equivalent of (0~3)

        env_sys = 2 # Option of 1 ~ 3, represents different environment scale.
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
            #print(action)
        self.env.render(close=True)

'''test_flow_sets = [[10, 10],
                  [5, 15],
                  [15, 5],
                  [20, 20]]'''

test_flow_sets = [[10, 10, 10, 10],
                  [5, 5, 15, 15],
                  [15, 15, 5, 5],
                  [15, 5, 15, 5],
                  [5, 15, 5, 15],
                  [15, 5, 15, 5],
                  [5, 15, 5, 15],
                  [20, 20, 20, 20]]

if __name__ == '__main__':
    app = QApplication(sys.argv)
    drl_app = TrafficDRL()
    drl_app.widget.show()
    
    # For Training
    '''
    drl_app.model.save(drl_app.save_path+'/a__0_steps')
    drl_app.model.learn(drl_app.n_train_episodes*drl_app.n_steps, drl_app.checkpoint_callback)
    '''

    # For Testing
    '''
    drl_app.model.set_env(drl_app.env)
    model = '/a__60000_steps'
    drl_app.model = PPO.load(drl_app.save_path + str(model))
    drl_app.test(flow=[20, 10, 11, 10])
    '''
    
    #excel for stay
    
    model_num = 21
    test_time = 5
    avg_list = ["fs1", 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
    lists = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
    all_avg_data = []
    percentage = 1
    wb1 = openpyxl.Workbook()
    ws1 = wb1.active
    ws1.append(["t0","t1","t2","t3","t4","t5","t6","t7","t8","t9","t10", "t11", "t12", "t13", "t14", "t15", "t16", "t17", "t18", "t19", "t20"])
    
    for i, flows in enumerate(test_flow_sets):
        for j in range(test_time):
            for k in range(model_num):
                model = '/a__' + str(k*drl_app.n_steps*drl_app.n_episode_per_callback) + '_steps.zip'
                drl_app.model = PPO.load(drl_app.save_path + str(model))
                drl_app.test(flow=flows)
                print("------"+str(round(percentage/((model_num*test_time)*len(test_flow_sets))*100 , 4))+" %------")
                percentage += 1
    number = 2
    for i, data in enumerate(all_stay_data):
        j = ((i+model_num)%model_num)+1
        lists[j-1] = data
        avg_list[j] += data

        if (i+1)%model_num == 0:
            ws1.append(lists)

        if (i+1)%(model_num*test_time) == 0:
            for i in range(1, model_num+1):
                avg_list[i]/=test_time
            ws1.append(avg_list)
            all_avg_data.append(avg_list)
            avg_list = ["fs"+str(number), 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
            ws1.append(["-"])
            number += 1

    ws1.append([" ","t0","t1","t2","t3","t4","t5","t6","t7","t8","t9","t10", "t11", "t12", "t13", "t14", "t15", "t16", "t17", "t18", "t19", "t20"])
    for data in all_avg_data:
        ws1.append(data)

    c1 = openpyxl.chart.LineChart()
    data = openpyxl.chart.Reference(ws1, min_col=1, min_row=3+len(test_flow_sets)*(test_time+2), max_col=model_num+1, max_row=6+len(test_flow_sets)*(test_time+2)) 
    c1.add_data(data, titles_from_data=True)
    s1 = c1.series[0]
    s2 = c1.series[1]
    s3 = c1.series[2]
    s4 = c1.series[3]
    s5 = c1.series[4]
    s6 = c1.series[5]
    s7 = c1.series[6]
    s8 = c1.series[7]
    s9 = c1.series[8]
    s10 = c1.series[9]
    s11 = c1.series[10]
    s12 = c1.series[11]
    s13 = c1.series[12]
    s14 = c1.series[13]
    s15 = c1.series[14]
    s16 = c1.series[15]
    s17 = c1.series[16]
    s18 = c1.series[17]
    s19 = c1.series[18]
    s20 = c1.series[19]
    s21 = c1.series[20]




    ws1.add_chart(c1, "O1")
    wb1.save("stay 7 2.xlsx")
    
    

    #excel for wait
    avg_list = ["fs1",0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
    lists = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
    all_avg_data = []
    percentage = 1
    wb2 = openpyxl.Workbook()
    ws2 = wb2.active
    ws2.append(["t0","t1","t2","t3","t4","t5","t6","t7","t8","t9","t10", "t11", "t12", "t13", "t14", "t15", "t16", "t17", "t18", "t19", "t20"])

    number = 2
    for i, data in enumerate(all_wait_data):
        j = ((i+model_num)%model_num)+1
        lists[j-1] = data
        avg_list[j] += data

        if (i+1)%model_num == 0:
            ws2.append(lists)

        if (i+1)%(model_num*test_time) == 0:
            for i in range(1, model_num+1):
                avg_list[i]/=test_time
            ws2.append(avg_list)
            all_avg_data.append(avg_list)
            avg_list = ["fs"+str(number), 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
            ws2.append(["-"])
            number += 1

    ws2.append([" ","t0","t1","t2","t3","t4","t5","t6","t7","t8","t9","t10", "t11", "t12", "t13","t14", "t15", "t16", "t17",  "t18", "t19", "t20"])
    for data in all_avg_data:
        ws2.append(data)

    c1 = openpyxl.chart.LineChart()
    data = openpyxl.chart.Reference(ws2, min_col=1, min_row=3+len(test_flow_sets)*(test_time+2), max_col=model_num+1, max_row=6+len(test_flow_sets)*(test_time+2)) 
    c1.add_data(data, titles_from_data=True)
    s1 = c1.series[0]
    s2 = c1.series[1]
    s3 = c1.series[2]
    s4 = c1.series[3]
    s5 = c1.series[4]
    s6 = c1.series[5]
    s7 = c1.series[6]
    s8 = c1.series[7]
    s9 = c1.series[8]
    s10 = c1.series[9]
    s11 = c1.series[10]
    s12 = c1.series[11]
    s13 = c1.series[12]
    s14 = c1.series[13]
    s15 = c1.series[14]
    s16 = c1.series[15]
    s17 = c1.series[16]
    s18 = c1.series[17]
    s19 = c1.series[18]
    s20 = c1.series[19]
    s21 = c1.series[20]

    ws2.add_chart(c1, "O1")
    wb2.save(  "wait 7 2.xlsx")
    print("finish")
    
    os._exit(app.exec_())