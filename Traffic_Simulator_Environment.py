import numpy as np
from typing import List

from Environment_Objects import Intersection, Road, Path, Car, Traffic_signal, Signals, Lane
from Environment_Objects import lane_

UPDATE_DUR = 0.1
RENDER_DUR = 1
RL_UPDATE_DUR = 2

STATE_EACH_ROAD = 6
PENALTY = 1000

lane_ = 3

class Traffic_Simulator_Env():

    def __init__(self):
        ''' Initialize the environment. '''
        self.view = None
        self.scale = 1

        self.intersections = {}
        self.roads = {}
        self.paths = {}
        self.signals = []
        self.cars = []

        self.update_reward = 0
        self.master_signals = []

        self.isRendering = False

        self.buildEnv()

    def reset(self):
        ''' Rebuild the environment and reset all cars.\n
            Returns the initial state. '''
        self.timer = 0

        self.cars = []
        self.penalty = 0
        self.avg_waiting_time = 0
        self.tot_car_cnt = 0
        return self.calculateState()

    def buildEnv(self):
        ''' Build the structures of the environment.\n
            Use addTrafficSignal(), addIntersection(), 
            addRoad(), addPath() in this method to 
            create your traffic system. '''

        sig1 = self.addTrafficSignal(Signals.RED, True)
        sig2 = self.addTrafficSignal(Signals.RED, master=sig1)
        sig3 = self.addTrafficSignal(Signals.RED, True)
        sig4 = self.addTrafficSignal(Signals.RED, master=sig3)
        sig5 = self.addTrafficSignal(Signals.RED, True)
        sig6 = self.addTrafficSignal(Signals.RED, master=sig5)
        sig7 = self.addTrafficSignal(Signals.RED, True)
        sig8 = self.addTrafficSignal(Signals.RED, master=sig7)

        a2 = self.addIntersection("a2", 200, 0)
        a3 = self.addIntersection("a3", 400, 0)
        b1 = self.addIntersection("b1", 0, 200)
        b2 = self.addIntersection("b2", 200, 200)
        b3 = self.addIntersection("b3", 400, 200)
        b4 = self.addIntersection("b4", 600, 200)
        c1 = self.addIntersection("c1", 0, 400)
        c2 = self.addIntersection("c2", 200, 400)
        c3 = self.addIntersection("c3", 400, 400)
        c4 = self.addIntersection("c4", 600, 400)
        d2 = self.addIntersection("d2", 200, 600)
        d3 = self.addIntersection("d3", 400, 600)

        a2b2 = self.addRoad(lane_, False, a2, b2, sig1)
        b2c2 = self.addRoad(lane_, False, b2, c2, sig5)
        c2d2 = self.addRoad(lane_, False, c2, d2)
        a3b3 = self.addRoad(lane_, False, a3, b3, sig3)
        b3c3 = self.addRoad(lane_, False, b3, c3, sig7)
        c3d3 = self.addRoad(lane_, False, c3, d3)
        b1b2 = self.addRoad(lane_, False, b1, b2, sig2)
        b2b3 = self.addRoad(lane_, False, b2, b3, sig4)
        b3b4 = self.addRoad(lane_, False, b3, b4)
        c1c2 = self.addRoad(lane_, False, c1, c2, sig6)
        c2c3 = self.addRoad(lane_, False, c2, c3, sig8)
        c3c4 = self.addRoad(lane_, False, c3, c4)

        b2a2 = self.addRoad(lane_, True, b2, a2)
        c2b2 = self.addRoad(lane_, True, c2, b2, sig1)
        d2c2 = self.addRoad(lane_, True, d2, c2, sig5)
        b3a3 = self.addRoad(lane_, True, b3, a3)
        c3b3 = self.addRoad(lane_, True, c3, b3, sig3)
        d3c3 = self.addRoad(lane_, True, d3, c3, sig7)
        b2b1 = self.addRoad(lane_, True, b2, b1)
        b3b2 = self.addRoad(lane_, True, b3, b2, sig2)
        b4b3 = self.addRoad(lane_, True, b4, b3, sig4)
        c2c1 = self.addRoad(lane_, True, c2, c1)
        c3c2 = self.addRoad(lane_, True, c3, c2, sig6)
        c4c3 = self.addRoad(lane_, True, c4, c3, sig8)

        p1 = self.addPath([a2b2, b2c2, c2d2], 10)
        p2 = self.addPath([a3b3, b3c3, c3d3], 10)
        p3 = self.addPath([b1b2, b2b3, b3b4], 10)
        p4 = self.addPath([c1c2, c2c3, c3c4], 10)

        p5 = self.addPath([d2c2, c2b2, b2a2], 10)
        p6 = self.addPath([d3c3, c3b3, b3a3], 10)
        p7 = self.addPath([b4b3, b3b2, b2b1], 10)
        p8 = self.addPath([c4c3, c3c2, c2c1], 10)
        
        self.n_action = (len(self.master_signals)* 2)
        self.action_high = 120
        self.action_low = 12
        self.n_state = len(self.roads)* STATE_EACH_ROAD + len(self.master_signals)
        self.observation_space_shape = (self.n_state,)

    def toggleRender(self, enable, view):
        ''' Enable the rendering. \n
            Set the GraphicView Widget from PyQt for rendering. '''
        self.isRendering = enable
        self.view = view
        if not self.isRendering:
            for key in self.intersections:
                inte = self.intersections[key]
                if inte.graphicsItem != None:
                    self.view.scene.removeItem(inte.graphicsItem)
                    inte.graphicsItem = None
            for key in self.roads:
                road = self.roads[key]
                if road.graphicsItem != None:
                    self.view.scene.removeItem(road.graphicsItem)
                    road.graphicsItem = None
            for car in self.cars:
                if car.graphicsItem != None:
                    self.view.scene.removeItem(car.graphicsItem)
                    car.graphicsItem = None
            for ts in self.signals:
                if ts.graphicsItem != None:
                    self.view.scene.removeItem(ts.graphicsItem)
                    ts.graphicsItem = None

    def render(self, onlyNonStatic=False):
        if self.isRendering:
            if onlyNonStatic:
                self.renderNonStatic()
            else:
                self.renderStatic()
                self.renderNonStatic()

    def renderStatic(self):
        for key in self.intersections:
            inte = self.intersections[key]
            inte.render(self.view, self.scale)
        for key in self.roads:
            road = self.roads[key]
            road.render(self.view, self.scale)

    def renderNonStatic(self):
        for car in self.cars:
            car.render(self.view, self.scale)
        for ts in self.signals:
            ts.render(self.view, self.scale)

    def update(self):
        ''' Update the environment.'''
        self.timer = (self.timer * 10 + UPDATE_DUR * 10)/10
        for key in self.paths:
            path = self.paths[key]
            rand = np.random.rand()
            prob = path.flow/10/60
            if rand < prob:
                '''if path.roads[0].isAvailable():
                    self.addCar(bestlane)
                else:
                    self.penalty -= PENALTY'''
                if path.roads[0].isAvailable() != 0:
                    self.addCar(1, path.roads[0].isAvailable() , path)
                elif path.roads[0].isAvailable() == 0:
                    self.penalty -= PENALTY
                
        for key in self.roads:
            self.roads[key].update()
        for index, car in enumerate(self.cars):
            car.update()
            if car.done:
                self.avg_waiting_time = (self.avg_waiting_time*self.tot_car_cnt + car.end_time)/(self.tot_car_cnt+1)
                self.tot_car_cnt += 1
                self.cars.pop(index)
        for sig in self.signals:
            sig.update()


    def makeAction(self, raw_action):
        ''' Make an action, change the duration of the traffic signals. '''
        ones = np.ones(shape=raw_action.shape)
        a = (self.action_high-self.action_low)/2 # f(x)=ax+b
        b = (self.action_high+self.action_low)/2 # low < f(x) < high
        self.action = a*raw_action+b*ones


        for idx, master in enumerate(self.master_signals):
            green = self.action[2*idx]
            red = self.action[2*idx+1]
            master.change_duration(green, red)

    def getStateAndReward(self):
        ''' returns the current state, reward, terminal and info.  '''
        state_ = self.calculateState()
        reward = self.calculateReward()
        term = None
        info = None
        return state_, reward, term, info

    def calculateState(self):
        state = np.zeros((self.n_state), dtype=float)
        for key in self.roads:
            road = self.roads[key]
            state[road.number+ 0] = road.get_car_density(1)
            state[road.number+ 1] = road.get_mean_speed(1)
            state[road.number+ 2] = road.get_trafficflow(1)
            state[road.number+ 0] = road.get_car_density(5)
            state[road.number+ 1] = road.get_mean_speed(5)
            state[road.number+ 2] = road.get_trafficflow(5)
        for idx, sig in enumerate(self.master_signals):
            state[len(self.roads)* STATE_EACH_ROAD +idx] = sig.get_next_green_time()
        return state

    def calculateReward(self):
        reward = 0
        for car in self.cars:
            reward -= car.getWaitTime()
        reward /= len(self.cars) if len(self.cars) != 0 else 1
        reward += self.penalty
        return reward

    def clearCarItems(self):
        for car in self.cars:
            if car.graphicsItem != None:
                self.view.scene.removeItem(car.graphicsItem)
                car.graphicsItem = None
        for key in self.roads:
            self.roads[key].initialize()
        

    def addIntersection(self, name : str, x : int, y : int, diam =20):
        add = Intersection(name, x, -y, diam)
        self.intersections[add.name] = add
        return add

    def addRoad(self, lane : int, op : bool, start : Intersection, end : Intersection, traffic_signal=None, spdLim : float = 60):
        name = start.name+"-"+end.name
        lim = spdLim/3600*1000
        add = Road(self, lane_, op, name, start, end, lim, traffic_signal=traffic_signal)
        add.number = len(self.roads)
        self.roads[add.name] = add
        return add

    def addPath(self, roads : List[Road], current : float):
        name = roads[0].name
        for i in range(len(roads) - 1):
            name += "," + roads[i+1].name
        add = Path(name, roads, current)
        self.paths[add.name] = add
        return add

    def addTrafficSignal(self, def_signal, is_master=False, master=None):
        add = Traffic_signal(def_signal, update_dur=UPDATE_DUR, master=master)
        if is_master:
            self.master_signals.append(add)
        self.signals.append(add)
        return add

    def addCar(self, lane : int, next_lane : int, path : Path, maxSpd=20.0):
        add = Car(self, 1, 1, path, update_dur=UPDATE_DUR, maxSpd=maxSpd, view=self.view)
        self.cars.append(add)
        return add

         
        



    

