from deployment import Deployment
from instance import Instance
import matplotlib.pyplot as plt
import numpy as np

class Visualizer:
    
    # This is a workaround
    colors = {0:'blue', 1:'green', 2:'red', 3:'cyan', 4:'magenta', 5:'yellow'}
    
    # Precomputed scale for KML instances, also a workaround
    SCALE = 0.01425

    def draw(self, instance = None, deployment = None):      
        # Fix aspect ratio
        plt.gca().set_aspect('equal')
        
        #Set title
        plt.title(instance.name)
        
        # Plot polygon of interest
        x_p, y_p = instance.polygon.exterior.xy
        plt.plot(x_p, y_p)

        # Plot users
        for u in instance.user_locations:
            plt.plot(u[0], u[1], marker = "^", markersize = "5", color = "green")
        
        # If there is no deployment, plot candidate locations
        if deployment is None:
            for c in instance.candidate_locations:
                plt.plot(c[0], c[1], marker = "x", markersize = "10", color = "red")
        
        # If there is a deployment, plot cells
        else:
            nnull_cells = [i for i in range(instance.ncandidates) if deployment[i] != 0]
            cell_loc = {key:[] for key in instance.cells.keys()}
            for ncell in nnull_cells:
                cell_loc[deployment[ncell]].append(ncell)
            
            for cell_id in cell_loc.keys():
                if not cell_loc[cell_id]:
                    continue
                
                # If it is a KML instance, apply the scale
                radius = instance.cells[cell_id][1] * self.SCALE if instance.name.endswith(".kml") else instance.cells[cell_id][1]
                locations = [instance.candidate_locations[idx] for idx in cell_loc[cell_id]]

                for c in locations:
                    circle = plt.Circle(xy = (c[0], c[1]), radius = radius, alpha = 0.5, color = self.colors[cell_id % len(self.colors)])
                    plt.gca().add_patch(circle)

        plt.show()