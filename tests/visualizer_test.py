import sys
import os
sys.path.insert(0, './src')
from instance import Instance
from visualizer import Visualizer

if __name__ == "__main__":
    '''
    path_ds = "data/blobs/"
    #datasets = os.listdir(path_ds)
    #datasets.sort()
    datasets = ["DST_B"]
    
    for ds in datasets:
        ins = Instance()
        ins.loadInstance(file = ds, path = "data/blobs/")

        vis = Visualizer(instance = ins)
        vis.visualizeInstance()
    '''
    
    ins = Instance()
    ins.loadInstance(file = "DS1_U", path = "data/uniform/")
    found_sol = [1, 1, 0, 1, 4, 1, 4, 1, 1, 1, 1, 1, 4, 0, 1, 1, 2, 4, 4, 2, 4, 1, 4, 4, 2, 1, 0, 1, 2, 1, 1, 1, 0, 0, 1, 1, 1, 2, 1, 1, 0, 1, 4, 1, 2, 1, 1, 1, 2, 0]
    vis = Visualizer(instance = ins, deployment = found_sol)
    vis.visualizeInstance()