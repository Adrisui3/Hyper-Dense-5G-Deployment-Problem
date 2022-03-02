import numpy as np

class Instance:
    def __init__(self):
        self.length = None
        self.width = None
        self.cells = {}
        self.cells_ids = None
        self.nusers = None
        self.ncandidates = None
        self.dmatrix_users_candidates = None
        self.dmatrix_candidates = None
        self.init_macrocells = None

        #If visualization enabled
        self.user_locations = None
        self.candidate_locations = None

    def loadInstance(self, file, visualization, path="data/"):
        with open(path + file) as f:
            ds = f.readlines()
            line = 1

            # AoI dimensions
            size = list(map(float, ds[line].split()))
            self.length, self.width = size[0], size[1]
            line += 2

            # Load cells' data
            ncells = int(ds[line])
            line += 2
            for _ in range(ncells):
                cdata = ds[line].split()
                self.cells[int(cdata[0])] = list(map(float, cdata[1:4]))
                line += 1
            
            self.cells_ids = list(self.cells.keys())

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

        # If visualization options are enabled    
        if visualization:
            with open(path + file + "_coordinates") as f:
                line = 1
                ds_c = f.readlines()

                # Load user locations
                self.user_locations = []
                for _ in range(self.nusers):
                    uloc = list(map(float, ds_c[line].split()))
                    self.user_locations.append(tuple(uloc))
                    line += 1
                
                # Load candidate locations
                line += 1
                self.candidate_locations = []
                for _ in range(self.ncandidates):
                    cloc = list(map(float, ds_c[line].split()))
                    self.candidate_locations.append(tuple(cloc))
                    line += 1
    
    def generateInitDeployment(self):
        # I assume maximum id corresponds to macrocells
        macro_id = max(self.cells_ids)
        return [0 if i not in self.init_macrocells else macro_id for i in range(self.ncandidates)]

if __name__ == "__main__":
    ins = Instance()
    ins.loadInstance(file = "DS1", visualization = True)

    print(ins.generateInitDeployment())