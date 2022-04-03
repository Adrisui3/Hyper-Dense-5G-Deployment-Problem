import numpy as np
import kmlParser
import shapely

class Instance:
    def __init__(self):
        
        self.polygon = None
        
        # id:[cost, range, power]
        self.cells = {}
        self.cells_ids = None
        self.macro_id = None
        self.init_deployment = None
        
        # For each cell, set of indices where it can be installed
        # id:set(compatible_locations)
        self.cell_compatibility = None
        
        # Number of users and candidate locations
        self.nusers = None
        self.ncandidates = None
        
        # Distance matrices
        self.dmatrix_users_candidates = None
        self.dmatrix_candidates = None

        # Coordinates
        self.user_locations = None
        self.candidate_locations = None

    def loadInstance(self, file, path):
        with open(path + file) as f:
            ds = f.readlines()
            line = 1

            # AoI
            self.polygon = float(ds[line])
            #self.polygon = shapely.wkt.loads(ds[line])
            line += 2

            # Load cells' data
            ncells = int(ds[line])
            line += 2
            for _ in range(ncells):
                cdata = ds[line].split()
                self.cells[int(cdata[0])] = list(map(float, cdata[1:4]))
                line += 1
            
            self.cells_ids = list(self.cells.keys())
            # Macrocells are encoded as the biggest id
            self.macro_id = max(self.cells_ids)

            # Number of users and candidates
            line += 1
            self.nusers = int(ds[line])
            line += 2
            self.ncandidates = int(ds[line])
            line += 2

            # List of compatible indices per cell kind
            self.cell_compatibility = {}
            for _ in range(ncells):
                compat_data = list(map(int, ds[line].split()))
                idx = compat_data[0]
                compat_data.pop(0)
                self.cell_compatibility[idx] = set(compat_data)
                line += 1

            # Distance matrices
            self.dmatrix_users_candidates = [[] for _ in range(self.nusers)]
            self.dmatrix_candidates = [[] for _ in range(self.ncandidates)]
            line += 1
            for i in range(self.nusers):
                self.dmatrix_users_candidates[i] = list(map(float, ds[line].split()))
                line+=1

            line += 1
            for i in range(self.ncandidates):
                self.dmatrix_candidates[i] = list(map(float, ds[line].split()))
                line += 1
            
            # Initial deployment data
            line += 1
            iDeployment_line = ds[line]
            self.init_deployment = [0 for _ in range(self.ncandidates)]
            if len(iDeployment_line) > 0:
                init_macrocells = list(map(int, iDeployment_line.split()))
                for idx in init_macrocells:
                    self.init_deployment[idx] = self.macro_id
            
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
    
    # If init is set to true, it will build the default solution provided by the instance.
    # Otherwise, it will generate an empty solution
    def getInitDeployment(self, init = True):
        return self.init_deployment if init else [0 for _ in range(self.ncandidates)]