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
    
    def __coveredUsers(self):        
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

    def coverage(self):
        return len(self.__coveredUsers()) / self.__instance.nusers
    
    def interferences(self):
        pass

    def evaluate(self, max_cost, max_interferences):
        print("Cost: ", self.deploymentCost())
        print("Coverage: ", self.coverage())

    

if __name__ == "__main__":
    ins = Instance()
    ins.loadInstance(file = "DS1", visualization = True)

    sol = Deployment(instance = ins)
    sol.evaluate(10, 10)