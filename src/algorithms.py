from deployment import Deployment
from instance import Instance
from operators import *
import random


def localSearch(problem_instance, iter, wobjective = (1/3, 1/3, 1/3)):
    current_solution = Deployment(instance = problem_instance, wcost = wobjective[0], wcoverage = wobjective[1], winterferences = wobjective[2])
    best_solution = current_solution
    best_objective = current_solution.objective()
    
    for i in range(iter):
        ran = random.uniform(0, 1)
        if ran < 0.5:
            current_solution = upgradeCells(best_solution)
        else:
            current_solution = downgradeCells(best_solution)

        if current_solution.isFeasible():
            current_objective = current_solution.objective()
            if best_objective < current_objective:
                best_solution = current_solution
                best_objective = current_objective
    
    return best_solution, best_objective


if __name__ == "__main__":
    ins = Instance()
    ins.loadInstance(file = "DS8", visualization = False)

    solution, objective = localSearch(ins, 2000)

    debug = Deployment(ins)
    print(" --- INITIAL SOLUTION DEBUG ---")
    debug.test()
    print(" --- BEST SOLUTION DEBUG --- ")
    solution.test()
    print("Best solution found: ", solution)
