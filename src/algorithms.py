from deployment import Deployment
from instance import Instance
from operators import *
import random
import numpy as np
import threading
import os
###################### SA ######################

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

        print("Iteration: ", _, " -- Current best: ", best_objective)
    return best_solution, best_objective




###################### SA ######################

def simulatedAnnealing(problem_instance, oper, init, n_neighbors = 1, T_ini = 10, T_end = 0.0001, alpha = 0.999, wobjective = (1, 1, 1)):
    incumbent = Deployment(instance = problem_instance, weights = wobjective, init = init)
    best_solution = incumbent
    best_objective = best_solution.objective()
    temp = T_ini

    while temp > T_end:
        for _ in range(n_neighbors):
            # Randomly selected operator to be applied
            current_solution = random.choices(oper, k = 1)[0](incumbent)
            
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

def simulatedAnnealingTABU(problem_instance, oper, init, n_neighbors = 1, T_ini = 10, T_end = 0.0001, alpha = 0.999, wobjective = (1, 1, 1)):
    feasible_solutions = {}
    infeasible_solutions = set()
    incumbent = Deployment(instance = problem_instance, weights = wobjective, init = init)
    best_solution = incumbent
    best_objective = best_solution.objective()
    temp = T_ini

    feasible_solutions[best_solution.immutableDeployment()] = best_objective
    while temp > T_end:
        for _ in range(n_neighbors):
            # Randomly selected operator to be applied
            current_solution = random.choices(oper, k = 1)[0](incumbent)
            
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
                        #print("New best!")
                elif random.uniform(0, 1) < np.exp(-delta/temp):
                    incumbent = current_solution
            else:
                if current_solution.immutableDeployment() not in infeasible_solutions:
                    infeasible_solutions.add(current_solution.immutableDeployment())

        temp = temp * alpha
        #print("Temperature:", temp, "-- Current best: ", best_objective)
    
    return best_solution, best_objective

def SAIteration(lock, thread_incumbents, thread_incumbents_costs, idx, temp, oper, best_solution, best_objective):
    current_solution = random.choices(oper, k = 1)[0](thread_incumbents[idx])

    if current_solution.isFeasible():
        current_objective = current_solution.objective()
        incumbent_objective = thread_incumbents_costs[idx]
        delta = incumbent_objective - current_objective
        if delta < 0:
            thread_incumbents[idx] = current_solution
            thread_incumbents_costs[idx] = current_objective
            with lock:
                if best_objective[0] < thread_incumbents_costs[idx]:
                    best_solution[0] = thread_incumbents[idx]
                    best_objective[0] = thread_incumbents_costs[idx]
        elif random.uniform(0, 1) < np.exp(-delta/temp):
            thread_incumbents[idx] = current_solution
            thread_incumbents_costs[idx] = current_objective


def simulatedAnnealingParallel(problem_instance, oper, init, n_jobs = 1, T_ini = 10, T_end = 0.0001, alpha = 0.999, wobjective = (1, 1, 1)):
    n_jobs = os.cpu_count() if n_jobs == -1 else n_jobs
    incumbent = Deployment(instance = problem_instance, weights = wobjective, init = init)
    best_solution = [incumbent]
    best_objective = [best_solution[0].objective()]
    thread_incumbents = [best_solution[0].copy() for _ in range(n_jobs)]
    thread_incumbents_costs = [best_objective[0] for _ in range(n_jobs)]
    threads = []
    lock = threading.Lock()
    
    temp = T_ini
    while temp > T_end:
        for ii in range(n_jobs):
            thread = threading.Thread(target=SAIteration, 
                                      args=(lock, thread_incumbents, thread_incumbents_costs, ii, temp, oper, best_solution, best_objective))
            thread.start()
            threads.append(thread)
        
        for thread in threads:
            thread.join()
        
        best_incumbent_idx = thread_incumbents_costs.index(max(thread_incumbents_costs))
        thread_incumbents = [thread_incumbents[best_incumbent_idx].copy() for _ in range(n_jobs)]
        thread_incumbents_costs = [thread_incumbents_costs[best_incumbent_idx] for _ in range(n_jobs)]

        temp = temp * alpha
        #print("Temperature:", temp, "-- Current best: ", best_objective[0])
    
    return best_solution[0], best_objective[0]


###################### ALNS ######################

def adaptiveSearch(problem_instance, oper, init, iter, segment, r, wobjective = (1, 1, 1)):
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
                # If the solution is an improvement, +2 points
                scores[oper_idx] += 2
                incumbent = current_solution
                if feasible_solutions[best_solution.immutableDeployment()] < feasible_solutions[incumbent.immutableDeployment()]:
                    best_solution = incumbent
                    best_objective = feasible_solutions[incumbent.immutableDeployment()]
                    # If the solution is the new best, +3 points
                    scores[oper_idx] += 3
            elif  best_objective - 0.2 * ((iter - i) / iter) * best_objective < feasible_solutions[current_solution.immutableDeployment()]:
                incumbent = current_solution
        else:
            if current_solution.immutableDeployment() not in infeasible_solutions:
                infeasible_solutions.add(current_solution.immutableDeployment())
        
        # Update weights
        if i % segment == 0:
            for i in range(nopers):
                if times_exe[i] == 0:
                    continue
                weights[i] = weights[i] * (1 - r) + r * (scores[i] / times_exe[i])
            
            norm = sum(weights)
            weights = [weight / norm for weight in weights]

        print("Current iteration: ", i, "-- Current best: ", best_objective, " -- Weights: ", weights, " -- Sum: ", sum(weights))

    return best_solution, best_objective

# ALNS using temperature based acceptance criterion
def adaptiveSearchTemperature(problem_instance, oper, init, iter, segment, r, T_ini = 100, T_end = 0.001, alpha = 0.999, wobjective = (1, 1, 1)):
    feasible_solutions = {}
    infeasible_solutions = set()
    incumbent = Deployment(instance = problem_instance, weights = wobjective, init = init)
    best_solution = incumbent
    best_objective = best_solution.objective()
    temp = T_ini

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
                # If the solution is an improvement, +2 points
                scores[oper_idx] += 2
                incumbent = current_solution
                if feasible_solutions[best_solution.immutableDeployment()] < feasible_solutions[incumbent.immutableDeployment()]:
                    best_solution = incumbent
                    best_objective = feasible_solutions[incumbent.immutableDeployment()]
                    # If the solution is the new best, +3 points
                    scores[oper_idx] += 3
            elif  random.uniform(0, 1) < np.exp(-delta/temp):
                incumbent = current_solution
        else:
            if current_solution.immutableDeployment() not in infeasible_solutions:
                infeasible_solutions.add(current_solution.immutableDeployment())
        
        # Update weights
        if i % segment == 0:
            for i in range(nopers):
                if times_exe[i] == 0:
                    continue
                weights[i] = weights[i] * (1 - r) + r * (scores[i] / times_exe[i])
            
            norm = sum(weights)
            weights = [weight / norm for weight in weights]
        
        temp = temp * alpha if temp > T_end else T_end
        print("Current iteration: ", i, "-- Current best: ", best_objective, " -- Weights: ", weights, " -- Sum: ", sum(weights), " -- Temperature: ", temp)

    return best_solution, best_objective