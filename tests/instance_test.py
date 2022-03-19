import sys
sys.path.insert(0, './src')
from instance import Instance


if __name__ == "__main__":
    ins = Instance()
    ins.loadInstance(file = "DS2_U", path = "data/uniform/")

    print(ins.generateInitDeployment())