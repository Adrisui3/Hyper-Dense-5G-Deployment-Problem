from deployment import Deployment
from instance import Instance
from instance_generator import InstanceGenerator
import matplotlib.pyplot as plt

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

        if self.deployment:
            nnull_cells = [idx for idx in range(self.instance.ncandidates) if self.deployment[idx] != 0]
            for cell in self.instance.cells_ids:
                indices = [idx for idx in nnull_cells if self.deployment[idx] == cell]
                if not indices:
                    continue
                reach = self.instance.cells[cell][1]
                x_d = [candidates[idx][0] for idx in indices]
                y_d = [candidates[idx][1] for idx in indices]
                plt.scatter(x_d, y_d, s = reach * 1000, alpha = 0.3)

        plt.scatter(x = x_u, y = y_u, s=5, c = 'blue')
        plt.scatter(x = x_c, y = y_c, s=7, marker='^', c = "red")
        plt.show()