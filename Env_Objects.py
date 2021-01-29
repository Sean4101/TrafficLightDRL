import numpy as np
import math
import enum

from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *

from typing import List 

UPDATE_DUR = 0.1

CAR_WIDTH = 2
CAR_HEIGHT = 3

TRAFFIC_SIGNAL_DIAM = 5
TRAFFIC_SIGNAL_DIST = 20
TRAFFIC_SIGNAL_AWAY = 10
INTERSECTION_DIAM = 20
ROAD_WIDTH = 12

TRANSIT_TIME = 2
SAFE_DIST = 7
SIGNAL_MIN = 12
SIGNAL_MAX = 120

class Intersection():
    def __init__(self, xpos : float, ypos : float, diam : float):
        self.x = xpos
        self.y = ypos
        self.diam = diam

        self.cars = []

        self.graphicsItem = None

    def render(self, scene, scale):

        x = self.x * scale
        y = self.y * scale
        diam = self.diam * scale

        self.scene = scene
        if self.graphicsItem == None:
            self.graphicsItem = self.scene.addEllipse(0, 0, 0, 0, QPen(Qt.gray), QBrush(Qt.gray))
        self.graphicsItem.setRect(x-diam/2, y-diam/2, diam, diam)

class Road():
    def __init__(self, env, from_ : Intersection, to : Intersection, spdLim: float, traffic_signal=None):
        self.env = env
        self.number = -1
        self.from_ = from_
        self.to = to
        self.spdLim = spdLim*1000/3600
        if traffic_signal != None:
            self.traffic_signal = traffic_signal
            self.traffic_signal.road = self
        else:
            self.traffic_signal = None

        self.calculate_cords()

        self.cars = []
        self.car_count_minute = []
        self.car_density = []
        self.car_speed = []

        for i in range(300):
            self.car_count_minute.append(0)
            self.car_density.append(0)
            self.car_speed.append(0)
        self.flow_per_sec = []
        self.trafficflow = 0
        self.trafficflow_in_minute = 0
        self.trafficflow_in_two_minute = 0
        self.trafficflow_in_five_minute = 0
        self.density_per_one_minute = 0
        self.density_per_two_minute = 0
        self.density_per_five_minute=  0
        self.car_tot_count = 0
        
        self.graphicsItem = None

    def render(self, scene, scale):
        x1 = self.startx * scale
        y1 = self.starty * scale
        x2 = self.endx * scale
        y2 = self.endy * scale

        road_w = ROAD_WIDTH * scale

        length = (math.sqrt((x2 - x1)**2 + (y2 - y1)**2) + road_w)

        x = x1 - math.sin(self.rot+math.pi*3/4)*road_w*math.sqrt(2)/2
        y = y1 + math.cos(self.rot+math.pi*3/4)*road_w*math.sqrt(2)/2

        if self.graphicsItem == None:
            self.graphicsItem = scene.addRect(0, 0, 0, 0, QPen(Qt.gray), QBrush(Qt.gray))
        self.graphicsItem.setRect(0, 0, length, road_w)
        self.graphicsItem.setPos(x, y)
        self.graphicsItem.setRotation(self.rotd)
    
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
        vec = complex(dx, dy)
        self.rot = np.angle(vec)
        self.rotd = np.angle(vec, deg=True)

    def car_enter(self, car):
        self.cars.append(car)
        self.car_tot_count += 1

    def update(self):
        if self.env.timer % 1 == 0:
            self.car_count_minute.append(self.car_tot_count)
            self.trafficflow = (self.car_tot_count - self.car_count_minute[0])
            self.car_density.append(len(self.cars)/self.len*ROAD_WIDTH)
            self.car_speed.append(self.speed())
            if len(self.car_count_minute) > 300:
                self.car_count_minute.pop(0)
                self.car_density.pop(0)
                self.car_speed.pop(0)

    def speed(self):
        self.speedsum = 0
        for car in self.cars:
            self.speedsum += car.prev_speed
        if len(self.cars) == 0:
            mspeed = 0
        else:
            mspeed = self.speedsum/len(self.cars)
        return mspeed

    def get_car_density(self, minute):
        den = 0
        for i in range((5-minute)*60, 5*60):
            den += self.car_density[i]
        return den/minute

    def get_mean_speed(self, minute):
        speed = 0
        for i in range((5-minute)*60, 5*60):
            speed += self.car_speed[i]
        return speed/(minute*60)

    def get_trafficflow(self, minute):
        countsum = self.car_count_minute[5*60-1]-self.car_count_minute[(5-minute)*60]
        return countsum/minute

    def get_queue(self):
        l = len(self.cars)
        if l == 0:
            return 0
        for i, car in enumerate(self.cars):
            if car.prev_speed > 5:
                return i
        return l
        
    def initialize(self):
        self.cars.clear()

    def isAvailable(self):
        if len(self.cars) >= 1:
            if self.cars[len(self.cars)-1].progress < SAFE_DIST/2:
                return False
        return True

class Path():
    ''' Add a new path that cars follow.
        Current: Cars per minute '''
    def __init__(self, roads : List[Road]):
        self.roads = roads
        self.flow = 10 # Cars per minute, default is 10

class Car():
    def __init__(self, env, path : Path, update_dur : float, maxSpd= 20.0, scene = None):
        self.env = env
        self.path = path
        self.road = path.roads[0]
        self.update_dur = update_dur
        self.maxSpd = maxSpd
        self.scene = scene
    
        self.graphicsItem = None

        self.tot_stages = len(self.path.roads)
        self.stage = 0
        self.in_intersection = True
        self.transit_timer = 0
        self.start_time = self.env.timer
        self.end_time = 0

        self.prev_progress = 0.0
        self.progress = 0.0
        self.prev_speed = 0.0
        self.speed = 0.0

        self.done = False

        self.road.car_enter(self)
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
        
    def render(self, scene, scale):

        x = self.xpos * scale
        y = self.ypos * scale
        h = CAR_HEIGHT * scale
        w = CAR_WIDTH * scale

        if self.graphicsItem == None:
            randColor = np.random.randint(0, 4)
            if randColor == 0:
                color = QBrush(Qt.red)
            elif randColor == 1:
                color = QBrush(Qt.yellow)
            elif randColor == 2:
                color = QBrush(Qt.green)
            elif randColor == 3:
                color = QBrush(Qt.blue)
            self.graphicsItem = self.scene.addRect(x-h/2, y-w/2, h, w, QPen(Qt.black), color)
            self.graphicsItem.setRect(0, 0, h, w)
        self.graphicsItem.setPos(x, y)
        self.graphicsItem.setRotation(self.rot)
    
    def leave(self):
        self.end_time = self.env.timer
        self.end_time = self.end_time - self.start_time
        self.done = True
        if self.scene != None and self.graphicsItem != None:
            self.scene.removeItem(self.graphicsItem)

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
            self.road.car_enter(self)

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
                if self.road.traffic_signal.signal != Signals.RED:
                    if self.stage < self.tot_stages - 1:
                        if self.path.roads[self.stage+1].isAvailable() == False and \
                           self.road.len - self.prev_progress < TRAFFIC_SIGNAL_DIST:
                            self.speed = 0
                        else:
                            self.speed = self.maxSpd
                    else:
                        self.speed = self.maxSpd
                else:
                    if self.road.len - self.prev_progress < TRAFFIC_SIGNAL_DIST: # m
                        self.speed = 0
                    else:
                        self.speed = self.maxSpd
            else:
                self.speed = self.maxSpd
        else:
            front_car = self.road.cars[idx - 1]
            front_spd = front_car.prev_speed
            front_dist = front_car.prev_progress - self.progress
            spd = front_dist + front_spd * self.update_dur - SAFE_DIST
            if spd > self.maxSpd:
                spd = self.maxSpd
            elif spd < 0:
                spd = 0
            self.speed = spd
        self.progress += self.speed * self.update_dur

        self.xpos = self.road.startx * (1 - self.progress/self.road.len) + self.road.endx * self.progress/self.road.len
        self.ypos = self.road.starty * (1 - self.progress/self.road.len) + self.road.endy * self.progress/self.road.len

        self.rot = self.road.rotd
    
    def record(self):
        self.prev_speed = self.speed
        self.prev_progress = self.progress

    
    def car_two_timing_delta(self):
        delta = self.carcountnum2 - self.carcountnum1
        self.carcountnum1 = self.carcountnum2
        if len(self.carcount) == 60:
            del(self.carcount[0])
            self.carcount.append(delta)

class Traffic_signal():
    def __init__(self, def_signal, master=None):
        self.signal = def_signal
        self.road : Road = None

        self.master = master
        self.slave = None
        if self.master != None:
            self.isSlave = True
            self.signal = Signals.RED
        else:
            self.isSlave = False
            self.signal = Signals.GREEN

        self.graphicsItem = None

    def initialize(self):
        self.light_timer = 0
        if self.master != None:
            self.master.slave = self

    def update(self):
        if self.isSlave:
            self.signal = Signals.RED if self.master.signal == Signals.GREEN else Signals.GREEN
        self.light_timer += UPDATE_DUR
        if self.light_timer >= SIGNAL_MAX:
            new_sig = Signals.RED if self.signal == Signals.GREEN else Signals.GREEN
            self.change_signal(new_sig)

    def render(self, scene, scale):
        diam = TRAFFIC_SIGNAL_DIAM * scale
        x1 = self.road.to.x
        x2 = self.road.from_.x
        y1 = self.road.to.y
        y2 = self.road.from_.y
        rot = self.road.rot

        mx = x1 + math.cos(rot+math.pi)*TRAFFIC_SIGNAL_DIST
        my = y1 + math.sin(rot+math.pi)*TRAFFIC_SIGNAL_DIST

        x = (mx + math.cos(rot+math.pi*3/2)*TRAFFIC_SIGNAL_AWAY) * scale
        y = (my + math.sin(rot+math.pi*3/2)*TRAFFIC_SIGNAL_AWAY) * scale

        if self.graphicsItem == None:
            self.graphicsItem = scene.addEllipse(0, 0, 0, 0, QPen(Qt.black), QBrush(Qt.green))
        if self.signal == Signals.GREEN:
            self.graphicsItem.setBrush(QBrush(Qt.green))
        if self.signal == Signals.YELLOW:
            self.graphicsItem.setBrush(QBrush(Qt.yellow))
        if self.signal == Signals.RED:
            self.graphicsItem.setBrush(QBrush(Qt.red))
        self.graphicsItem.setRect(x-diam/2, y-diam/2, diam, diam)

    def change_signal(self, sig):
        ''' 0 = red, 1 = green '''
        og = 0 if self.signal == Signals.RED else 1
        changed = og != sig
        if changed:
            if self.light_timer >= 12:
                self.light_timer = 0
                if self.slave != None:
                    self.slave.light_timer = 0
                self.signal = Signals.RED if sig == 0 else Signals.GREEN

class Signals(enum.IntEnum):
    RED = 0
    GREEN = 1
    YELLOW = 2
