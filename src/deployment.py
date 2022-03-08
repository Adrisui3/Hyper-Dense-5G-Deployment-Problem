from instance import Instance
import copy
import os


class Deployment:
    def __init__(self, instance, max_cost = None, max_interferences = None, weights = (1, 1, 1), deployment = None):
        self.__instance = instance
        self.__deployment = deployment if deployment is not None else self.__instance.generateInitDeployment()
        self.__wcoverage = weights[0]        
        self.__wcost = weights[1]
        self.__winterferences = weights[2]

        # Compute maximum cost and maximum interferences
        self.__max_cost = self.__instance.cells[self.__instance.macro_id][0] * self.__instance.ncandidates if max_cost is None else max_cost
        if max_interferences is None:
            aux_dep = [self.__instance.macro_id]*self.__instance.ncandidates
            self.__max_interferences = self.__interferencesHelper(aux_dep, self.__coveredUsersHelper(aux_dep))
        else:
            self.__max_interferences = max_interferences

    def __getitem__(self, index):
        return self.__deployment[index]
    
    def __setitem__(self, index, item):
        self.__deployment[index] = item
    
    def __delitem__(self, index):
        del self.__deployment[index]
    
    def __len__(self):
        return len(self.__deployment)
    
    def __str__(self):
        return str(self.__deployment)

    def instance(self):
        return self.__instance
    
    def __coveredUsersHelper(self, deployment):
        covered_users = set()
        for i in range(self.__instance.nusers):
            user_dist = self.__instance.dmatrix_users_candidates[i]
            for j in range(self.__instance.ncandidates):
                if deployment[j] == 0:
                    continue
                
                # If covered, go for the next user
                if user_dist[j] <= self.__instance.cells[deployment[j]][1]:
                    covered_users.add(i)
                    break

        return covered_users
    
    def copy(self):
        return Deployment(instance = self.__instance, max_cost = self.__max_cost, 
                          max_interferences = self.__max_interferences, weights = self.weights(), 
                          deployment = self.__deployment.copy())

    def coveredUsers(self):        
        return self.__coveredUsersHelper(self.__deployment)

    def cost(self):
        cost = 0
        for cell in self.__deployment:
            if cell == 0:
                continue
            cost += self.__instance.cells[cell][0]
        
        return cost

    # Both coverage and interferences need the set of covered users
    # It can be sent as a parameter to prevent wasting time computing it twice
    def coverage(self, nusers_covered = None):
        if nusers_covered is None:
            return len(self.coveredUsers()) / self.__instance.nusers
        else:
            return nusers_covered / self.__instance.nusers
    
    def __interferencesHelper(self, deployment, cusers):
        interferences = 0
        for user in cusers:
            isum, pmax, dmax = 0, 0, []
            for i in range(self.__instance.ncandidates):
                if deployment[i] == 0:
                    continue
                
                if self.__instance.dmatrix_users_candidates[user][i] <= self.__instance.cells[deployment[i]][1]:
                    dist = self.__instance.dmatrix_users_candidates[user][i]
                    power = self.__instance.cells[deployment[i]][2]
                    isum += power / pow(dist, 2)
                    
                    # I assume pmax and dmax correspond to the closest most powerful cell whose signal reaches the user
                    if power > pmax:
                        pmax = power
                        dmax = [dist]

                    elif power == pmax:
                        dmax.append(dist)
            
            interferences += isum - pmax / pow(min(dmax), 2)
        
        return interferences

    def interferences(self, cusers = None):
        covered_users = self.coveredUsers() if cusers is None else cusers
        return self.__interferencesHelper(self.__deployment, covered_users)

    def isFeasible(self):
        # Non-null cell indices for the __deployment array
        nncells_idx = [i for i in range(self.__instance.ncandidates) if self.__deployment[i] != 0]
        # For every non-null cell, true if connected, false if not.
        # Initially, all macrocells are connected. The aim is to find if the others are.
        connected_cells = [True if self.__deployment[idx] == self.__instance.macro_id else False for idx in nncells_idx]
        
        for i in range(len(nncells_idx)):
            if connected_cells[i]:
                continue

            for j in range(len(nncells_idx)):
                if i == j:
                    continue
                
                # If j-th cell is connected, bigger than i-th cell and has i-th cell inside its range, then i-th cell is connected too
                isBigger = self.__deployment[nncells_idx[i]] < self.__deployment[nncells_idx[j]]
                inRange = self.__instance.dmatrix_candidates[nncells_idx[j]][nncells_idx[i]] <= self.__instance.cells[self.__deployment[nncells_idx[j]]][1]
                connected_cells[i] = connected_cells[j] and isBigger and inRange

                if connected_cells[i]:
                    break
        
        # If all non-null cells are connected, the solution is feasible
        return all(connected_cells)

    def weights(self):
        return (self.__wcoverage, self.__wcost, self.__winterferences)

    # Python tuples are immutable, so they can be used as keys for dictionaries. 
    # This can be helpful when implementing memoization/TABU search features
    def deployment(self):
        return self.__deployment
    
    def immutableDeployment(self):
        return tuple(self.__deployment)

    def splitObjective(self):
        covered_users = self.coveredUsers()
        return (self.coverage(len(covered_users)), self.cost(), self.interferences(covered_users))

    def objective(self):
        obj = self.splitObjective()
        
        ncost = (self.__max_cost - obj[1]) / self.__max_cost
        ninterferences = (self.__max_interferences - obj[2]) / self.__max_interferences if self.__max_interferences > 0 else 1
        
        return self.__wcoverage * obj[0] + self.__wcost * ncost + self.__winterferences * ninterferences
    
    def getNonNullCells(self):
        return [i for i in range(self.__instance.ncandidates) if self.__deployment[i] != 0]

    def test(self):
        print(" --- DEBUG ---")
        print("Cost: ", self.cost())
        print("Max cost", self.__max_cost)
        print("Coverage: ", self.coverage())
        print("Interferences: ", self.interferences())
        print("Max interferences: ", self.__max_interferences)
        print("Objective: ", self.objective())
        print("Feasible: ", self.isFeasible())

    

if __name__ == "__main__":
    path_ds = "./data/"
    ds_r = os.listdir(path_ds)
    datasets = [name for name in ds_r if "_coordinates" not in name]
    datasets.sort()
    
    for ds in datasets:
        ins = Instance()
        ins.loadInstance(file = ds, visualization = True)
        sol = Deployment(instance = ins)
        sol.test()