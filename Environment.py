import numpy as np
import gym
import statistics
import time

from PyQt5.QtWidgets import QApplication

from typing import List
from gym import spaces
from Env_Objects import Intersection, Road, Path, Car, Traffic_signal, Signals

STATE_EACH_ROAD = 2
FLOW_MIN = 0
FLOW_MAX = 20

UPDATE_DUR = 0.1
SEC_EACH_STEP = 3

class TrafficDRL_Env(gym.Env):
    def __init__(self, render_scene=None, n_steps=3600/SEC_EACH_STEP):
        super(TrafficDRL_Env, self).__init__()
        
        self.buildEnv()

        self.action_space = spaces.MultiBinary(self.n_action)

        self.observation_space = spaces.Box(
            low=0, 
            high=255,
            shape=(self.n_state,),
            dtype=np.float32)

        self.render_scene = render_scene
        self.n_steps = n_steps
        self.isRendering = False
        self.scale = 1

    def reset(self, fixed_flow=None, isTest=False):
        self.isTest = isTest
        self.timer = 0
        self.episode_len = self.n_steps * SEC_EACH_STEP
        self.buildEnv()

        self.cars = []
        self.prev_avg_wait = 0
        self.avg_waiting_time = 0
        self.tot_car_cnt = 0
        self.tot_progress = 1
        self.prev_tot_progress = 1

        self.n_exit_cars = 0
        self.signal_penalty = 0

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
        self.signal_penalty = 0
        self.makeAction(action)
        for i in range(10*SEC_EACH_STEP):
            self.update() # update every object and sum up penalty
            if self.isRendering:
                self.update_render()
        finished = self.timer>=self.episode_len
        state_ = self.calculateState()
        reward = self.calculateReward()
        done = finished
        info = {}
        if done:
            print(self.avg_waiting_time)
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

        s1m = self.addTrafficSignal(Signals.RED, True)
        s1s = self.addTrafficSignal(Signals.RED, master=s1m)

        A = self.addIntersection(200, 0)
        B = self.addIntersection(0, -200)
        C = self.addIntersection(200, -200)
        D = self.addIntersection(400, -200)
        E = self.addIntersection(200, -400)

        AC = self.addRoad(A, C, s1m)
        CE = self.addRoad(C, E)
        BC = self.addRoad(B, C, s1s)
        CD = self.addRoad(C, D)

        p1 = self.addPath([AC, CE])
        p2 = self.addPath([BC, CD])

        self.n_action = len(self.master_signals)
        self.n_state = len(self.roads)* STATE_EACH_ROAD + len(self.signals)

    def update(self):
        ''' Update the environment.'''
        self.timer = (self.timer * 10 + UPDATE_DUR * 10)/10
        for path in self.paths:
            rand = np.random.rand()
            prob = path.flow/10/60
            if rand < prob:
                if path.roads[0].isAvailable():
                    self.addCar(path)
                else:
                    self.n_exit_cars += 1
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
            self.signal_penalty += master.penalty

    def calculateState(self):
        state = np.zeros((self.n_state), dtype=float)
        for i, road in enumerate(self.roads):
            state[i*STATE_EACH_ROAD+ 0] = road.get_queue()
            state[i*STATE_EACH_ROAD+ 1] = len(road.cars)
        for j, signal in enumerate(self.signals):
            state[len(self.roads)*STATE_EACH_ROAD + j] = signal.light_timer if signal.signal == Signals.RED else 0
        return state

    def calculateReward(self):
        cur_avg_wait = self.get_cur_avg_wait()
        delta_wait = self.prev_avg_wait - cur_avg_wait
        self.prev_avg_wait = cur_avg_wait


        return delta_wait - self.signal_penalty

    def get_cur_avg_wait(self):
        l = len(self.cars)
        if l == 0:
            return 0
        sum = 0
        for car in self.cars:
            sum += (self.timer - car.start_time)
        return sum/l

    def addIntersection(self, x : int, y : int, diam =20):
        add = Intersection(x, -y, diam)
        self.intersections.append(add)
        return add

    def addRoad(self, start : Intersection, end : Intersection, traffic_signal=None, spdLim : float = 60):
        lim = spdLim/3600*1000
        add = Road(self, start, end, lim, traffic_signal=traffic_signal)
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

    def addCar(self, path : Path, maxSpd=20.0):
        add = Car(self, path, update_dur=UPDATE_DUR, maxSpd=maxSpd, scene=self.render_scene)
        self.cars.append(add)
        return add

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