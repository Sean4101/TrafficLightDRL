import tkinter as tk
import Traffic_Simulator

class TrafficSimulatorEnvironment(object):
    def __init__(self):
        self.window = Traffic_Simulator.Ui_MainWindow
        self.window.title('Traffic Simulator Environment')
        self.window.geometry('800x600')
        self.window.configure(background='gray')

        top_frame = tk.Frame(self.window)
        top_frame.pack(side=tk.TOP)
        bottom_frame = tk.Frame(self.window)
        bottom_frame.pack(side=tk.BOTTOM)

        left_button = tk.Button(top_frame, text='Red', fg='red')

        left_button.pack(side=tk.LEFT)

        middle_button = tk.Button(top_frame, text='Green', fg='green')
        middle_button.pack(side=tk.LEFT)

        right_button = tk.Button(top_frame, text='Blue', fg='blue')
        right_button.pack(side=tk.LEFT)


        bottom_button = tk.Button(bottom_frame, text='Black', fg='black', command=self.hello)

        bottom_button.pack(side=tk.BOTTOM)

    def loop(self):
        self.window.mainloop()
    
    def hello(self):
        print('hello')

env = TrafficSimulatorEnvironment()
env.loop()