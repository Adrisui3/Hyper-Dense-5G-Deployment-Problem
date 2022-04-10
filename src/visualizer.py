from deployment import Deployment
from instance import Instance
import matplotlib.pyplot as plt

class Visualizer:
    def __init__(self, deployment = None, instance = None):
        self.deployment = deployment
        self.instance = instance

    def visualizeInstance(self):
        # Plot polygon of interest
        x_p, y_p = self.instance.polygon.exterior.xy
        plt.plot(x_p, y_p)

        for u in self.instance.user_locations:
            plt.plot(u[0], u[1], marker = "^", markersize = "5", color = "green")

        if self.deployment is None:
            for c in self.instance.candidate_locations:
                plt.plot(c[0], c[1], marker = "x", markersize = "10", color = "red")

        plt.show()