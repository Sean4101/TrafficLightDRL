import numpy as np
import math
import enum
from typing import List

CAR_WIDTH = 2
CAR_HEIGHT = 3

INTERSECTION_DIAM = 20
ROAD_WIDTH = 12

TRANSIT_TIME = 2
SAFE_DIST = 7

class Intersection():
    def __init__(self, name : str, xpos : float, ypos : float, diam : float):
        self.name = name
        self.x = xpos
        self.y = ypos
        self.diam = diam

        self.cars = []

        self.graphicsItem = None

    def render(self, view, scale):

        x = self.x * scale
        y = self.y * scale
        diam = self.diam * scale

        self.view = view
        if self.graphicsItem == None:
            self.graphicsItem = view.scene.addEllipse(0, 0, 0, 0, view.grayPen, view.grayBrush)
        self.graphicsItem.setRect(x-diam/2, y-diam/2, diam, diam)

class Road():
    def __init__(self, name : str, from_ : Intersection, to : Intersection, spdLim: float, traffic_signal=None):
        self.name = name
        self.from_ = from_
        self.to = to
        self.spdLim = spdLim*1000/3600
        self.traffic_signal = traffic_signal

        self.calculate_cords()

        self.cars = []
        
        self.graphicsItem = None

    def render(self, view, scale):
        self.view = view
        x1 = self.startx * scale
        y1 = self.starty * scale
        x2 = self.endx * scale
        y2 = self.endy * scale

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
    
    def calculate_cords(self):
        fx, fy = self.from_.x, self.from_.y
        tx, ty = self.to.x, self.to.y
        dx, dy = tx-fx, ty-fy
        raw_len = np.sqrt(dx**2 + dy**2)
        self.startx = fx + dx*(self.from_.diam/2/raw_len)
        self.starty = fy + dy*(self.from_.diam/2/raw_len)
        self.endx = tx - dx*(self.from_.diam/2/raw_len)
        self.endy = ty - dy*(self.from_.diam/2/raw_len)
        dx, dy = self.endx-self.startx, self.endy-self.starty
        self.len = np.sqrt(dx**2 + dy**2)



class Path():
    def __init__(self, name : str, roads : List[Road], current : float):
        self.roads = roads
        self.current = current

class Car():
    def __init__(self, path : Path, update_dur : float, maxSpd= 20.0, view = None):
        self.path = path
        self.road = path.roads[0]
        self.update_dur = update_dur
        self.maxSpd = maxSpd
        self.view = view
    
        self.graphicsItem = None

        self.tot_stages = len(self.path.roads)
        self.stage = 0
        self.in_intersection = True
        self.transit_timer = 0

        self.prev_progress = 0.0
        self.progress = 0.0
        self.prev_speed = 0.0
        self.speed = 0.0

        self.done = False

        self.road.cars.append(self)
        self.xpos = self.road.startx
        self.ypos = self.road.starty

        dx = self.road.endx - self.road.startx
        dy = -self.road.endy - self.road.starty
        vec = complex(dx, dy)
        self.rot = np.angle(vec, deg=True)

    def update(self):
        if self.transit():
            return
        self.relative_safe_dist_drive()
        self.record()
        
    def render(self, view, scale):
        self.view = view

        x = self.xpos * scale
        y = self.ypos * scale
        h = CAR_HEIGHT * scale
        w = CAR_WIDTH * scale

        if self.graphicsItem == None:
            randColor = np.random.randint(0, 4)
            if randColor == 0:
                color = view.redBrush
            elif randColor == 1:
                color = view.yellowBrush
            elif randColor == 2:
                color = view.greenBrush
            elif randColor == 3:
                color = view.blueBrush
            self.graphicsItem = self.view.scene.addRect(x-h/2, y-w/2, h, w, view.blackPen, color)
        self.graphicsItem.setRect(0, 0, h, w)
        self.graphicsItem.setPos(x, y)
        self.graphicsItem.setRotation(self.rot)
    
    def leave(self):
        if self.view != None:
            self.done = True
            self.view.scene.removeItem(self.graphicsItem)

    def transit(self):
        if self.progress >= self.road.len:
            self.in_intersection = True
            self.progress = 0
            self.road.cars.remove(self)
            self.stage += 1
            if self.stage >= self.tot_stages:
                self.leave()
                return True
            self.road = self.path.roads[self.stage]
            self.road.cars.append(self)
        if self.in_intersection:
            self.transit_timer += self.update_dur
            if self.transit_timer >= TRANSIT_TIME:
                self.in_intersection = False
                self.transit_timer = 0
                return False
            return True
        return False

    def relative_safe_dist_drive(self):
        idx = self.road.cars.index(self)
        if idx == 0:
            if self.road.traffic_signal != None:
                if self.road.traffic_signal.signal == Signals.GREEN:
                    self.speed = self.maxSpd
                elif self.road.traffic_signal.signal == Signals.RED:
                    if self.road.len - self.prev_progress < 20: # m
                        self.speed = 0
                    else:
                        self.speed = self.maxSpd

        else:
            front_car = self.road.cars[idx - 1]
            front_spd = front_car.prev_speed
            front_dx = front_car.prev_progress - self.progress
            spd = front_dx + front_spd * self.update_dur - SAFE_DIST
            if spd > self.maxSpd:
                spd = self.maxSpd
            elif spd < 0:
                spd = 0
            self.speed = spd
        self.progress += self.speed * self.update_dur

        self.xpos = self.road.startx * (1 - self.progress/self.road.len) + self.road.endx * self.progress/self.road.len
        self.ypos = self.road.starty * (1 - self.progress/self.road.len) + self.road.endy * self.progress/self.road.len

        dx = self.road.endx - self.road.startx
        dy = -self.road.endy + self.road.starty
        vec = complex(dx, dy)
        self.rot = np.angle(vec, deg=True)
    
    def record(self):
        self.prev_speed = self.speed
        self.prev_progress = self.progress

class Traffic_signal():
    def __init__(self, def_signal):
        self.signal = def_signal

class Signals(enum.IntEnum):
    GREEN = 0
    YELLOW = 1
    RED = 2
