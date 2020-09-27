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

        self.graphicsItem = None

    def render(self, view, scale):

        x = self.x * scale
        y = self.y * scale
        diam = INTERSECTION_DIAM * scale

        self.view = view
        if self.graphicsItem == None:
            self.graphicsItem = view.scene.addEllipse(0, 0, 0, 0, view.grayPen, view.grayBrush)
        self.graphicsItem.setRect(x-diam/2, y-diam/2, diam, diam)

class Road():
    def __init__(self, name : str, start : Intersection, end : Intersection, len: float, lim: float):
        self.name = name
        self.start = start
        self.end = end
        self.len = len
        self.lim = lim

        self.cars = []
        
        self.graphicsItem = None

    def render(self, view, scale):
        self.view = view

        x1 = self.start.x * scale
        y1 = self.start.y * scale
        x2 = self.end.x * scale
        y2 = self.end.y * scale

        road_w = ROAD_WIDTH * scale

        length = (math.sqrt((x2 - x1)**2 + (y2 - y1)**2) + road_w)
        dx = x2 - x1
        dy = y2 - y1
        vec = complex(dx, dy)
        rot = np.angle(vec)
        rotd = np.angle(vec, deg=True)

        x = x1 - math.sin(rot+math.pi*3/4)*road_w*math.sqrt(2)/2
        y = y1 + math.cos(rot+math.pi*3/4)*road_w*math.sqrt(2)/2

        if self.graphicsItem == None:
            self.graphicsItem = view.scene.addRect(0, 0, 0, 0, view.grayPen, view.grayBrush)
        self.graphicsItem.setRect(0, 0, length, road_w)
        self.graphicsItem.setPos(x, y)
        self.graphicsItem.setRotation(rotd)

class Path():
    def __init__(self, name : str, roads : List[Road], current : float):
        self.roads = roads
        self.current = current

class Car():
    def __init__(self, path : Path, maxSpd= 20.0, info=False, view = None):
        self.path = path
        self.road = path.roads[0]
        self.maxSpd = maxSpd
        self.info = info
        self.view = view
    
        self.graphicsItem = None

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
    
    def step(self):

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
        
        if self.info:
            print(str(self.xpos) + ", " + str(self.ypos))
            print(self.rot)
        
    def render(self, view, scale):
        self.view = view

        x = self.xpos * scale
        y = self.ypos * scale
        h = CAR_HEIGHT * scale
        w = CAR_WIDTH * scale

        if self.graphicsItem == None:
            self.graphicsItem = self.view.scene.addRect(x-h/2, y-w/2, h, w, view.blackPen, view.redBrush)
        self.graphicsItem.setRect(0, 0, h, w)
        self.graphicsItem.setPos(x, y)
        self.graphicsItem.setRotation(self.rot)
    
    def leave(self):
        if self.render:
            self.view.scene.removeItem(self.graphicsItem)