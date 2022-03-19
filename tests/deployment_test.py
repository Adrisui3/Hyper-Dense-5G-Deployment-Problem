import sys
import os
sys.path.insert(0, './src')
from instance import Instance
from deployment import Deployment

if __name__ == "__main__":
    path_ds = "data/uniform/"
    datasets = os.listdir(path_ds)
    datasets.sort()
    init = True
    
    for ds in datasets:
        print(" --- DATASET", ds, "---")
        ins = Instance()
        ins.loadInstance(file = ds, path = path_ds)
        sol = Deployment(instance = ins, init = init)
        sol.test()