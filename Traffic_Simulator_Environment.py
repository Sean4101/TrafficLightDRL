import numpy as np
from typing import List

from Environment_Objects import Intersection, Road, Path, Car

class Traffic_Simulator_Env():

    def __init__(self):
        ''' Initialize the environment. '''
        self.view = None

        self.isRendering = False

    def setView(self, viewTab):
        ''' Set the GraphicView Widget from PyQt for rendering. '''
        self.view = viewTab

    def buildEnv(self):
        ''' Build the structures of the environment.\n
            Use addIntersection(), addRoad(), addPath() in this method
            to create your traffic system. '''
        a = self.addIntersection("a", 0, 0)
        b = self.addIntersection("b", 100, 0)
        c = self.addIntersection("c", 100, 100)
        d = self.addIntersection("d", 200, 100)

        ab = self.addRoad(a, b, 400, 60)
        bc = self.addRoad(b, c, 400, 60)
        cd = self.addRoad(c, d, 400, 60)

        path1 = self.addPath([ab, bc, cd], 60)

        if self.isRendering:
            for key in self.intersections:
                inte = self.intersections[key]
                self.view.addInte(inte.x, inte.y)
            for key in self.roads:
                road = self.roads[key]
                self.view.addRoad(road.start.x, road.start.y, road.end.x, road.end.y)

        car1 = self.addCar(path1, 60)

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

    def render(self):
        ''' Enable the rendering. '''
        self.isRendering = True

    def step(self, action):
        ''' Make an action and update the environment.\n
            returns the next state, reward, terminal and info. '''
        for index, car in enumerate(self.cars):
            car.step(render=self.isRendering)
            if car.done:
                #self.view.scene.removeItem(car.car_rect)
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
        add = Car(path, maxSpd=maxSpd, view=self.view, render=True)
        self.cars.append(add)
        return add