import numpy as np
import gym
import statistics
import time
from PyQt5.QtWidgets import QApplication

from typing import List
from gym import spaces
from Env_Objects import Intersection, Road, Path, Car, Traffic_signal, Signals
from Env_Objects import CAR_HEIGHT, lane
STATE_EACH_ROAD = 1
FLOW_MIN = 0
FLOW_MAX = 20

UPDATE_DUR = 0.1

class TrafficDRL_Env(gym.Env):
    def __init__(self, render_scene=None):
        super(TrafficDRL_Env, self).__init__()
        
        self.buildEnv()

        self.action_space = spaces.MultiBinary(self.n_action)

        self.observation_space = spaces.Box(
            low=0, 
            high=255,
            shape=(self.n_state,),
            dtype=np.float32)
        
        self.step_per_epi = 3600

        self.render_scene = render_scene
        self.isRendering = False
        self.scale = 1

        self.tot_progress = 0

    def reset(self, fixed_flow=None, episode_len=3600, isTest=False):
        self.isTest = isTest
        self.timer = 0
        self.episode_len = episode_len
        self.buildEnv()

        self.cars = []
        self.prev_avg_wait = 0
        self.avg_waiting_time = 0
        self.tot_car_cnt = 0

        if fixed_flow == None:
            flows = np.random.randint(FLOW_MIN, high=FLOW_MAX, size=(len(self.paths)))
        else:
            flows = fixed_flow

        for i, path in enumerate(self.paths):
            path.flow = flows[i]

        for signal in self.signals:
            signal.initialize()

        first_state = self.calculateState()
        return first_state

    def step(self, action):
        self.makeAction(action)
        self.n_exit_cars = 0
        self.n_fail_enter = 0
        for i in range(10):
            self.update() # update every object and sum up penalty
            if self.isRendering:
                self.update_render()
        finished = self.timer>=self.episode_len
        state_ = self.calculateState()
        reward = self.calculateReward()
        done = finished
        info = {}
        if done:
            print(self.avg_waiting_time/self.tot_progress)
        return state_, reward, done, info

    def render(self, mode='human', close=False):
        self.isRendering = not close
        if close:
            self.clearCarItems()

    def buildEnv(self):
        ''' Build the structures of the environment.\n
            Use addTrafficSignal(), addIntersection(), 
            addRoad(), addPath() in this method to 
            create your traffic system. '''

        self.intersections = []
        self.roads = []
        self.paths = []
        self.signals = []
        self.cars = []
        self.master_signals = []
        # environment 1
        # 1 intersection, 2 path

        '''
        s1m = self.addTrafficSignal(Signals.RED, True)
        s1s = self.addTrafficSignal(Signals.RED, master=s1m)

        o = self.addIntersection(0, 0)
        a = self.addIntersection(200, 0)
        b = self.addIntersection(-200, 0)
        c = self.addIntersection(0, 200)
        d = self.addIntersection(0, -200)

        ao = self.addRoad(lane, True, a, o, s1m)
        ob = self.addRoad(lane, False, o, b)
        co = self.addRoad(lane, True, c, o, s1s)
        od = self.addRoad(lane, False, o, d)

        p1 = self.addPath([ao, od])
        p2 = self.addPath([co, ob])
        '''

        # environment 2
        # 1 intersection, 2 path
        
        '''
        s1m = self.addTrafficSignal(Signals.RED, True)
        s1s = self.addTrafficSignal(Signals.RED, master=s1m)

        o = self.addIntersection(0, 0)
        a = self.addIntersection(200, 0)
        b = self.addIntersection(-200, 0)
        c = self.addIntersection(0, 200)
        d = self.addIntersection(0, -200)

        bo = self.addRoad(lane, False, b, o, s1m)
        oa = self.addRoad(lane, False, o, a)
        co = self.addRoad(lane, False, c, o, s1s)
        od = self.addRoad(lane, False, o, d)

        p1 = self.addPath([bo, oa])
        p2 = self.addPath([co, od])
        '''

        # environment 3
        # 1 intersection, 2 path
        
        '''
        s1m = self.addTrafficSignal(Signals.RED, True)
        s1s = self.addTrafficSignal(Signals.RED, master=s1m)

        o = self.addIntersection(0, 0)
        a = self.addIntersection(200, 0)
        b = self.addIntersection(-200, 0)
        c = self.addIntersection(0, 200)
        d = self.addIntersection(0, -200)

        bo = self.addRoad(lane, False, b, o)
        ao = self.addRoad(lane, True, a, o, s1s)
        co = self.addRoad(lane, False, c, o, s1m)
        oa = self.addRoad(lane, False, o, a)
        oc = self.addRoad(lane, True, o,c)
        od = self.addRoad(lane, False, o, d)

        p1 = self.addPath([co, oa])
        p2 = self.addPath([ao, oc])
        '''

        # environment 4
        # 1 intersection, 4 path
        
        '''
        s1m = self.addTrafficSignal(Signals.RED, True)
        s1s = self.addTrafficSignal(Signals.RED, master=s1m)

        o = self.addIntersection(0, 0)
        a = self.addIntersection(200, 0)
        b = self.addIntersection(-200, 0)
        c = self.addIntersection(0, 200)
        d = self.addIntersection(0, -200)

        co = self.addRoad(lane, False, c, o, s1m)
        od = self.addRoad(lane, False, o, d)
        bo = self.addRoad(lane, False, b, o, s1s)
        oa = self.addRoad(lane, False, o, a)

        do = self.addRoad(lane, True, d, o, s1m)
        oc = self.addRoad(lane, True, o, c)
        ao = self.addRoad(lane, True, a, o, s1s)
        ob = self.addRoad(lane, True, o, b)

        p1 = self.addPath([bo, oa])
        p2 = self.addPath([co, od])
        p3 = self.addPath([do, oc])
        p4 = self.addPath([ao, ob])
        '''

        # environment 5
        # 1 intersection, 3 path

        '''
        s1m = self.addTrafficSignal(Signals.RED, True)
        s1s = self.addTrafficSignal(Signals.RED, master=s1m)

        o = self.addIntersection(0, 0)
        a = self.addIntersection(200, 0)
        b = self.addIntersection(-200, 0)
        c = self.addIntersection(0, 200)
        d = self.addIntersection(0, -200)

        co = self.addRoad(lane, False, c, o, s1m)
        ao = self.addRoad(lane, True, a, o, s1s)
        do = self.addRoad(lane, True, d, o, s1m)
        ob = self.addRoad(lane, True, o, b)

        p1 = self.addPath([co, ob])
        p2 = self.addPath([ao, ob])
        p3 = self.addPath([do, ob])
        '''

        # environment 6
        # 1 intersection, 12 path

        '''
        s1m = self.addTrafficSignal(Signals.RED, True)
        s1s = self.addTrafficSignal(Signals.RED, master=s1m)

        o = self.addIntersection(0, 0)
        a = self.addIntersection(200, 0)
        b = self.addIntersection(-200, 0)
        c = self.addIntersection(0, 200)
        d = self.addIntersection(0, -200)

        ao = self.addRoad(lane, False, a, o, s1m)
        ob = self.addRoad(lane, False, o, b)
        co = self.addRoad(lane, False, c, o, s1s)
        od = self.addRoad(lane, False, o, d)

        oa = self.addRoad(lane, True, o, a)
        bo = self.addRoad(lane, True, b, o, s1m)
        oc = self.addRoad(lane, True, o, c)
        do = self.addRoad(lane, True, d, o, s1s)

        p1 = self.addPath([ao, ob])
        p2 = self.addPath([ao, oc])
        p3 = self.addPath([ao, od])

        p4 = self.addPath([bo, oa])
        p5 = self.addPath([bo, oc])
        p6 = self.addPath([bo, od])

        p7 = self.addPath([co, oa])
        p8 = self.addPath([co, ob])
        p9 = self.addPath([co, od])

        p10 = self.addPath([do, oa])
        p11 = self.addPath([do, ob])
        p12 = self.addPath([do, oc])
        '''

        
        # environment 7
        # 4 intersection, 4 path

        '''
        s1m = self.addTrafficSignal(Signals.RED, True)
        s1s = self.addTrafficSignal(Signals.RED, master=s1m)
        s2m = self.addTrafficSignal(Signals.RED, True)
        s2s = self.addTrafficSignal(Signals.RED, master=s2m)
        s3m = self.addTrafficSignal(Signals.RED, True)
        s3s = self.addTrafficSignal(Signals.RED, master=s3m)
        s4m = self.addTrafficSignal(Signals.RED, True)
        s4s = self.addTrafficSignal(Signals.RED, master=s4m)

        A = self.addIntersection(200, 0)
        B = self.addIntersection(400, 0)
        C = self.addIntersection(0, -200)
        D = self.addIntersection(200, -200)
        E = self.addIntersection(400, -200)
        F = self.addIntersection(600, -200)
        G = self.addIntersection(0, -400)
        H = self.addIntersection(200, -400)
        I = self.addIntersection(400, -400)
        J = self.addIntersection(600, -400)
        K = self.addIntersection(200, -600)
        L = self.addIntersection(400, -600)

        AD = self.addRoad(lane, True, A, D, s1m)
        DH = self.addRoad(lane, True, D, H, s3m)
        HK = self.addRoad(lane, True, H, K)
        BE = self.addRoad(lane, True, B, E, s2m)
        EI = self.addRoad(lane, True, E, I, s4m)
        IL = self.addRoad(lane, True, I, L)
        CD = self.addRoad(lane, True, C, D, s1s)
        DE = self.addRoad(lane, True, D, E, s2s)
        EF = self.addRoad(lane, True, E, F)
        GH = self.addRoad(lane, True, G, H, s3s)
        HI = self.addRoad(lane, True, H, I, s4s)
        IJ = self.addRoad(lane, True, I, J)

        p1 = self.addPath([AD, DH, HK])
        p2 = self.addPath([BE, EI, IL])
        p3 = self.addPath([CD, DE, EF])
        p4 = self.addPath([GH, HI, IJ])
        '''

        # environment 8
        # 4 intersection, 8 path

        '''
        s1m = self.addTrafficSignal(Signals.RED, True)
        s1s = self.addTrafficSignal(Signals.RED, master=s1m)
        s2m = self.addTrafficSignal(Signals.RED, True)
        s2s = self.addTrafficSignal(Signals.RED, master=s2m)
        s3m = self.addTrafficSignal(Signals.RED, True)
        s3s = self.addTrafficSignal(Signals.RED, master=s3m)
        s4m = self.addTrafficSignal(Signals.RED, True)
        s4s = self.addTrafficSignal(Signals.RED, master=s4m)

        A = self.addIntersection(200, 0)
        B = self.addIntersection(400, 0)
        C = self.addIntersection(0, -200)
        D = self.addIntersection(200, -200)
        E = self.addIntersection(400, -200)
        F = self.addIntersection(600, -200)
        G = self.addIntersection(0, -400)
        H = self.addIntersection(200, -400)
        I = self.addIntersection(400, -400)
        J = self.addIntersection(600, -400)
        K = self.addIntersection(200, -600)
        L = self.addIntersection(400, -600)

        AD = self.addRoad(lane, True, A, D, s1m)
        DH = self.addRoad(lane, True, D, H, s3m)
        HK = self.addRoad(lane, True, H, K)
        BE = self.addRoad(lane, True, B, E, s2m)
        EI = self.addRoad(lane, True, E, I, s4m)
        IL = self.addRoad(lane, True, I, L)
        CD = self.addRoad(lane, True, C, D, s1s)
        DE = self.addRoad(lane, True, D, E, s2s)
        EF = self.addRoad(lane, True, E, F)
        GH = self.addRoad(lane, True, G, H, s3s)
        HI = self.addRoad(lane, True, H, I, s4s)
        IJ = self.addRoad(lane, True, I, J)

        DA = self.addRoad(lane, False, D, A)
        HD = self.addRoad(lane, False, H, D, s1m)
        KH = self.addRoad(lane, False, K, H, s3m)
        EB = self.addRoad(lane, False, E, B)
        IE = self.addRoad(lane, False, I, E, s2m)
        LI = self.addRoad(lane, False, L, I, s4m)
        DC = self.addRoad(lane, False, D, C)
        ED = self.addRoad(lane, False, E, D, s1s)
        FE = self.addRoad(lane, False, F, E, s2s)
        HG = self.addRoad(lane, False, H, G)
        IH = self.addRoad(lane, False, I, H, s3s)
        JI = self.addRoad(lane, False, J, I, s4s)

        p1 = self.addPath([AD, DH, HK])
        p2 = self.addPath([BE, EI, IL])
        p3 = self.addPath([CD, DE, EF])
        p4 = self.addPath([GH, HI, IJ])
        p5 = self.addPath([KH, HD, DA])
        p6 = self.addPath([LI, IE, EB])
        p7 = self.addPath([FE, ED, DC])
        p8 = self.addPath([JI, IH, HG])
        '''
        



        # environment 9
        # 4 intersection, 13 path
        '''
        s1m = self.addTrafficSignal(Signals.RED, True)
        s1s = self.addTrafficSignal(Signals.RED, master=s1m)
        s2m = self.addTrafficSignal(Signals.RED, True)
        s2s = self.addTrafficSignal(Signals.RED, master=s2m)
        s3m = self.addTrafficSignal(Signals.RED, True)
        s3s = self.addTrafficSignal(Signals.RED, master=s3m)
        s4m = self.addTrafficSignal(Signals.RED, True)
        s4s = self.addTrafficSignal(Signals.RED, master=s4m)

        A = self.addIntersection(200, 0)
        B = self.addIntersection(400, 0)
        C = self.addIntersection(0, -200)
        D = self.addIntersection(200, -200)
        E = self.addIntersection(400, -200)
        F = self.addIntersection(600, -200)
        G = self.addIntersection(0, -400)
        H = self.addIntersection(200, -400)
        I = self.addIntersection(400, -400)
        J = self.addIntersection(600, -400)
        K = self.addIntersection(200, -600)
        L = self.addIntersection(400, -600)

        AD = self.addRoad(lane, False, A, D, s1m)
        DH = self.addRoad(lane, False, D, H, s3m)
        HK = self.addRoad(lane, False, H, K)
        BE = self.addRoad(lane, False, B, E, s2m)
        EI = self.addRoad(lane, False, E, I, s4m)
        IL = self.addRoad(lane, False, I, L)
        CD = self.addRoad(lane, False, C, D, s1s)
        DE = self.addRoad(lane, False, D, E, s2s)
        EF = self.addRoad(lane, False, E, F)
        GH = self.addRoad(lane, False, G, H, s3s)
        HI = self.addRoad(lane, False, H, I, s4s)
        IJ = self.addRoad(lane, False, I, J)

        DA = self.addRoad(lane, True, D, A)
        HD = self.addRoad(lane, True, H, D, s1m)
        KH = self.addRoad(lane, True, K, H, s3m)
        EB = self.addRoad(lane, True, E, B)
        IE = self.addRoad(lane, True, I, E, s2m)
        LI = self.addRoad(lane, True, L, I, s4m)
        DC = self.addRoad(lane, True, D, C)
        ED = self.addRoad(lane, True, E, D, s1s)
        FE = self.addRoad(lane, True, F, E, s2s)
        HG = self.addRoad(lane, True, H, G)
        IH = self.addRoad(lane, True, I, H, s3s)
        JI = self.addRoad(lane, True, J, I, s4s)

        p1 = self.addPath([AD, DC])
        p2 = self.addPath([AD, DE, EB])
        p3 = self.addPath([AD, DE, EF])
        p4 = self.addPath([AD, DE, EI, IJ])
        p5 = self.addPath([AD, DE, EI, IL])
        p6 = self.addPath([AD, DE, EI, IH, HG])
        p7 = self.addPath([AD, DE, EI, IH, HK])
        p8 = self.addPath([AD, DH, HG])
        p9 = self.addPath([AD, DH, HK])
        p10 = self.addPath([AD, DH, HI, IJ])
        p11 = self.addPath([AD, DH, HI, IL])
        p12 = self.addPath([AD, DH, HI, IE, EB])
        p13 = self.addPath([AD, DH, HI, EB, EF])
        '''
        
        # environment 10
        # 4 intersection, 104 path

        '''
        s1m = self.addTrafficSignal(Signals.RED, True)
        s1s = self.addTrafficSignal(Signals.RED, master=s1m)
        s2m = self.addTrafficSignal(Signals.RED, True)
        s2s = self.addTrafficSignal(Signals.RED, master=s2m)
        s3m = self.addTrafficSignal(Signals.RED, True)
        s3s = self.addTrafficSignal(Signals.RED, master=s3m)
        s4m = self.addTrafficSignal(Signals.RED, True)
        s4s = self.addTrafficSignal(Signals.RED, master=s4m)

        A = self.addIntersection(200, 0)
        B = self.addIntersection(400, 0)
        C = self.addIntersection(0, -200)
        D = self.addIntersection(200, -200)
        E = self.addIntersection(400, -200)
        F = self.addIntersection(600, -200)
        G = self.addIntersection(0, -400)
        H = self.addIntersection(200, -400)
        I = self.addIntersection(400, -400)
        J = self.addIntersection(600, -400)
        K = self.addIntersection(200, -600)
        L = self.addIntersection(400, -600)

        AD = self.addRoad(lane, False, A, D, s1m)
        DH = self.addRoad(lane, False, D, H, s3m)
        HK = self.addRoad(lane, False, H, K)
        BE = self.addRoad(lane, False, B, E, s2m)
        EI = self.addRoad(lane, False, E, I, s4m)
        IL = self.addRoad(lane, False, I, L)
        CD = self.addRoad(lane, False, C, D, s1s)
        DE = self.addRoad(lane, False, D, E, s2s)
        EF = self.addRoad(lane, False, E, F)
        GH = self.addRoad(lane, False, G, H, s3s)
        HI = self.addRoad(lane, False, H, I, s4s)
        IJ = self.addRoad(lane, False, I, J)

        DA = self.addRoad(lane, True, D, A)
        HD = self.addRoad(lane, True, H, D, s1m)
        KH = self.addRoad(lane, True, K, H, s3m)
        EB = self.addRoad(lane, True, E, B)
        IE = self.addRoad(lane, True, I, E, s2m)
        LI = self.addRoad(lane, True, L, I, s4m)
        DC = self.addRoad(lane, True, D, C)
        ED = self.addRoad(lane, True, E, D, s1s)
        FE = self.addRoad(lane, True, F, E, s2s)
        HG = self.addRoad(lane, True, H, G)
        IH = self.addRoad(lane, True, I, H, s3s)
        JI = self.addRoad(lane, True, J, I, s4s)

        p1 = self.addPath([AD, DC])
        p2 = self.addPath([AD, DE, EB])
        p3 = self.addPath([AD, DE, EF])
        p4 = self.addPath([AD, DE, EI, IJ])
        p5 = self.addPath([AD, DE, EI, IL])
        p6 = self.addPath([AD, DE, EI, IH, HG])
        p7 = self.addPath([AD, DE, EI, IH, HK])
        p8 = self.addPath([AD, DH, HG])
        p9 = self.addPath([AD, DH, HK])
        p10 = self.addPath([AD, DH, HI, IJ])
        p11 = self.addPath([AD, DH, HI, IL])
        p12 = self.addPath([AD, DH, HI, IE, EB])
        p13 = self.addPath([AD, DH, HI, EB, EF])

        p14 = self.addPath([FE, EB])
        p15 = self.addPath([FE, EI, IJ])
        p16 = self.addPath([FE, EI, IL])
        p17 = self.addPath([FE, EI, IH, HK])
        p18 = self.addPath([FE, EI, IH, HG])
        p19 = self.addPath([FE, EI, IH, HD, DA])
        p20 = self.addPath([FE, EI, IH, HD, DC])
        p21 = self.addPath([FE, ED, DA])
        p22 = self.addPath([FE, ED, DC])
        p23 = self.addPath([FE, ED, DH, HK])
        p24 = self.addPath([FE, ED, DH, HG])
        p25 = self.addPath([FE, ED, DH, HI, IJ])
        p26 = self.addPath([FE, ED, DH, IJ, IL])

        p27 = self.addPath([LI, IJ])
        p28 = self.addPath([LI, IH, HK])
        p29 = self.addPath([LI, IH, HG])
        p30 = self.addPath([LI, IH, HD, DC])
        p31 = self.addPath([LI, IH, HD, DA])
        p32 = self.addPath([LI, IH, HD, DE, EF])
        p33 = self.addPath([LI, IH, HD, DE, EB])
        p34 = self.addPath([LI, IE, EF])
        p35 = self.addPath([LI, IE, EB])
        p36 = self.addPath([LI, IE, ED, DC])
        p37 = self.addPath([LI, IE, ED, DA])
        p38 = self.addPath([LI, IE, ED, DH, HK])
        p39 = self.addPath([LI, IE, ED, HK, HG])

        p40 = self.addPath([GH, HK])
        p41 = self.addPath([GH, HD, DC])
        p42 = self.addPath([GH, HD, DA])
        p43 = self.addPath([GH, HD, DE, EB])
        p44 = self.addPath([GH, HD, DE, EF])
        p45 = self.addPath([GH, HD, DE, EI, IL])
        p46 = self.addPath([GH, HD, DE, EI, IJ])
        p47 = self.addPath([GH, HI, IL])
        p48 = self.addPath([GH, HI, IJ])
        p49 = self.addPath([GH, HI, IE, EB])
        p50 = self.addPath([GH, HI, IE, EF])
        p51 = self.addPath([GH, HI, IE, ED, DC])
        p52 = self.addPath([GH, HI, IE, DC, DA])

        p53 = self.addPath([BE, EF])
        p54 = self.addPath([BE, ED, DA])
        p55 = self.addPath([BE, ED, DC])
        p56 = self.addPath([BE, ED, DH, HG])
        p57 = self.addPath([BE, ED, DH, HK])
        p58 = self.addPath([BE, ED, DH, HI, IJ])
        p59 = self.addPath([BE, ED, DH, HI, IL])
        p60 = self.addPath([BE, EI, IJ])
        p61 = self.addPath([BE, EI, IL])
        p62 = self.addPath([BE, EI, IH, HG])
        p63 = self.addPath([BE, EI, IH, HK])
        p64 = self.addPath([BE, EI, IH, HD, DA])
        p65 = self.addPath([BE, EI, IH, DA, DC])

        p66 = self.addPath([CD, DA])
        p67 = self.addPath([CD, DH, HG])
        p68 = self.addPath([CD, DH, HK])
        p69 = self.addPath([CD, DH, HI, IL])
        p70 = self.addPath([CD, DH, HI, IJ])
        p71 = self.addPath([CD, DH, HI, IE, EB])
        p72 = self.addPath([CD, DH, HI, IE, EF])
        p73 = self.addPath([CD, DE, EB])
        p74 = self.addPath([CD, DE, EF])
        p75 = self.addPath([CD, DE, EI, IL])
        p76 = self.addPath([CD, DE, EI, IJ])
        p77 = self.addPath([CD, DE, EI, IH, HG])
        p78 = self.addPath([CD, DE, EI, HG, HK])

        p79 = self.addPath([KH, HG])
        p80 = self.addPath([KH, HI, IL])
        p81 = self.addPath([KH, HI, IJ])
        p82 = self.addPath([KH, HI, IE, EF])
        p83 = self.addPath([KH, HI, IE, EB])
        p84 = self.addPath([KH, HI, IE, ED, DC])
        p85 = self.addPath([KH, HI, IE, ED, DA])
        p86 = self.addPath([KH, HD, DC])
        p87 = self.addPath([KH, HD, DA])
        p88 = self.addPath([KH, HD, DE, EF])
        p89 = self.addPath([KH, HD, DE, EB])
        p90 = self.addPath([KH, HD, DE, EI, IL])
        p91 = self.addPath([KH, HD, DE, IL, IJ])

        p92 = self.addPath([JI, IL])
        p93 = self.addPath([JI, IE, EF])
        p94 = self.addPath([JI, IE, EB])
        p95 = self.addPath([JI, IE, ED, DA])
        p96 = self.addPath([JI, IE, ED, DC])
        p97 = self.addPath([JI, IE, ED, DH, HK])
        p98 = self.addPath([JI, IE, ED, DH, HG])
        p99 = self.addPath([JI, IH, HK])
        p100 = self.addPath([JI, IH, HG])
        p101 = self.addPath([JI, IH, HD, DA])
        p102 = self.addPath([JI, IH, HD, DC])
        p103 = self.addPath([JI, IH, HD, DE, EF])
        p104 = self.addPath([JI, IH, HD, EF, EB])
        '''

        # environment 11
        # Lishan Senior High


        self.n_action = len(self.master_signals)
        self.n_state = len(self.roads)* STATE_EACH_ROAD + len(self.signals)

    def update(self):
        ''' Update the environment.'''
        #time.sleep(0.04)
        self.timer = (self.timer * 10 + UPDATE_DUR * 10)/10
        for path in self.paths:
            rand = np.random.rand()
            prob = path.flow/10/60
            if rand < prob:
                self.addCar(path.roads[0].bestLaneNum(), path, CAR_HEIGHT)

        for road in self.roads:
            road.update()
        for index, car in enumerate(self.cars):
            car.update()
            if car.done:
                self.avg_waiting_time = (self.avg_waiting_time*self.tot_car_cnt + car.end_time)/(self.tot_car_cnt+1)
                self.tot_car_cnt += 1
                self.cars.pop(index)
                self.n_exit_cars += 1
        for sig in self.signals:
            sig.update()

    def get_car_speed_std(self):
        spd_list = []
        for i, car in enumerate(self.cars):
            spd_list.append(car.speed)
        if len(spd_list) > 1:
            return statistics.stdev(spd_list)
        elif len(spd_list) == 1:
            return spd_list[0]
        else:
            return 0

    def makeAction(self, raw_action):
        ''' Make an action, change the traffic signals. '''

        for idx, master in enumerate(self.master_signals):
            action = Signals.RED if raw_action[idx] == 0 else Signals.GREEN
            master.change_signal(action)

    def calculateState(self):
        state = np.zeros((self.n_state), dtype=float)
        for i, road in enumerate(self.roads):
            state[i*STATE_EACH_ROAD+ 0] = road.get_queue()
        for j, signal in enumerate(self.signals):
            state[len(self.roads)*STATE_EACH_ROAD + j] = signal.light_timer if signal.signal == Signals.RED else 0
        return state

    def calculateReward(self):
        cur_avg_wait = self.get_cur_avg_wait()
        reward = self.prev_avg_wait - cur_avg_wait
        self.prev_avg_wait = cur_avg_wait
        return reward

    def get_cur_avg_wait(self):
        l = len(self.cars)
        if l == 0:
            return 0
        sum = 0
        for car in self.cars:
            sum += (self.timer - car.start_time)
        return sum/l

    def addIntersection(self, x : int, y : int, diam =20):
        add = Intersection(x, -y, diam)
        self.intersections.append(add)
        return add

    def addRoad(self, lane : int, op : bool, start : Intersection, end : Intersection, traffic_signal=None, spdLim : float = 60):
        lim = spdLim/3600*1000
        add = Road(self, lane, op, start, end, lim, traffic_signal=traffic_signal)
        add.number = len(self.roads)
        self.roads.append(add)
        return add

    def addPath(self, roads : List[Road]):
        add = Path(roads)
        self.paths.append(add)
        return add

    def addTrafficSignal(self, def_signal, is_master=False, master=None):
        add = Traffic_signal(def_signal, master=master)
        if is_master:
            self.master_signals.append(add)
        self.signals.append(add)
        return add

    def addCar(self, lane : int, path : Path, height : int, maxSpd=20.0):
        if lane == -1:
            self.n_fail_enter += 1
            return
        add = Car(self, lane, path, update_dur=UPDATE_DUR, maxSpd=maxSpd, scene=self.render_scene)
        self.cars.append(add)

    def update_render(self):
        for inte in self.intersections:
            inte.render(self.render_scene, self.scale)
        for road in self.roads:
            road.render(self.render_scene, self.scale)
        for car in self.cars:
            car.render(self.render_scene, self.scale)
        for ts in self.signals:
            ts.render(self.render_scene, self.scale)
        QApplication.processEvents()

    def clearCarItems(self):
        for car in self.cars:
            if car.graphicsItem != None:
                self.render_scene.removeItem(car.graphicsItem)
                car.graphicsItem = None
        for road in self.roads:
            road.initialize()