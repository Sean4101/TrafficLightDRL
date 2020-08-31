from Traffic_Simulator_Environment import Traffic_Simulator_Env
from Traffic_Simulator_Widget import mainWidget


class Traffic_Simulator():

    def __init__(self):
        self.env = Traffic_Simulator_Env()
        self.widget = mainWidget()