import random
import numpy as np
import math
from sklearn.datasets import make_blobs

# Instance generator for the Hyper-Dense Deployment Problem.

class InstanceGenerator:
    
    # Data related to cells is fixed for now, and it comes from the same paper as the model
    # [id, cost, range, power]
    cells = [[4, 175, 25, 50], [3, 25, 10, 10], [2, 5, 0.5, 1], [1, 1, 0.05, 0.25]]

    # If not specified, locations will be uniformly distributed over the AoI
    def __init__(self, size, nusers, ncandidates, distrib = random.uniform):
        self.size = size
        self.nusers = nusers
        self.ncandidates = ncandidates
        self.distrib = distrib
    
    def __euclidean_distance(self, A, B):
        return np.sqrt(pow(A[0] - B[0], 2) + pow(B[1] - A[1], 2))

    def __generateBlobs(self, cluster_std, centers):        
        users_r, _ = make_blobs(n_samples = self.nusers, n_features = 2, cluster_std = cluster_std, center_box=(0, self.size), centers = centers)
        users = []
        for user in users_r:
            x = abs(user[0]) if user[0] <= self.size else self.size
            y = abs(user[1]) if user[1] <= self.size else self.size
            users.append((x, y))

        return users

    def generateInstance(self, file, blobs = False, path = "data/", cluster_std = None, centers = None):
        candidate_locations = []
        deployed_macros = []
        user_locations = []
        
        # Actual locations of the users and/or candidates is not relevant
        dmatrix_users_candidates = [[] for _ in range(self.nusers)]
        # Distances between cells is necessary to grant feasibility
        dmatrix_candidates = [[] for _ in range(self.ncandidates)]

        kind = "uniform/" if not blobs else "blobs/"
        with open(path + kind + file, "w") as f:
            print("# Site size (km)", file = f)
            print(self.size, file = f)
            
            print("# Number of cells", file = f)
            print(len(self.cells), file = f)

            print("# For every kind of cell: id, cost, range, power", file = f)
            for cell in self.cells:
                print(' '.join(map(str, cell)), file = f)
                
            print("# Number of users", file = f)
            print(self.nusers, file = f)

            print("# Number of candidate locations", file = f)
            print(self.ncandidates, file = f)

            # Random generation of locations for both users and candidate points
            if not blobs:
                for i in range(self.nusers):
                    user_locations.append((self.distrib(0, self.size), self.distrib(0, self.size)))
            else:
                user_locations = self.__generateBlobs(cluster_std, centers)
            
            for i in range(self.ncandidates):
                candidate_locations.append((self.distrib(0, self.size), self.distrib(0, self.size)))
            
            # nusers x ncandidates distance matrix
            print("# Distance matrix between users and candidate locations", file = f)
            for i in range(self.nusers):
                for j in range(self.ncandidates):
                    dist = self.__euclidean_distance(user_locations[i], candidate_locations[j])
                    dmatrix_users_candidates[i].append(dist)
                print(' '.join(map(str, dmatrix_users_candidates[i])), file = f)
            
            # ncandidates x ncandidates distance matrix
            print("# Distance matrix between candidate locations", file = f)
            for i in range(self.ncandidates):
                for j in range(self.ncandidates):
                    dist = 0 if i == j else self.__euclidean_distance(candidate_locations[i], candidate_locations[j])
                    dmatrix_candidates[i].append(dist)
                print(' '.join(map(str, dmatrix_candidates[i])), file = f)

            # Random deployment of macrocells emulating a 4G network
            # Between 5-7% of candidate locations will have a macrocell
            perc = random.uniform(0.05, 0.07)
            deployed_macros = random.sample(range(self.ncandidates), math.ceil(self.ncandidates*perc))
            print("# Candidate locations' indices where macrocells are deployed", file = f)
            print(' '.join(map(str, deployed_macros)), file = f)
            
            # Both users and candidates coordinates
            print("# User's coordinates", file = f)
            for i in range(self.nusers):
                print(user_locations[i][0], user_locations[i][1], file = f)
            
            print("# Candidate locations coordinates", file = f)
            for j in range(self.ncandidates):
                print(candidate_locations[j][0], candidate_locations[j][1], file = f)



if __name__ == "__main__":
    '''
    # UNIFORM INSTANCES #

    # Small instances
    gen = InstanceGenerator(size = 100, nusers = 1000, ncandidates = 50)
    gen.generateInstance(file = "DS1_U")

    gen = InstanceGenerator(size = 100, nusers = 1000, ncandidates = 100)
    gen.generateInstance(file = "DS2_U")

    gen = InstanceGenerator(size = 100, nusers = 2000, ncandidates = 100)
    gen.generateInstance(file = "DS3_U")

    # Medium instances
    gen = InstanceGenerator(size = 200, nusers = 2000, ncandidates = 100)
    gen.generateInstance(file = "DS4_U")

    gen = InstanceGenerator(size = 200, nusers = 2000, ncandidates = 200)
    gen.generateInstance(file = "DS5_U")

    gen = InstanceGenerator(size = 200, nusers = 4000, ncandidates = 200)
    gen.generateInstance(file = "DS6_U")
    
    # Big instances
    gen = InstanceGenerator(size = 300, nusers = 4000, ncandidates = 200)
    gen.generateInstance(file = "DS7_U")
    
    gen = InstanceGenerator(size = 300, nusers = 4000, ncandidates = 300)
    gen.generateInstance(file = "DS8_U")
    '''
    
    '''
    # BLOB INSTANCES #
    
    # Small instances
    gen = InstanceGenerator(size = 100, nusers = 1000, ncandidates = 50)
    gen.generateInstance(file = "DS1_B", blobs = True, cluster_std = 5.0)

    gen = InstanceGenerator(size = 100, nusers = 1000, ncandidates = 100)
    gen.generateInstance(file = "DS2_B", blobs = True, cluster_std = 5.0)

    gen = InstanceGenerator(size = 100, nusers = 2000, ncandidates = 100)
    gen.generateInstance(file = "DS3_B", blobs = True, cluster_std = 7.0)

    # Medium instances
    gen = InstanceGenerator(size = 200, nusers = 2000, ncandidates = 100)
    gen.generateInstance(file = "DS4_B", blobs = True, cluster_std =  10.0)

    gen = InstanceGenerator(size = 200, nusers = 2000, ncandidates = 200)
    gen.generateInstance(file = "DS5_B", blobs = True, cluster_std = 10.0)

    gen = InstanceGenerator(size = 200, nusers = 4000, ncandidates = 200)
    gen.generateInstance(file = "DS6_B", blobs = True, cluster_std = 10.0)
    
    # Big instances
    gen = InstanceGenerator(size = 300, nusers = 4000, ncandidates = 200)
    gen.generateInstance(file = "DS7_B", blobs = True, cluster_std = 15.0)
    
    gen = InstanceGenerator(size = 300, nusers = 4000, ncandidates = 300)
    gen.generateInstance(file = "DS8_B", blobs = True, cluster_std = 15.0)
    '''