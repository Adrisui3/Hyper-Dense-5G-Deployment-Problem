from instance import Instance
import copy


class Deployment:
    def __init__(self, instance, max_cost = None, max_interferences = None, weights = (1, 1, 1), deployment = None, init = True):
        self.__instance = instance
        self.__deployment = deployment if deployment is not None else self.__instance.getInitDeployment(init = init)
        self.__wcoverage = weights[0]        
        self.__wcost = weights[1]
        self.__winterferences = weights[2]

        # Compute maximum cost and maximum interferences
        if max_interferences is None and max_cost is None:
            max_deployment = self.__getMaxDeployment()
            self.__max_interferences = self.__interferencesHelper(max_deployment, self.__coveredUsersHelper(max_deployment))
            self.__max_cost = self.__costHelper(max_deployment)
        else:
            self.__max_interferences = max_interferences
            self.__max_cost = max_cost

    def __getitem__(self, index):
        return self.__deployment[index]
    
    def __setitem__(self, index, item):
        self.__deployment[index] = item
    
    def __delitem__(self, index):
        del self.__deployment[index]
    
    def __len__(self):
        return self.__instance.ncandidates
    
    def __str__(self):
        return str(self.__deployment)

    # I define maximum deployment as the deployment for which each location has the biggest compatible cell installed
    # This is the most expensive with the most interferences solution for an instance
    def __getMaxDeployment(self):
        max_depl = [[0] for _ in range(self.__instance.ncandidates)]
        for idx in range(self.__instance.ncandidates):
            for cell in self.__instance.cells_ids:
                if idx in self.__instance.cell_compatibility[cell]:
                    max_depl[idx].append(cell)
        
        return [max(compatible) for compatible in max_depl]

    def instance(self):
        return self.__instance
    
    def __coveredUsersHelper(self, deployment):
        covered_users = set()
        nnull_idx = [i for i in range(self.__instance.ncandidates) if deployment[i] != 0]
        for i in range(self.__instance.nusers):
            user_dist = self.__instance.dmatrix_users_candidates[i]
            for j in nnull_idx:
                # If covered, go for the next user
                if user_dist[j] <= self.__instance.cells[deployment[j]][1]:
                    covered_users.add(i)
                    break

        return covered_users
    
    def __costHelper(self, deployment):
        cost = 0
        for cell in deployment:
            if cell == 0:
                continue
            cost += self.__instance.cells[cell][0]
        
        return cost
    
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
                    isum += power / dist**2
                    
                    # I assume pmax and dmax correspond to the closest most powerful cell whose signal reaches the user
                    if power > pmax:
                        pmax = power
                        dmax = [dist]

                    elif power == pmax:
                        dmax.append(dist)
            
            interferences += isum - pmax / min(dmax)**2
        
        return interferences
    
    def coveredUsers(self):        
        return self.__coveredUsersHelper(self.__deployment)

    def cost(self):        
        return self.__costHelper(self.__deployment)

    # Both coverage and interferences need the set of covered users
    # It can be sent as a parameter to prevent wasting time computing it twice
    def coverage(self, nusers_covered = None):
        if nusers_covered is None:
            return len(self.coveredUsers()) / self.__instance.nusers
        else:
            return nusers_covered / self.__instance.nusers
    
    def interferences(self, cusers = None):
        covered_users = self.coveredUsers() if cusers is None else cusers
        return self.__interferencesHelper(self.__deployment, covered_users)

    def isFeasible(self):
        # A solution is feasible if all cells are compatible with their current locations and also are connected

        # Non-null cell indices for the __deployment array
        nncells_idx = self.getNonNullCells()
        
        # For every non-null cell, if it is deployed in an incompatible location, the solution is not feasible
        for idx in nncells_idx:
            if idx not in self.__instance.cell_compatibility[self.__deployment[idx]]:
                return False
        
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
    
    def copy(self):
        return Deployment(instance = self.__instance, max_cost = self.__max_cost, 
                          max_interferences = self.__max_interferences, weights = self.weights(), 
                          deployment = self.__deployment.copy())
    
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
    
    def getNullCells(self):
        return [i for i in range(self.__instance.ncandidates) if self.__deployment[i] == 0]
    
    def getMaxInterferences(self):
        return self.__max_interferences
    
    def getMaxCost(self):
        return self.__max_cost
    
    def getCellCount(self):
        count = {}
        for cell in self.__instance.cells_ids:
            count[cell] = self.__deployment.count(cell)
        count[0] = self.__deployment.count(0)

        return count

    def getSummary(self):
        print("--- DEPLOYMENT SUMMARY ---")
        print("Coverage: ", self.coverage())
        print("Cost: ", self.cost())
        print("Max cost", self.__max_cost)
        print("Interferences: ", self.interferences())
        print("Max interferences: ", self.__max_interferences)
        print("Objective: ", self.objective())
        print("Feasible: ", self.isFeasible())