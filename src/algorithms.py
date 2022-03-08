from deployment import Deployment
from instance import Instance
from operators import *
import random
import numpy as np


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

# Values for initial and final temperature are found in the references
def simulatedAnnealing(problem_instance, n_neighbors = 1, T_ini = 100, T_end = 0.001, alpha = 0.999, wobjective = (1, 1, 1)):
    incumbent = Deployment(instance = problem_instance, weights = wobjective)
    best_solution = incumbent
    best_objective = best_solution.objective()
    temp = T_ini

    while temp > T_end:
        for _ in range(n_neighbors):
            ran = random.uniform(0, 1)
            if ran < 0.25:
                current_solution = upgradeCells(incumbent)
            elif ran < 0.5:
                current_solution = downgradeCells(incumbent)
            elif ran < 0.75:
                current_solution = swapCells(incumbent)
            else:
                current_solution = deployConnected(incumbent)
            
            if current_solution.isFeasible():
                current_objective = current_solution.objective()
                incumbent_objective = incumbent.objective()
                delta = incumbent_objective - current_objective
                if delta < 0:
                    incumbent = current_solution
                    if best_objective < current_objective:
                        best_solution = current_solution
                        best_objective = current_objective
                elif random.uniform(0, 1) < np.exp(-delta/temp):
                    incumbent = current_solution
        
        temp = temp * alpha
    
    return best_solution, best_objective

def simulatedAnnealingTABU(problem_instance, n_neighbors = 1, T_ini = 100, T_end = 0.001, alpha = 0.999, wobjective = (1, 1, 1)):
    feasible_solutions = {}
    infeasible_solutions = set()
    incumbent = Deployment(instance = problem_instance, weights = wobjective)
    best_solution = incumbent
    best_objective = best_solution.objective()
    temp = T_ini

    feasible_solutions[best_solution.immutableDeployment()] = best_objective
    while temp > T_end:
        for _ in range(n_neighbors):
            ran = random.uniform(0, 1)
            if ran < 0.25:
                current_solution = upgradeCells(incumbent)
            elif ran < 0.5:
                current_solution = downgradeCells(incumbent)
            elif ran < 0.75:
                current_solution = swapCells(incumbent)
            else:
                current_solution = deployConnected(incumbent)
            
            if current_solution.immutableDeployment() in feasible_solutions:
                feasible = True
            elif current_solution.immutableDeployment() in infeasible_solutions:
                feasible = False
            else:
                feasible = current_solution.isFeasible()


            if feasible:
                if current_solution.immutableDeployment() not in feasible_solutions:
                    feasible_solutions[current_solution.immutableDeployment()] = current_solution.objective()
                
                delta = feasible_solutions[incumbent.immutableDeployment()] - feasible_solutions[current_solution.immutableDeployment()]
                if delta < 0:
                    incumbent = current_solution
                    if feasible_solutions[best_solution.immutableDeployment()] < feasible_solutions[incumbent.immutableDeployment()]:
                        best_solution = incumbent
                        best_objective = feasible_solutions[incumbent.immutableDeployment()]
                elif random.uniform(0, 1) < np.exp(-delta/temp):
                    incumbent = current_solution
            else:
                if current_solution.immutableDeployment() not in infeasible_solutions:
                    infeasible_solutions.add(current_solution.immutableDeployment())

        temp = temp * alpha
        #print("Temperature: ", temp)
    
    return best_solution, best_objective

if __name__ == "__main__":
    ins = Instance()
    ins.loadInstance(file = "DS8", visualization = False)

    #solution, objective = localSearch(ins, 5000)
    solution, objective = simulatedAnnealingTABU(problem_instance= ins, n_neighbors = 1)

    debug = Deployment(instance = ins)
    print(" --- INITIAL SOLUTION DEBUG ---")
    debug.test()
    print("Initial solution: ", ins.generateInitDeployment())
    print(" --- BEST SOLUTION DEBUG --- ")
    solution.test()
    print("Best solution found: ", solution)
