

class Traffic_Simulator_Env():

    def __init__(self):
        self.intersections = {}
        self.roads = set()
        self.paths = []

        self.buildEnv()
        print(self.intersections)
        print(self.roads)
        print(self.paths)

    def buildEnv(self):
        self.addIntersection("a", 0, 0)
        self.addIntersection("b", 400, 0)
        self.addIntersection("c", 400, 400)

        self.addRoad("a", "b")
        self.addRoad("b", "a")
        self.addRoad("b", "c")
        self.addRoad("c", "b")

        self.addPath([("a", "b"), ("b", "c"), ("c", "b"), ("b", "a")])

    def addIntersection(self, name, xPos, yPos):
        self.intersections.update({name :(xPos, yPos)})

    def addRoad(self, start, end):
        miss = False
        if start not in self.intersections:
            print("Intersection {} missing!".format(start))
            miss = True
        if end not in self.intersections:
            print("Intersection {} missing!".format(end))
            miss = True
        if miss:
            return
        name = start + " to " + end
        self.roads.add((start, end))

    def addPath(self, path):
        miss = False
        for i in range(len(path)):
            if path[i] not in self.roads:
                print("Road {} missing!".format(path[0]))
                miss = True
        if miss:
            return
        self.paths.append(path)


bruh = Traffic_Simulator_Env()