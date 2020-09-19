import numpy as np
from typing import List

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