import numpy as np
from typing import List

from Environment_Objects import Intersection, Road, Path, Car, Traffic_signal, Signals

UPDATE_DUR = 0.1
RENDER_DUR = 1
RL_UPDATE_DUR = 2

class Traffic_Simulator_Env():

    def __init__(self):
        ''' Initialize the environment. '''
        self.view = None

        self.isRendering = False

        self.timer = {}

    def reset(self):
        ''' Rebuild the environment and reset all cars.\n
            Returns the initial state. '''
        self.intersections = {}
        self.roads = {}
        self.paths = {}

        self.signals = []
        self.timer = {}

        self.cars = []
        self.buildEnv()
        state = None
        return state

    def buildEnv(self):
        ''' Build the structures of the environment.\n
            Use addTrafficSignal(), addIntersection(), 
            addRoad(), addPath() in this method to 
            create your traffic system. '''

        self.sig1 = self.addTrafficSignal(Signals.RED)
        self.sig2 = self.addTrafficSignal(Signals.RED, self.sig1)

        a = self.addIntersection("a", 0, 0)
        b = self.addIntersection("b", 200, 0)
        c = self.addIntersection("c", 400, 0)
        d = self.addIntersection("d", 200, -200)
        e = self.addIntersection("e", 200, 200)

        ab = self.addRoad(a, b, 60, self.sig1)
        bc = self.addRoad(b, c, 60)
        db = self.addRoad(d, b, 60, self.sig2)
        be = self.addRoad(b, e, 60)

        self.path1 = self.addPath([ab, bc], 1)
        self.path2 = self.addPath([db, be], 1)

        if self.isRendering:
            self.renderScale(1)

    def enableRender(self, view):
        ''' Enable the rendering. \n
            Set the GraphicView Widget from PyQt for rendering. '''
        self.view = view
        self.isRendering = True

    def renderScale(self, scale):
        for key in self.intersections:
            inte = self.intersections[key]
            inte.render(self.view, scale)
        for key in self.roads:
            road = self.roads[key]
            road.render(self.view, scale)
        self.renderUpdate(scale)

    def renderUpdate(self, scale):
        for car in self.cars:
            car.render(self.view, scale)
        self.tsRender(scale)

    def tsRender(self, scale):
        for ts in self.signals:
            ts.render(self.view, scale)

    def update(self):
        ''' Update the environment.'''
        rand1 = np.random.rand()
        rand2 = np.random.rand()
        if rand1 < 0.02:
            self.addCar(self.path1, maxSpd=20)
        if rand2 < 0.01:
            self.addCar(self.path2, maxSpd=20)
        for index, car in enumerate(self.cars):
            car.update()
            if car.done:
                self.cars.pop(index)
        for sig in self.signals:
            sig.update()

        for tmr in self.timer:
            tmr.update() += 0.1 #update dur

    def makeAction(self, action):
        ''' Make an action, change the duration of the traffic signals. '''
        self.action = action

    def getStateAndReward(self):
        ''' returns the current state, reward, terminal and info.  '''
        state_ = None
        reward = None
        term = None
        info = None
        return state_, reward, term, info 
        

    def addIntersection(self, name : str, x : int, y : int, diam =20):
        add = Intersection(name, x, -y, diam)
        self.intersections[add.name] = add
        return add

    def addRoad(self, start : Intersection, end : Intersection, spdLim : float, traffic_signal=None):
        name = start.name+"-"+end.name
        lim = spdLim/3600*1000
        add = Road(name, start, end, lim, traffic_signal=traffic_signal)
        self.roads[add.name] = add
        return add

    def addPath(self, roads : List[Road], current : float):
        name = roads[0].name
        for i in range(len(roads) - 1):
            name += "," + roads[i+1].name
        add = Path(name, roads, current)
        return add

    def addTrafficSignal(self, def_signal, master=None):
        add = Traffic_signal(def_signal, update_dur=UPDATE_DUR, master=master)
        self.signals.append(add)
        return add

    def addCar(self, path : Path, maxSpd=20.0):
        add = Car(path, update_dur=UPDATE_DUR, maxSpd=maxSpd, view=self.view)
        self.cars.append(add)
        return add

    def get_cardensity(self, carnum : Car, roadarea : 100):
        return carnum/roadarea
        
    def get_speed(self, carnum : Car):
        self.speed = 0
        for carnum in Car:
            speed += Car.maxSpd
        return speed/Car
        
    def get_trafficflow(self):
        #need to add a line before getting into newroad


    

