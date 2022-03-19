import sys
sys.path.insert(0, './src')
from operators import *


if __name__ == "__main__":
    ins = Instance()
    ins.loadInstance(file = "DS1_U", path = "data/uniform/")

    sol = Deployment(instance = ins)
    print(sol)
    print(upgradeCells(sol))
    print(downgradeCells(sol))
    print(swapCells(sol))
    print(deployConnected(sol))
    print(deployMacrocell(sol))