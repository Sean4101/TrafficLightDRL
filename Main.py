import sys
import os
import time
import numpy as np
import openpyxl

from Environment import TrafficDRL_Env
from Render_Widget import mainWidget
from stable_baselines3 import SAC, PPO
from stable_baselines3.ppo import MlpPolicy
from stable_baselines3.common.callbacks import CheckpointCallback
from PyQt5.QtWidgets import QApplication
from Environment import all_test_data, each_test_data

class TrafficDRL():
    def __init__(self):
        self.widget = mainWidget()

        self.n_steps = 1200
        self.n_episode_per_callback = 20
        self.save_path = './a_logs/'

        self.env = TrafficDRL_Env(
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
            #print(action)
        self.env.render(close=True)
        

test_flow_sets = [[10, 10],
                  [5, 15],
                  [15, 5],
                  [20, 20]]



if __name__ == '__main__':
    app = QApplication(sys.argv)
    drl_app = TrafficDRL()
    drl_app.widget.show()
    
    
    # For Training
    '''
    drl_app.model.save(drl_app.save_path+'/a__0_steps')
    drl_app.model.learn(200*drl_app.n_steps, drl_app.checkpoint_callback)
    '''

    # For Testing
    
    model_num = 11
    test_time = 5
    avg_list = ["fs1", 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
    lists = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
    all_avg_data = []
    percentage = 0
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.append(["t0","t1","t2","t3","t4","t5","t6","t7","t8","t9","t10"])

    drl_app.model.set_env(drl_app.env)
    for i, flows in enumerate(test_flow_sets):
        for j in range(test_time):
            for k in range(model_num):
                model = '/a__' + str(k*24000) + '_steps.zip'
                drl_app.model = PPO.load(drl_app.save_path + str(model))
                drl_app.test(flow=flows)
                print("------"+str(round(percentage/((model_num*test_time)*len(test_flow_sets)) , 4))+" %------")
                percentage += 1
    number = 2
    for i, data in enumerate(each_test_data):
        j = ((i+11)%11)+1
        lists[j-1] = data
        avg_list[j] += data

        if (i+1)%11 == 0:
            ws.append(lists)

        if (i+1)%(11*test_time) == 0:
            for i in range(1, 12):
                avg_list[i]/=5
            ws.append(avg_list)
            all_avg_data.append(avg_list)
            avg_list = ["fs"+str(number), 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
            ws.append(["-"])
            number += 1

    ws.append([" ","t0","t1","t2","t3","t4","t5","t6","t7","t8","t9","t10"])
    for data in all_avg_data:
        ws.append(data)

    c1 = openpyxl.chart.LineChart()
    data = openpyxl.chart.Reference(ws, min_col=1, min_row=3+len(test_flow_sets)*(test_time+2), max_col=model_num+1, max_row=6+len(test_flow_sets)*(test_time+2)) 
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

    ws.add_chart(c1, "O1")
    wb.save("sample1.xlsx")
    print("finish")
    

    os._exit(app.exec_())