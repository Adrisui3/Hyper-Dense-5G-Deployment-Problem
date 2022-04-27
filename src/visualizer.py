from deployment import Deployment
from instance import Instance
import matplotlib.pyplot as plt
import math
import random

class Visualizer:
    colors = {4:'blue', 3:'green', 2:'red', 1:'yellow'}
    
    def __init__(self, deployment = None, instance = None):
        self.deployment = deployment
        self.instance = instance

    def visualizeInstance(self):
        # Fix aspect ratio
        plt.gca().set_aspect('equal')
        
        # Plot polygon of interest
        x_p, y_p = self.instance.polygon.exterior.xy
        plt.plot(x_p, y_p)

        # Plot users
        for u in self.instance.user_locations:
            plt.plot(u[0], u[1], marker = "^", markersize = "5", color = "green")

        # If there is a deployment, plot it
        if self.deployment is None:
            for c in self.instance.candidate_locations:
                plt.plot(c[0], c[1], marker = "x", markersize = "10", color = "red")
        else:
            nnull_cells = [i for i in range(self.instance.ncandidates) if self.deployment[i] != 0]
            cell_loc = {key:[] for key in self.instance.cells.keys()}
            for ncell in nnull_cells:
                cell_loc[self.deployment[ncell]].append(ncell)
            
            for cell_id in cell_loc.keys():
                if not cell_loc[cell_id]:
                    continue
                
                radius = self.instance.cells[cell_id][1]
                locations = [self.instance.candidate_locations[idx] for idx in cell_loc[cell_id]]

                for c in locations:
                    circle = plt.Circle(xy = (c[0], c[1]), radius = radius, alpha = 0.5, color = self.colors[cell_id])
                    plt.gca().add_patch(circle)

        plt.show()