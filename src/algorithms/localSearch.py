from deployment import Deployment
from instance import Instance
from operators import *
import random

def localSearch(problem_instance, iter, oper, init, wobjective = (1, 1, 1)):
    current_solution = Deployment(instance = problem_instance, weights = wobjective, init = init)
    best_solution = current_solution
    best_objective = current_solution.objective()
    
    for _ in range(iter):
        # Randomly selected operator to be applied
        current_solution = random.choices(oper, k = 1)[0](best_solution)

        if current_solution.isFeasible():
            current_objective = current_solution.objective()
            if best_objective < current_objective:
                best_solution = current_solution
                best_objective = current_objective

        #print("Iteration: ", _, " -- Current best: ", best_objective)
    return best_solution, best_objective