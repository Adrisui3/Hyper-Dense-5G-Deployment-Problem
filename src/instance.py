import numpy as np
from kmlParser import KMLParser
import shapely.wkt

class Instance:
    def __init__(self, polygon = None, cells = {}, cells_ids = None, macro_id = None, init_deployment = None, 
                cell_compatibility = None, nusers = None, ncandidates = None, dmatrix_users_candidates = None, 
                dmatrix_candidates = None, user_locations = None, candidate_locations = None, name = None):
        
        # Area of interest
        self.polygon = polygon
        
        # id:[cost, range, power]
        self.cells = cells
        self.cells_ids = cells_ids
        self.macro_id = macro_id
        self.init_deployment = init_deployment
        
        # For each cell, set of indices where it can be installed
        # id:set(compatible_locations)
        self.cell_compatibility = cell_compatibility
        
        # Number of users and candidate locations
        self.nusers = nusers
        self.ncandidates = ncandidates
        
        # Distance matrices
        self.dmatrix_users_candidates = dmatrix_users_candidates
        self.dmatrix_candidates = dmatrix_candidates

        # Coordinates
        self.user_locations = user_locations
        self.candidate_locations = candidate_locations

        # Name of the instance
        self.name = name

    def __loadFile(self, file, path):
        with open(path + file) as f:
            ds = f.readlines()
            line = 1

            # AoI
            self.polygon = shapely.wkt.loads(ds[line])
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
    
    def __loadKML(self, file, path):
        kml = KMLParser().loadKML(path = path, file = file)
        
        self.polygon = kml["polygon"]
        self.cells = kml["cells"]
        self.cells_ids = kml["cells_ids"]
        self.macro_id = kml["macro_id"]
        self.init_deployment = kml["init_deployment"]
        self.cell_compatibility = kml["cell_compatibility"]
        self.nusers = kml["nusers"]
        self.ncandidates = kml["ncandidates"]
        self.dmatrix_users_candidates = kml["dmatrix_users_candidates"]
        self.dmatrix_candidates = kml["dmatrix_candidates"]
        self.user_locations = kml["user_locations"]
        self.candidate_locations = kml["candidate_locations"]
    
    def loadInstance(self, file, path):
        self.name = file
        if file.endswith(".kml"):
            self.__loadKML(file = file, path = path)
        else:
            self.__loadFile(file = file, path = path)

    # If init is set to true, it will build the default solution provided by the instance.
    # Otherwise, it will generate an empty solution
    def getInitDeployment(self, init = True):
        return self.init_deployment if init else [0 for _ in range(self.ncandidates)]