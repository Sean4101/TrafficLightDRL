import numpy as np
import math
from typing import List

CAR_WIDTH = 2
CAR_HEIGHT = 3

INTERSECTION_DIAM = 15
ROAD_WIDTH = 12

class Intersection():
    def __init__(self, name : str, xpos : int, ypos : int):
        self.name = name
        self.x = xpos
        self.y = ypos

        self.graphicObj = None

    def render(self, view):
        self.view = view
        if self.graphicObj == None:
            self.graphicObj = view.scene.addEllipse(self.x-INTERSECTION_DIAM/2, self.y-INTERSECTION_DIAM/2, 
                                                    INTERSECTION_DIAM, INTERSECTION_DIAM, view.grayPen, view.grayBrush)

class Road():
    def __init__(self, name : str, start : Intersection, end : Intersection, len: float, lim: float):
        self.name = name
        self.start = start
        self.end = end
        self.len = len
        self.lim = lim

        self.cars = []
        
        self.graphicObj = None

    def render(self, view):
        self.view = view

        x1 = self.start.x
        y1 = self.start.y
        x2 = self.end.x
        y2 = self.end.y

        length = math.sqrt((x2 - x1)**2 + (y2 - y1)**2) + ROAD_WIDTH
        dx = x2 - x1
        dy = y2 - y1
        vec = complex(dx, dy)
        rot = np.angle(vec)
        rotd = np.angle(vec, deg=True)

        x = x1 - math.sin(rot+math.pi*3/4)*ROAD_WIDTH*math.sqrt(2)/2
        y = y1 + math.cos(rot+math.pi*3/4)*ROAD_WIDTH*math.sqrt(2)/2

        if self.graphicObj == None:
            self.graphicObj = view.scene.addRect(0, 0, length, ROAD_WIDTH, view.grayPen, view.grayBrush)
        self.graphicObj.setRotation(rotd)
        self.graphicObj.setPos(x, y)

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
        
    def render(self, view):
        self.view = view
    
    def leave(self):
        if self.render:
            self.view.scene.removeItem(self.car_rect)