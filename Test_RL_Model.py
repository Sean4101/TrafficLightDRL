import numpy as np

class test_model():

    def __init__(self, action_space, observation_space):
        self.action_space = action_space
        self.observation_space = observation_space

        self.buffer = None

    def predict(self, state):
        ''' Returns a action based on given state. '''
        action = np.array([[1, 40]])
        return action

    def add_transition(transition):

        self.buffer = None
