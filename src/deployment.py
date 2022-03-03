from instance import Instance


class Deployment:
    def __init__(self, instance, deployment = None):
        self.__instance = instance
        self.__deployment = deployment if deployment is not None else self.__instance.generateInitDeployment()

    def __getitem__(self, index):
        return self.__deployment[index]
    
    def __setitem__(self, index):
        return self.__deployment[index]
    
    def __delitem__(self, index):
        del self.__deployment[index]
    
    def __len__(self):
        return len(self.__deployment)
    
    def __str__(self):
        return str(self.__deployment)
    
    def coveredUsers(self):        
        covered_users = set()
        for i in range(self.__instance.nusers):
            user_dist = self.__instance.dmatrix_users_candidates[i]
            for j in range(self.__instance.ncandidates):
                if self.__deployment[j] == 0:
                    continue
                
                # If covered, go for the next user
                if user_dist[j] <= self.__instance.cells[self.__deployment[j]][1]:
                    covered_users.add(i)
                    break

        return covered_users

    def deploymentCost(self):
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
    
    def interferences(self, cusers = None):
        covered_users = self.coveredUsers() if cusers is None else cusers
        interferences = 0
        for user in covered_users:
            isum, pmax, dmax = 0, 0, 0
            for i in range(self.__instance.ncandidates):
                if self.__deployment[i] == 0:
                    continue
                
                if self.__instance.dmatrix_users_candidates[user][i] <= self.__instance.cells[self.__deployment[i]][1]:
                    dist = self.__instance.dmatrix_users_candidates[user][i]
                    power = self.__instance.cells[self.__deployment[i]][2]
                    isum += power / pow(dist, 2)
                    
                    if power > pmax:
                        pmax = power
                        dmax = dist
            
            interferences += isum - pmax / pow(dmax, 2)
        
        return interferences

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
            
    def evaluate(self):
        print("\nCost: ", self.deploymentCost())
        print("Coverage: ", self.coverage())
        print("Interferences: ", self.interferences())
        print("Feasible: ", self.isFeasible())

    

if __name__ == "__main__":
    ins = Instance()
    ins.loadInstance(file = "DST", visualization = True)

    sol = Deployment(instance = ins)
    sol.evaluate()

    ins = Instance()
    ins.loadInstance(file = "DS1", visualization = True)

    sol = Deployment(instance = ins)
    sol.evaluate()

    ins = Instance()
    ins.loadInstance(file = "DS2", visualization = True)

    sol = Deployment(instance = ins)
    sol.evaluate()

    ins = Instance()
    ins.loadInstance(file = "DS3", visualization = True)

    sol = Deployment(instance = ins)
    sol.evaluate()