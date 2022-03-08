from deployment import Deployment
from instance import Instance
from operators import *
import random


def localSearch(problem_instance, iter, wobjective = (1, 1, 1)):
    current_solution = Deployment(instance = problem_instance, weights = wobjective)
    best_solution = current_solution
    best_objective = current_solution.objective()
    
    for _ in range(iter):
        ran = random.uniform(0, 1)
        if ran < 0.25:
            current_solution = upgradeCells(best_solution)
        elif ran < 0.5:
            current_solution = downgradeCells(best_solution)
        elif ran < 0.75:
            current_solution = swapCells(best_solution)
        else:
            current_solution = deployConnected(best_solution)

        if current_solution.isFeasible():
            current_objective = current_solution.objective()
            if best_objective < current_objective:
                best_solution = current_solution
                best_objective = current_objective
    
    return best_solution, best_objective


if __name__ == "__main__":
    ins = Instance()
    ins.loadInstance(file = "DS1", visualization = False)

    solution, objective = localSearch(ins, 100)

    debug = Deployment(instance = ins)
    print(" --- INITIAL SOLUTION DEBUG ---")
    debug.test()
    print(" --- BEST SOLUTION DEBUG --- ")
    solution.test()
    print("Best solution found: ", solution)
