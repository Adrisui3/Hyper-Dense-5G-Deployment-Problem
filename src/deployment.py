from instance import Instance

class Deployment:
    def __init__(self, instance, deployment = None):
        self.__instance = instance
        self.__deployment = deployment if deployment is not None else self.instance.generateInitDeployment()

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


    # Working in progress
    def __deploymentCost(self):
        pass
    
    def __coverage(self):
        pass
    
    def __interferences(self):
        pass

    def evaluate(self):
        pass
    

if __name__ == "__main__":
    ins = Instance()
    ins.loadInstance(file = "DST", visualization = True)

    sol = Deployment(instance = ins, deployment = [0, 1, 2, 3, 4])

    for i in range(len(sol)):
        print(sol[i])