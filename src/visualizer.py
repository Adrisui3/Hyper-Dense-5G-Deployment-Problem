from deployment import Deployment
from instance import Instance
import matplotlib.pyplot as plt
import math

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
        else:
            nnull_cells = [i for i in range(self.instance.ncandidates) if self.deployment[i] != 0]
            cell_loc = {key:[] for key in self.instance.cells.keys()}
            for ncell in nnull_cells:
                cell_loc[self.deployment[ncell]].append(ncell)
            
            for cell_id in cell_loc.keys():
                if not cell_loc[cell_id]:
                    continue
                
                radius = self.instance.cells[cell_id][1]
                positions_x = [self.instance.candidate_locations[idx][0] for idx in cell_loc[cell_id]]
                positions_y = [self.instance.candidate_locations[idx][1] for idx in cell_loc[cell_id]]

                plt.scatter(x = positions_x, y = positions_y, s = (2*radius)**2, alpha = 0.5)



        plt.show()