from deployment import Deployment
from instance import Instance
from instance_generator import InstanceGenerator
import matplotlib.pyplot as plt
import os

class Visualizer:
    def __init__(self, deployment = None, instance = None):
        self.deployment = deployment
        self.instance = instance

    def visualizeInstance(self):
        users = self.instance.user_locations
        candidates = self.instance.candidate_locations

        x_u = [user[0] for user in users]
        y_u = [user[1] for user in users]

        x_c = [candidate[0] for candidate in candidates]
        y_c = [candidate[1] for candidate in candidates]

        nnull_cells = [idx for idx in self.instance.ncandidates if self.deployment[idx] != 0]
        for cell in self.instance.cells_ids:
            indices = [idx for idx in nnull_cells if self.deployment[idx] == cell]
            if not indices:
                continue
            reach = self.instance.cells[cell][1]
            x_d = [candidates[idx][0] for idx in indices]
            y_d = [candidates[idx][1] for idx in indices]
            plt.scatter(x_d, y_d, s = reach * 1000, alpha = 0.3)

        plt.scatter(x = x_u, y = y_u, s=5, c = 'blue')
        plt.scatter(x = x_c, y = y_c, s=7, marker='^')
        plt.show()

if __name__ == "__main__":
    '''
    path_ds = "data/blobs/"
    datasets = os.listdir(path_ds)
    datasets.sort()
    
    for ds in datasets:
        ins = Instance()
        ins.loadInstance(file = ds, path = "data/blobs/")

        vis = Visualizer(instance = ins)
        vis.visualizeInstance()
    '''
    ins = Instance()
    ins.loadInstance(file = "DS8_U", path = "data/uniform/")
    found_sol = [0, 4, 2, 3, 0, 4, 0, 3, 2, 0, 2, 1, 1, 1, 1, 4, 4, 0, 4, 4, 1, 1, 0, 1, 2, 2, 3, 2, 4, 0, 1, 4, 0, 3, 0, 4, 1, 1, 4, 2, 1, 1, 0, 0, 0, 1, 0, 2, 1, 0, 2, 4, 0, 3, 4, 3, 0, 4, 4, 0, 3, 0, 2, 3, 1, 4, 4, 2, 4, 4, 0, 2, 4, 1, 2, 1, 4, 2, 2, 4, 2, 1, 1, 4, 4, 0, 4, 2, 2, 4, 4, 2, 4, 3, 4, 1, 3, 1, 1, 3, 2, 2, 4, 4, 3, 3, 2, 1, 4, 1, 0, 0, 2, 3, 1, 4, 3, 1, 2, 4, 0, 1, 4, 3, 0, 1, 0, 4, 1, 2, 4, 1, 1, 4, 3, 0, 3, 4, 0, 3, 0, 2, 2, 2, 0, 2, 0, 0, 0, 2, 3, 1, 4, 0, 0, 4, 1, 2, 0, 3, 0, 3, 1, 3, 0, 1, 4, 4, 4, 1, 0, 1, 0, 3, 2, 1, 0, 0, 4, 1, 3, 4, 4, 1, 2, 4, 2, 1, 4, 1, 0, 0, 0, 1, 0, 4, 0, 2, 4, 0, 1, 2, 1, 4, 3, 2, 1, 1, 1, 4, 0, 3, 4, 4, 2, 3, 0, 4, 4, 0, 4, 0, 2, 2, 1, 1, 3, 1, 0, 1, 2, 0, 0, 4, 4, 3, 1, 0, 0, 4, 0, 0, 0, 1, 0, 3, 4, 3, 0, 1, 4, 0, 1, 0, 4, 1, 3, 2, 3, 4, 3, 0, 3, 3, 0, 0, 1, 0, 0, 4, 2, 2, 0, 1, 0, 4, 0, 0, 1, 0, 0, 2, 2, 1, 0, 3, 4, 2, 4, 2, 2, 0, 4, 2, 4, 2, 1, 4, 0, 4]
    vis = Visualizer(instance = ins, deployment = found_sol)
    vis.visualizeInstance()