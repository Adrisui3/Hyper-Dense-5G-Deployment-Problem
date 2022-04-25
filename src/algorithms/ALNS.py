from deployment import Deployment
from instance import Instance
from operators import *
import random
import numpy as np

def adaptiveSearchThreshold(problem_instance, oper, init, iter, segment, r, beta, wobjective = (1, 1, 1)):
    feasible_solutions = {}
    infeasible_solutions = set()
    incumbent = Deployment(instance = problem_instance, weights = wobjective, init = init)
    best_solution = incumbent
    best_objective = best_solution.objective()
    
    nopers = len(oper)
    weights = [1/nopers for _ in range(nopers)]
    scores = [0 for _ in range(nopers)]
    times_exe = [0 for _ in range(nopers)]

    feasible_solutions[best_solution.immutableDeployment()] = best_objective
    for i in range(iter):
        # Randomly selected operator to be applied
        oper_idx = random.choices(range(nopers), weights = weights, k = 1)[0]
        current_solution = oper[oper_idx](incumbent)
        times_exe[oper_idx] += 1

        if current_solution.immutableDeployment() in feasible_solutions:
            feasible = True
        elif current_solution.immutableDeployment() in infeasible_solutions:
            feasible = False
        else:
            feasible = current_solution.isFeasible()

        if feasible:            
            # If the solution is feasible and not visited, +1 point
            if current_solution.immutableDeployment() not in feasible_solutions:
                feasible_solutions[current_solution.immutableDeployment()] = current_solution.objective()
                scores[oper_idx] += 1
            
            delta = feasible_solutions[incumbent.immutableDeployment()] - feasible_solutions[current_solution.immutableDeployment()]
            if delta < 0:
                # If the solution is an improvement, +1 point
                scores[oper_idx] += 1
                incumbent = current_solution
                if feasible_solutions[best_solution.immutableDeployment()] < feasible_solutions[incumbent.immutableDeployment()]:
                    # If the solution is the new best, +1 point
                    scores[oper_idx] += 1
                    best_solution = incumbent
                    best_objective = feasible_solutions[incumbent.immutableDeployment()]
            elif  best_objective - beta * ((iter - i) / iter) * best_objective < feasible_solutions[current_solution.immutableDeployment()]:
                incumbent = current_solution
            else:
                # If the solution is not an improvement and it is not accepted, -1 point
                scores[oper_idx] -= 1
        else:
            if current_solution.immutableDeployment() not in infeasible_solutions:
                infeasible_solutions.add(current_solution.immutableDeployment())
            # If the solution is infeasible, -1 point
            scores[oper_idx] -= 1
        
        # Update weights
        if i % segment == 0:
            for j in range(nopers):
                if times_exe[j] == 0:
                    continue
                weights[j] = weights[j] * (1 - r) + r * (scores[j] / times_exe[j])
            
            norm = sum(weights)
            weights = [weight / norm for weight in weights]

            # Re-set scores and number of executions between segments
            scores = [0 for _ in range(nopers)]
            times_exe = [0 for _ in range(nopers)]

        #print("Current iteration: ", i, "-- Current best: ", best_objective, " -- Weights: ", weights, " -- Sum: ", sum(weights))

    return best_solution, best_objective

# ALNS using temperature based acceptance criterion
def adaptiveSearchTemperature(problem_instance, oper, init, iter, segment, r, t_ini, alpha, wobjective = (1, 1, 1)):
    feasible_solutions = {}
    infeasible_solutions = set()
    incumbent = Deployment(instance = problem_instance, weights = wobjective, init = init)
    best_solution = incumbent
    best_objective = best_solution.objective()
    temp = t_ini

    nopers = len(oper)
    weights = [1/nopers for _ in range(nopers)]
    scores = [0 for _ in range(nopers)]
    times_exe = [0 for _ in range(nopers)]

    feasible_solutions[best_solution.immutableDeployment()] = best_objective
    for i in range(iter):
        # Randomly selected operator to be applied
        oper_idx = random.choices(range(nopers), weights = weights, k = 1)[0]
        current_solution = oper[oper_idx](incumbent)
        times_exe[oper_idx] += 1

        if current_solution.immutableDeployment() in feasible_solutions:
            feasible = True
        elif current_solution.immutableDeployment() in infeasible_solutions:
            feasible = False
        else:
            feasible = current_solution.isFeasible()

        if feasible:
            # If the solution is feasible and not visited, +1 point
            if current_solution.immutableDeployment() not in feasible_solutions:
                feasible_solutions[current_solution.immutableDeployment()] = current_solution.objective()
                scores[oper_idx] += 1
            
            delta = feasible_solutions[incumbent.immutableDeployment()] - feasible_solutions[current_solution.immutableDeployment()]
            if delta < 0:
                # If the solution is an improvement, +1 point
                scores[oper_idx] += 1
                incumbent = current_solution
                if feasible_solutions[best_solution.immutableDeployment()] < feasible_solutions[incumbent.immutableDeployment()]:
                    # If the solution is the new best, +1 point
                    scores[oper_idx] += 1
                    best_solution = incumbent
                    best_objective = feasible_solutions[incumbent.immutableDeployment()]
            elif  random.uniform(0, 1) < np.exp(-delta/temp):
                incumbent = current_solution
            else:
                # If the solution is not an improvement and it is not accepted, -1 point
                scores[oper_idx] -= 1
        else:
            if current_solution.immutableDeployment() not in infeasible_solutions:
                infeasible_solutions.add(current_solution.immutableDeployment())
            # If the solution is infeasible, -1 point
            scores[oper_idx] -= 1
        
        # Update weights
        if i % segment == 0:
            for j in range(nopers):
                if times_exe[j] == 0:
                    continue
                weights[j] = weights[j] * (1 - r) + r * (scores[j] / times_exe[j])
            
            norm = sum(weights)
            weights = [weight / norm for weight in weights]
            
            # Re-set scores and number of executions between segments
            scores = [0 for _ in range(nopers)]
            times_exe = [0 for _ in range(nopers)]
        
        temp = temp * alpha
        #print("Iteration: ", i, "-- Temperature: ", temp, "-- Current best: ", best_objective, " -- Weights: ", weights, " -- Sum: ", sum(weights))

    return best_solution, best_objective

# ALNS using temperature based acceptance criterion
def adaptiveSearchTABU(problem_instance, oper, init, iter, segment, r, t_ini, alpha, wobjective = (1, 1, 1)):
    visited_solutions = set()
    incumbent = Deployment(instance = problem_instance, weights = wobjective, init = init)
    best_solution = incumbent
    best_objective = best_solution.objective()
    incumbent_objective = best_objective
    temp = t_ini

    nopers = len(oper)
    weights = [1/nopers for _ in range(nopers)]
    scores = [0 for _ in range(nopers)]
    times_exe = [0 for _ in range(nopers)]
    for i in range(iter):
        # Randomly selected operator to be applied
        oper_idx = random.choices(range(nopers), weights = weights, k = 1)[0]
        current_solution = oper[oper_idx](incumbent)
        
        # If the solution has already been visited, it is skipped
        if current_solution.immutableDeployment() in visited_solutions:
            # To prevent losing iterations
            i += 1
            continue
        
        # Keep track of visited solutions
        visited_solutions.add(current_solution.immutableDeployment())

        # Only new solutions will count
        times_exe[oper_idx] += 1
        if current_solution.isFeasible():
            # If the solution is feasible and not visited, +1 point
            scores[oper_idx] += 1
            current_objective = current_solution.objective()
            delta = incumbent_objective - current_objective
            if delta < 0:
                # If the solution is an improvement, +1 point
                scores[oper_idx] += 1
                incumbent = current_solution
                incumbent_objective = current_objective
                if best_objective < incumbent_objective:
                    # If the solution is the new best, +1 point
                    scores[oper_idx] += 1
                    best_solution = incumbent
                    best_objective = incumbent_objective
            elif  random.uniform(0, 1) < np.exp(-delta/temp):
                incumbent = current_solution
                incumbent_objective = current_objective
            else:
                # If the solution is not an improvement and it is not accepted, -1 point
                scores[oper_idx] -= 1
        else:
            # If the solution is infeasible, -1 point
            scores[oper_idx] -= 1
        
        # Update weights
        if i % segment == 0:
            for j in range(nopers):
                if times_exe[j] == 0:
                    continue
                weights[j] = weights[j] * (1 - r) + r * (scores[j] / times_exe[j])
            
            norm = sum(weights)
            weights = [weight / norm for weight in weights]
            
            # Re-set scores and number of executions between segments
            scores = [0 for _ in range(nopers)]
            times_exe = [0 for _ in range(nopers)]
        
        temp = temp * alpha
        #print("Iteration: ", i, "-- Temperature: ", temp, "-- Current best: ", best_objective, " -- Weights: ", weights, " -- Sum: ", sum(weights))

    return best_solution, best_objective