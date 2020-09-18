from typing import List
import numpy as np

class Intersection():
    def __init__(self, name : str, xpos : int, ypos : int):
        self.name = name
        self.x = xpos
        self.y = ypos

class Road():
    def __init__(self, name : str, start : Intersection, end : Intersection, len: float, lim: float):
        self.name = name
        self.start = start
        self.end = end
        self.len = len
        self.lim = lim

        self.cars = []

class Path():
    def __init__(self, name : str, roads : List[Road], current : float):
        self.roads = roads
        self.current = current

class Car():
    def __init__(self, path : Path, maxSpd= 20.0, info=False, render = False, view = None):
        self.path = path
        self.road = path.roads[0]
        self.maxSpd = maxSpd
        self.info = info
        self.render = render
        self.view = view
    
        self.car_rect = None

        self.tot_stages = len(self.path.roads)
        self.stage = 0
        self.progress = 0.0
        self.done = False

        self.xpos = self.road.start.x
        self.ypos = self.road.start.y

        dx = self.road.end.x - self.road.start.x
        dy = -self.road.end.y - self.road.start.y
        vec = complex(dx, dy)
        self.rot = np.angle(vec, deg=True)

        if self.render:
            self.car_rect = self.view.addCar(self.xpos, self.ypos)
            self.car_rect.setRotation(self.rot)
    
    def step(self, render=False):
        self.render = render

        self.road = self.path.roads[self.stage]
        self.progress += self.maxSpd
        if self.progress >= self.road.len:
            self.stage += 1
            if self.stage >= self.tot_stages:
                self.done = True
                self.leave()
                return
            self.road = self.path.roads[self.stage]
            self.progress = 0
        self.xpos = self.road.start.x * (1 - self.progress/self.road.len) + self.road.end.x * self.progress/self.road.len
        self.ypos = self.road.start.y * (1 - self.progress/self.road.len) + self.road.end.y * self.progress/self.road.len
        dx = self.road.end.x - self.road.start.x
        dy = -self.road.end.y + self.road.start.y
        vec = complex(dx, dy)
        self.rot = np.angle(vec, deg=True)
        
        if self.render:
            if self.car_rect == None:
                self.car_rect = self.view.addCar(self.xpos, self.ypos)
            else:
                self.car_rect.setPos(self.xpos, self.ypos)
                self.car_rect.setRotation(self.rot)
        
        if self.info:
            print(str(self.xpos) + ", " + str(self.ypos))
            print(self.rot)
    
    def leave(self):
        if self.render:
            self.view.scene.removeItem(self.car_rect)


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

        car1 = self.addCar(path1, 40)

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