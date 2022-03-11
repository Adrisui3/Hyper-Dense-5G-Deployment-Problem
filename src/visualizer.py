from deployment import Deployment
from instance import Instance
from instance_generator import InstanceGenerator
import matplotlib.pyplot as plt
import os

class Visulizer:
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

        plt.scatter(x = x_u, y = y_u, s=5)
        plt.scatter(x = x_c, y = y_c, s=7, marker='^')
        plt.show()

if __name__ == "__main__":
    path_ds = "data/blobs/"
    datasets = os.listdir(path_ds)
    datasets.sort()
    
    for ds in datasets:
        ins = Instance()
        ins.loadInstance(file = ds, path = "data/blobs/")

        vis = Visulizer(instance = ins)
        vis.visualizeInstance()