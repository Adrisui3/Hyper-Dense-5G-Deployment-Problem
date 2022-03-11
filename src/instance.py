import numpy as np

class Instance:
    def __init__(self):
        self.size = None
        # id:[cost, range, power]
        self.cells = {}
        self.cells_ids = None
        self.macro_id = None
        self.nusers = None
        self.ncandidates = None
        self.dmatrix_users_candidates = None
        self.dmatrix_candidates = None
        self.init_macrocells = None
        self.user_locations = None
        self.candidate_locations = None

    def loadInstance(self, file, path):
        with open(path + file) as f:
            ds = f.readlines()
            line = 1

            # AoI dimensions
            self.size = float(ds[line])
            line += 2

            # Load cells' data
            ncells = int(ds[line])
            line += 2
            for _ in range(ncells):
                cdata = ds[line].split()
                self.cells[int(cdata[0])] = list(map(float, cdata[1:4]))
                line += 1
            
            self.cells_ids = list(self.cells.keys())
            self.macro_id = max(self.cells_ids)

            # Distance matrices
            line += 1
            self.nusers = int(ds[line])
            line += 2
            self.ncandidates = int(ds[line])
            
            self.dmatrix_users_candidates = [[] for _ in range(self.nusers)]
            self.dmatrix_candidates = [[] for _ in range(self.ncandidates)]
            line += 2
            for i in range(self.nusers):
                self.dmatrix_users_candidates[i] = list(map(float, ds[line].split()))
                line+=1

            line += 1
            for i in range(self.ncandidates):
                self.dmatrix_candidates[i] = list(map(float, ds[line].split()))
                line += 1
            
            # Initial deployment data
            line += 1
            self.init_macrocells = set(map(int, ds[line].split()))
            line += 2

            # Load user locations
            self.user_locations = []
            for _ in range(self.nusers):
                uloc = list(map(float, ds[line].split()))
                self.user_locations.append(tuple(uloc))
                line += 1
            
            # Load candidate locations
            line += 1
            self.candidate_locations = []
            for _ in range(self.ncandidates):
                cloc = list(map(float, ds[line].split()))
                self.candidate_locations.append(tuple(cloc))
                line += 1
    
    # If init is set to true, it will provide the default solution provided by the instance.
    # Otherwise, it will generate an empty solution
    def generateInitDeployment(self, init = True):
        return [0 if i not in self.init_macrocells else self.macro_id for i in range(self.ncandidates)] if init else [0 for _ in range(self.ncandidates)]


if __name__ == "__main__":
    ins = Instance()
    ins.loadInstance(file = "uniform/DS2")

    print(ins.generateInitDeployment())