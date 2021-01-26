import numpy as np
import gym
import statistics

from PyQt5.QtWidgets import QApplication

from typing import List
from gym import spaces
from Env_Objects import Intersection, Road, Path, Car, Traffic_signal, Signals
from Env_Objects import CAR_HEIGHT

from openpyxl import Workbook

STATE_EACH_ROAD = 6
FLOW_MIN = 0
FLOW_MAX = 20
CAR_ENTER_PENALTY = 1000

UPDATE_DUR = 0.1

class TrafficDRL_Env(gym.Env):
    def __init__(self, render_scene=None):
        super(TrafficDRL_Env, self).__init__()
        
        self.episode_cnt = 0
        self.buildEnv()
    
        self.action_space = spaces.MultiBinary(self.n_action)
        self.observation_space = spaces.Box(
            low=0, 
            high=255,
            shape=(self.n_state,),
            dtype=np.float32)
        
        self.step_per_epi = 2048

        self.render_scene = render_scene
        self.isRendering = False
        self.scale = 1

        self.wb = Workbook()
        self.ws = self.wb.active
        self.ws.append(["Episode Count", "Average Wait", "Fail Enter"])

    def reset(self, fixed_flow=None, episode_len=2048, test=False):
        self.isTest = test
        if self.isTest == False:
            self.episode_cnt += 1
        self.timer = 0
        self.episode_len = episode_len
        self.buildEnv()

        self.cars = []
        self.avg_waiting_time = 0
        self.tot_car_cnt = 0

        self.initialize_episode_log()

        if fixed_flow == None:
            flows = np.random.randint(FLOW_MIN, high=FLOW_MAX, size=(len(self.paths)))
        else:
            flows = fixed_flow

        for i, path in enumerate(self.paths):
            path.flow = flows[i]

        for signal in self.signals:
            signal.initialize()

        first_state = self.calculateState()
        return first_state

    def step(self, action):
        self.makeAction(action)
        self.n_exit_cars = 0
        self.n_fail_enter = 0
        for i in range(10):
            self.update() # update every object and sum up penalty
            if self.isRendering:
                self.update_render()
        
        finished = self.timer>=self.episode_len
        state_ = self.calculateState()
        reward = self.calculateReward()
        done = finished
        info = {}

        self.ep_log_tot_fail_enter += self.n_fail_enter

        if finished:
            self.append_episode_log()

        return state_, reward, done, info

    def render(self, mode='human', close=False):
        self.isRendering = not close
        if close:
            self.clearCarItems()

    def buildEnv(self):
        ''' Build the structures of the environment.\n
            Use addTrafficSignal(), addIntersection(), 
            addRoad(), addPath() in this method to 
            create your traffic system. '''

        self.intersections = []
        self.roads = []
        self.paths = []
        self.signals = []
        self.cars = []
        self.master_signals = []

        sig1 = self.addTrafficSignal(Signals.RED, True)
        sig2 = self.addTrafficSignal(Signals.RED, master=sig1)

        o = self.addIntersection(0, 0)
        a = self.addIntersection(0, 200)
        b = self.addIntersection(0, -200)
        c = self.addIntersection(200, 0)
        d = self.addIntersection(-200, 0)

        ao = self.addRoad(1, False, a, o, sig1)
        ob = self.addRoad(1, False, o, b)
        co = self.addRoad(1, False, c, o, sig2)
        od = self.addRoad(1, False, o, d)

        p1 = self.addPath([ao, ob])
        p1 = self.addPath([co, od])

        self.n_action = len(self.master_signals)
        self.n_state = len(self.roads)* STATE_EACH_ROAD + len(self.signals)

    def update(self):
        ''' Update the environment.'''
        self.timer = (self.timer * 10 + UPDATE_DUR * 10)/10
        for path in self.paths:
            rand = np.random.rand()
            prob = path.flow/10/60
            if rand < prob:
                self.addCar(path.roads[0].bestLaneNum(), path, CAR_HEIGHT)

        for road in self.roads:
            road.update()
        for index, car in enumerate(self.cars):
            car.update()
            if car.done:
                self.avg_waiting_time = (self.avg_waiting_time*self.tot_car_cnt + car.end_time)/(self.tot_car_cnt+1)
                self.tot_car_cnt += 1
                self.cars.pop(index)
                self.n_exit_cars += 1
        for sig in self.signals:
            sig.update()

    def get_car_speed_std(self):
        spd_list = []
        for i, car in enumerate(self.cars):
            spd_list.append(car.speed)
        if len(spd_list) > 1:
            return statistics.stdev(spd_list)
        elif len(spd_list) == 1:
            return spd_list[0]
        else:
            return 0

    def makeAction(self, raw_action):
        ''' Make an action, change the traffic signals. '''

        for idx, master in enumerate(self.master_signals):
            action = Signals.RED if raw_action[idx] == 0 else Signals.GREEN
            master.change_signal(action)

    def calculateState(self):
        state = np.zeros((self.n_state), dtype=float)
        for i, road in enumerate(self.roads):
            state[i*6+0] = road.get_car_density(1)
            state[i*6+1] = road.get_mean_speed(1)
            state[i*6+2] = road.get_trafficflow(1)
            state[i*6+3] = road.get_car_density(5)
            state[i*6+4] = road.get_mean_speed(5)
            state[i*6+5] = road.get_trafficflow(5)
        for j, signal in enumerate(self.signals):
            state[len(self.roads)*6 + j] = signal.light_timer if signal.signal == Signals.RED else 0
        return state

    def calculateReward(self):
        reward = -10*self.avg_waiting_time - 5*self.get_car_speed_std() + 10*self.n_exit_cars - 100*self.n_fail_enter 
        return reward

    def addIntersection(self, x : int, y : int, diam =20):
        add = Intersection(x, -y, diam)
        self.intersections.append(add)
        return add

    def addRoad(self, lane : int, op : bool, start : Intersection, end : Intersection, traffic_signal=None, spdLim : float = 60):
        lim = spdLim/3600*1000
        add = Road(self, lane, op, start, end, lim, traffic_signal=traffic_signal)
        add.number = len(self.roads)
        self.roads.append(add)
        return add

    def addPath(self, roads : List[Road]):
        add = Path(roads)
        self.paths.append(add)
        return add

    def addTrafficSignal(self, def_signal, is_master=False, master=None):
        add = Traffic_signal(def_signal, master=master)
        if is_master:
            self.master_signals.append(add)
        self.signals.append(add)
        return add

    def addCar(self, lane : int, path : Path, height : int, maxSpd=20.0):
        if lane == -1:
            self.n_fail_enter += 1
            return
        add = Car(self, lane, path, update_dur=UPDATE_DUR, maxSpd=maxSpd, scene=self.render_scene)
        self.cars.append(add)

    def update_render(self):
        for inte in self.intersections:
            inte.render(self.render_scene, self.scale)
        for road in self.roads:
            road.render(self.render_scene, self.scale)
        for car in self.cars:
            car.render(self.render_scene, self.scale)
        for ts in self.signals:
            ts.render(self.render_scene, self.scale)
        QApplication.processEvents()

    def clearCarItems(self):
        for car in self.cars:
            if car.graphicsItem != None:
                self.render_scene.removeItem(car.graphicsItem)
                car.graphicsItem = None
        for road in self.roads:
            road.initialize()

    def initialize_episode_log(self):
        self.ep_log_tot_fail_enter = 0
    
    def append_episode_log(self):
        if self.isTest == False:
            self.ws.append([self.episode_cnt , self.avg_waiting_time, self.ep_log_tot_fail_enter])
        self.wb.save("sample.xlsx")

