import random
import numpy as np


class InstanceGenerator:
    
    # Data related to cells is fixed for now, and it comes from the same paper as the model
    # [id, cost, range, power]
    cells = [[4, 175, 25, 50], [3, 25, 10, 10], [2, 5, 0.5, 1], [1, 1, 0.05, 0.25]]

    # If not specified, locations will be uniformly distributed over the AoI
    def __init__(self, length, width, nusers, ncandidates, distrib = random.uniform):
        self.length = length
        self.width = width
        self.nusers = nusers
        self.ncandidates = ncandidates
        self.distrib = distrib
    
    def __euclidean_distance(self, A, B):
        return np.sqrt(pow(A[0] - B[0], 2) + pow(B[1] - A[1], 2))

    def generate(self, name, path = "data/"):
        candidate_locations = []
        user_locations = []
        
        # Actual locations of the users and/or candidates is not relevant
        dmatrix_users_candidates = [[] for _ in range(self.nusers)]
        # Distances between cells is necessary to grant feasibility
        dmatrix_candidates = [[] for _ in range(self.ncandidates)]

        with open(path + name, "w") as f:
            print("# Site size (km)", file = f)
            print(self.length, " ", self.width, file = f)
            
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
            for i in range(self.nusers):
                user_locations.append((self.distrib(0, self.length), self.distrib(0, self.width)))
            
            for i in range(self.ncandidates):
                candidate_locations.append((self.distrib(0, self.length), self.distrib(0, self.width)))
            
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



if __name__ == "__main__":
    gen = InstanceGenerator(100, 100, 10, 4)
    gen.generate("test1")


    