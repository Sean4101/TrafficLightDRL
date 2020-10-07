import numpy as np
from typing import List

from Environment_Objects import Intersection, Road, Path, Car

class Traffic_Simulator_Env():

    def __init__(self):
        ''' Initialize the environment. '''
        self.view = None

        self.isRendering = False

    def buildEnv(self):
        ''' Build the structures of the environment.\n
            Use addIntersection(), addRoad(), addPath() in this method
            to create your traffic system. '''
        a = self.addIntersection("a", 0, 0)
        b = self.addIntersection("b", 200, 0)
        c = self.addIntersection("c", 400, 0)

        ab = self.addRoad(a, b, 200, 60)
        bc = self.addRoad(b, c, 200, 60)

        self.path1 = self.addPath([ab, bc], 1)
        
        car1 = self.addCar(self.path1)

        if self.isRendering:
            self.render(1)


    def reset(self):
        ''' Rebuild the environment and reset all cars.\n
            Returns the initial state. '''
        self.intersections = {}
        self.roads = {}
        self.paths = {}
        self.cars = []
        self.buildEnv()
        state = None
        return state

    def enableRender(self, view):
        ''' Enable the rendering. \n
            Set the GraphicView Widget from PyQt for rendering. '''
        self.view = view
        self.isRendering = True

    def render(self, scale):
        for key in self.intersections:
            inte = self.intersections[key]
            inte.render(self.view, scale)
        for key in self.roads:
            road = self.roads[key]
            road.render(self.view, scale)
        for car in self.cars:
            car.render(self.view, scale)

    def step(self, action):
        ''' Make an action and update the environment.\n
            returns the next state, reward, terminal and info. '''
        self.addCar(self.path1, maxSpd=3)
        for index, car in enumerate(self.cars):
            car.step()
            if car.done:
                self.cars.pop(index)
        state_ = None
        reward = None
        term = None
        info = None
        return state_, reward, term, info 
        

    def addIntersection(self, name : str, x : int, y : int):
        add = Intersection(name, x, y)
        self.intersections[add.name] = add
        return add

    def addRoad(self, start : Intersection, end : Intersection, len : float, spdLim : float):
        name = start.name+"-"+end.name
        lim = spdLim/3600*1000
        add = Road(name, start, end, len, lim)
        self.roads[add.name] = add
        return add

    def addPath(self, roads : List[Road], current : float):
        name = roads[0].name
        for i in range(len(roads) - 1):
            name += "," + roads[i+1].name
        add = Path(name, roads, current)
        return add

    def addCar(self, path : Path, maxSpd=20.0):
        add = Car(path, maxSpd=maxSpd, view=self.view)
        self.cars.append(add)
        return add