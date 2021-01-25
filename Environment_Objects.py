import numpy as np
import math
import enum
from typing import List
import random

CAR_WIDTH = 2
CAR_HEIGHT = 3

lane_ = 2
ROAD_WIDTH = 12 * lane_ * 2

TRAFFIC_SIGNAL_DIAM = 5
TRAFFIC_SIGNAL_DIST = 20
TRAFFIC_SIGNAL_AWAY = 10
INTERSECTION_DIAM = (ROAD_WIDTH/20)*12

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

class Lane():
    def __init__(self, env,  name : str, lane : int, op, from_ : Intersection, to : Intersection, spdLim: float, traffic_signal=None):
        #make one lane
        self.from_ = from_
        self.to = to
        self.env = env
        self.name = name
        self.lane = lane
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

        self.calculate_cords()
    
    def render(self, view, scale):
        self.view = view
        x1 = self.startx * scale
        y1 = self.starty * scale
        x2 = self.endx * scale
        y2 = self.endy * scale

        road_w = ROAD_WIDTH * scale

        length = (math.sqrt((x2 - x1)**2 + (y2 - y1)**2) + road_w)

        x = x1 - math.sin(self.rot+math.pi*3/4)*road_w*math.sqrt(2)/2
        y = y1 + math.cos(self.rot+math.pi*3/4)*road_w*math.sqrt(2)/2

        if self.graphicsItem == None:
            self.graphicsItem = view.scene.addRect(0, 0, 0, 0, view.grayPen, view.grayBrush)
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
            self.car_density.append(len(self.cars)/((math.sqrt((self.from_.x - self.to.x)**2 + (self.from_.y - self.to.y)**2))*ROAD_WIDTH))
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
        self.get_waittime_line
        return countsum/minute

    def get_waittime_line(self):
        line_long = 0
        print(1)
        for car in self.cars:
            line_long += car.height
        print(line_long)
        return line_long

    def initialize(self):
        self.cars.clear()

    def isAvailable(self):
        if len(self.cars) == 0:
            return -1, -1
        if len(self.cars) >= 1:
            if self.cars[len(self.cars)-1].progress < SAFE_DIST/2:
                return 0, 0
        return self.name[6],self.cars[len(self.cars)-1].progress

class Road():
    def __init__(self, env, lanenum : int, op : bool, name : str, from_ : Intersection, to : Intersection, spdLim: float, traffic_signal=None):
        self.op = op
        self.lanenum = lanenum
        self.env = env
        self.name = name
        self.number = -1
        self.from_ = from_
        self.to = to
        self.spdLim = spdLim*1000/3600
        self.lane = {}


        if traffic_signal != None:
            self.traffic_signal = traffic_signal
            self.traffic_signal.road = self
        else:
            self.traffic_signal = None

        self.calculate_cords()
        print(self.rotd)

        number = self.lanenum + 1
        for i in range(1, number):
            add = Lane(self.env, self.name+"-"+str(i), i, self.op, self.from_, self.to, self.spdLim, self.traffic_signal)
            self.lane[self.name+"-"+str(i)] = add
        
        self.graphicsItem = None

    def render(self, view, scale):
        self.view = view
        x1 = self.startx * scale
        y1 = self.starty * scale
        x2 = self.endx * scale
        y2 = self.endy * scale

        road_w = ROAD_WIDTH * scale

        length = (math.sqrt((x2 - x1)**2 + (y2 - y1)**2) + road_w)

        x = x1 - math.sin(self.rot+math.pi*3/4)*road_w*math.sqrt(2)/2
        y = y1 + math.cos(self.rot+math.pi*3/4)*road_w*math.sqrt(2)/2

        if self.graphicsItem == None:
            self.graphicsItem = view.scene.addRect(0, 0, 0, 0, view.grayPen, view.grayBrush)
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
        self.lane[self.name+"-"+str(car.lane)].car_enter(car)

    def update(self):
        for lane in self.lane:
            self.lane[lane].update()

    def speed(self):
        speed = 0
        number = 0
        for lane in self.lane:
            number += 1
            speed += self.lane[lane].speed()
        return speed/number

    def get_car_density(self, minute):
        car_density = 0
        number = 0
        for lane in self.lane:
            number += 1 
            car_density += self.lane[lane].get_car_density(minute)
        return car_density/number

    def get_mean_speed(self, minute):
        mean_speed = 0
        number = 0
        for lane in self.lane:
            number += 1
            mean_speed += self.lane[lane].get_mean_speed(minute)
        return mean_speed/number

    def get_trafficflow(self, minute):
        trafficflow = 0
        number = 0
        for lane in self.lane:
            number += 1
            trafficflow += self.lane[lane].get_trafficflow(minute)
        return trafficflow/number

    def get_waittime_line(self):
        waittime = 0
        number = 0
        for lane in self.lane:
            number += 1
            waittime += self.lane[lane].get_waittime_line(minute)
        return waittime/number
    
    def initialize(self):
        for lane in self.lane:
            self.lane[lane].initialize()

    def isAvailable(self):
        bestlanenum = 0
        lanenum = 0
        shortest_progress = (math.sqrt((self.from_.x - self.to.x)**2 + (self.from_.y - self.to.y)**2))
        longgest_progress = 0
        number = 0
        acceptlist = []
        for lanes in self.lane:
            number += 1
            lanenum, progress = self.lane[lanes].isAvailable()
            if lanenum == -1 and progress == -1:
                return number
            if lanenum == 0 and progress == 0:
                continue
            if progress > longgest_progress :
                bestlanenum = number
                longgest_progress = progress
        return bestlanenum
    

class Path():
    ''' Add a new path that cars follow.
        Current: Cars per minute '''
    def __init__(self, name : str, roads : List[Road], flow : float):
        self.name = name
        self.roads = roads
        self.flow = flow # Cars per minute


class Car():
    def __init__(self, env, lane, next_lane : int, path : Path, height : int, update_dur : float, maxSpd= 20.0, view = None):
        self.env = env
        self.lane = lane
        self.path = path
        self.road = path.roads[0]
        self.update_dur = update_dur
        self.maxSpd = maxSpd
        self.height = height
        self.view = view
        self.next_lane = next_lane
        
        self.graphicsItem = None

        x = self.road.isAvailable()
        self.lane = x

        self.randColor = 0
        y = random.randint(1,100)
        if y > 0 and y <= 20:
            self.height = 6
            self.randColor = 0
        elif y > 20 and y <= 80:
            self.height = 3
            self.randColor = 1
        elif y > 80 and y <= 100:
            self.height = 10
            self.randColor = 2
        

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
        
    def render(self, view, scale):
        self.view = view

        x = self.xpos * scale
        y = self.ypos * scale
        h = self.height * scale
        w = CAR_WIDTH * scale

        if self.graphicsItem == None:
            if self.randColor == 0:
                color = view.redBrush
            elif self.randColor == 1:
                color = view.yellowBrush
            elif self.randColor == 2:
                color = view.greenBrush
            '''elif randColor == 3:
                color = view.blueBrush'''
            self.graphicsItem = self.view.scene.addRect(x-h/2, y-w/2, h, w, view.blackPen, color)
            self.graphicsItem.setRect(0, 0, h, w)
        self.graphicsItem.setPos(x, y)
        self.graphicsItem.setRotation(self.rot)
    
    def leave(self):
        self.end_time = self.env.timer
        self.end_time = self.end_time - self.start_time
        self.done = True
        if self.view != None and self.graphicsItem != None:
            self.view.scene.removeItem(self.graphicsItem)

    def getWaitTime(self):
        curTime = self.env.timer
        return curTime - self.start_time

    def transit(self):
        if self.progress >= self.road.len:
            self.in_intersection = True
            self.progress = 0
            self.road.lane[self.road.name+"-"+str(self.lane)].cars.remove(self)
        
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
        idx = self.road.lane[self.road.name+"-"+str(self.lane)].cars.index(self)
        if idx == 0:
            if self.road.traffic_signal != None:
                if self.road.traffic_signal.signal != Signals.RED:
                    if self.stage < self.tot_stages - 1:
                        if self.path.roads[self.stage+1].isAvailable() == 0 and self.road.len - self.prev_progress - self.height/2 - SAFE_DIST< TRAFFIC_SIGNAL_DIST:
                            self.speed = 0
                        else :
                            self.speed = self.maxSpd


                        
                    else:
                        self.speed = self.maxSpd
                else:
                    
                    if self.road.len - self.prev_progress - self.height/2< TRAFFIC_SIGNAL_DIST: # m
                        self.speed = 0

                    else:
                        self.speed = self.maxSpd       
            else:
                self.speed = self.maxSpd
        else:
            front_car = self.road.lane[self.road.name+"-"+str(self.lane)].cars[idx - 1]
            front_spd = front_car.prev_speed
            front_dist = front_car.prev_progress - self.progress - self.height/2 - front_car.height/2
            spd = front_dist + front_spd * self.update_dur - SAFE_DIST
            if spd > self.maxSpd:
                spd = self.maxSpd
            elif spd < 0:
                spd = 0
            self.speed = spd
        self.progress += self.speed * self.update_dur

        offset = ((ROAD_WIDTH/(lane_*2))-1)*int(self.lane)

        if self.road.rotd >= 0 and self.road.rotd <= 45 or self.road.rotd >= 180 and self.road.rotd <= 225:
            if self.road.op == False:
                self.xpos = self.road.startx * (1 - self.progress/self.road.len) + self.road.endx * self.progress/self.road.len #+ offset
                self.ypos = self.road.starty * (1 - self.progress/self.road.len) + self.road.endy * self.progress/self.road.len + offset

            elif self.road.op == True:
                self.xpos = self.road.startx * (1 - self.progress/self.road.len) + self.road.endx * self.progress/self.road.len #- offset
                self.ypos = self.road.starty * (1 - self.progress/self.road.len) + self.road.endy * self.progress/self.road.len - offset
        else:
            if self.road.op == False:
                self.xpos = self.road.startx * (1 - self.progress/self.road.len) + self.road.endx * self.progress/self.road.len + offset
                self.ypos = self.road.starty * (1 - self.progress/self.road.len) + self.road.endy * self.progress/self.road.len #+ offset

            elif self.road.op == True:
                self.xpos = self.road.startx * (1 - self.progress/self.road.len) + self.road.endx * self.progress/self.road.len - offset
                self.ypos = self.road.starty * (1 - self.progress/self.road.len) + self.road.endy * self.progress/self.road.len #- offset

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
    def __init__(self, def_signal, update_dur, master=None):
        self.signal = def_signal
        self.update_dur = update_dur
        self.road : Road = None

        self.initialize()
        self.master = master
        self.isSlave = False
        if self.master != None:
            self.isSlave = True

        self.graphicsItem = None

    def initialize(self):
        self.state = 0
        self.states = TrafficSignalStates.stateTime.copy()
        self.timer = TrafficSignalStates.stateSignal[self.state]

    def update(self):
        if not self.isSlave:
            self.timer = (self.timer * 10 - self.update_dur * 10)/10
            if self.timer <= 0:
                self.state = (self.state + 1) % len(TrafficSignalStates.stateSignal)
                self.timer = self.states[self.state]
                self.signal = TrafficSignalStates.stateSignal[self.state]
        else:
            self.state = (self.master.state + 3) % len(TrafficSignalStates.stateSignal)
            self.signal = TrafficSignalStates.stateSignal[self.state]

    def render(self, view, scale):
        self.view = view
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
            self.graphicsItem = view.scene.addEllipse(0, 0, 0, 0, view.blackPen, view.greenBrush)
        if self.signal == Signals.GREEN:
            self.graphicsItem.setBrush(view.greenBrush)
        if self.signal == Signals.YELLOW:
            self.graphicsItem.setBrush(view.yellowBrush)
        if self.signal == Signals.RED:
            self.graphicsItem.setBrush(view.redBrush)
        self.graphicsItem.setRect(x-diam/2, y-diam/2, diam, diam)

    def change_duration(self, green, red):
        self.states[1] = green
        self.states[4] = red

    def get_next_green_time(self):
        i = self.state
        time = 0
        if i == 1:
            pass
        else:
            time += self.timer
            i = (i + 1) % len(TrafficSignalStates.stateTime)
            while i != 1:
                time += self.states[i]
                i = (i + 1) % len(TrafficSignalStates.stateTime)
        return time

class Signals(enum.IntEnum):
    GREEN = 0
    YELLOW = 1
    RED = 2


class TrafficSignalStates:
    R_ALL_RED_1 =   0
    G_GREEN =       1
    Y_YELLOW =      2
    R_ALL_RED_2 =   3
    R_RED =         4
    R_COUNTER_YELLOW = 5
    
    stateSignal = { 0: Signals.RED,
                    1: Signals.GREEN,
                    2: Signals.YELLOW,
                    3: Signals.RED,
                    4: Signals.RED,
                    5: Signals.RED,}

    stateTime = {   0: 2,
                    1: 30, # Default value
                    2: 3,
                    3: 2,
                    4: 30, # Default value
                    5: 3}