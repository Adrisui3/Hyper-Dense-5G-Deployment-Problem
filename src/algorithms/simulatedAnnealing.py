from deployment import Deployment
from instance import Instance
from operators import *
import random
import numpy as np
import threading
import os

def simulatedAnnealing(problem_instance, oper, init, t_ini, t_end, alpha, n_neighbors = 1, wobjective = (1, 1, 1)):
    incumbent = Deployment(instance = problem_instance, weights = wobjective, init = init)
    best_solution = incumbent
    best_objective = best_solution.objective()
    temp = t_ini

    while temp > t_end:
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

def simulatedAnnealingCache(problem_instance, oper, init, t_ini, t_end, alpha, n_neighbors = 1, wobjective = (1, 1, 1)):
    feasible_solutions = {}
    infeasible_solutions = set()
    incumbent = Deployment(instance = problem_instance, weights = wobjective, init = init)
    best_solution = incumbent
    best_objective = best_solution.objective()
    temp = t_ini

    feasible_solutions[best_solution.immutableDeployment()] = best_objective
    while temp > t_end:
        for _ in range(n_neighbors):
            # Randomly selected operator to be applied
            current_solution = random.choices(oper, k = 1)[0](incumbent)
            
            # If the solution has already been visited, avoid wasting time
            if current_solution.immutableDeployment() in feasible_solutions:
                feasible = True
            elif current_solution.immutableDeployment() in infeasible_solutions:
                feasible = False
            else:
                feasible = current_solution.isFeasible()

            if feasible:
                # If feasible but not visited, store its cost
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
                # If infeasible but not visited, store it
                if current_solution.immutableDeployment() not in infeasible_solutions:
                    infeasible_solutions.add(current_solution.immutableDeployment())

        temp = temp * alpha
        #print("Temperature:", temp, "-- Current best: ", best_objective)
    
    return best_solution, best_objective

def SAIteration(lock, thread_infeasible_solutions, thread_feasible_solutions, thread_incumbents, idx, 
                    temp, oper, best_solution, best_objective):
    
    current_solution = random.choices(oper, k = 1)[0](thread_incumbents[idx])
    
    # If the solution has already been visited, avoid wasting time
    if current_solution.immutableDeployment() in thread_feasible_solutions[idx]:
        feasible = True
    elif current_solution.immutableDeployment() in thread_infeasible_solutions[idx]:
        feasible = False
    else:
        feasible = current_solution.isFeasible()

    if feasible:
        # If feasible but not visited, store its cost
        if current_solution.immutableDeployment() not in thread_feasible_solutions[idx]:
            thread_feasible_solutions[idx][current_solution.immutableDeployment()] = current_solution.objective()
        
        delta = thread_feasible_solutions[idx][thread_incumbents[idx].immutableDeployment()] - thread_feasible_solutions[idx][current_solution.immutableDeployment()]
        if delta < 0:
            thread_incumbents[idx] = current_solution
            # Preventing race conditions...
            with lock:
                if best_objective[0] < thread_feasible_solutions[idx][thread_incumbents[idx].immutableDeployment()]:
                    best_solution[0] = thread_incumbents[idx]
                    best_objective[0] = thread_feasible_solutions[idx][thread_incumbents[idx].immutableDeployment()]
        elif random.uniform(0, 1) < np.exp(-delta/temp):
            thread_incumbents[idx] = current_solution
    else:
        # If infeasible but not visited, store it
        if current_solution.immutableDeployment() not in thread_infeasible_solutions[idx]:
            thread_infeasible_solutions[idx].add(current_solution.immutableDeployment())

def cooperativeSimulatedAnnealing(problem_instance, oper, init, t_ini, t_end, alpha, n_jobs = 1, wobjective = (1, 1, 1)):
    
    # n_jobs threads will compute a neighbor solution of the incumbent in parallel.
    # Once finished, all neighbors will be compared and the best of them will be selected
    # as the next incumbent.
    
    n_jobs = os.cpu_count() if n_jobs == -1 else n_jobs
    incumbent = Deployment(instance = problem_instance, weights = wobjective, init = init)
   
    # Best solution and objective are now stored in lists, so they can be shared between threads. 
    # This is probably the easiest way to do it
    best_solution = [incumbent]
    best_objective = [best_solution[0].objective()]
    
    # i-th thread owns the i-th incumbent 
    thread_incumbents = [best_solution[0].copy() for _ in range(n_jobs)]
    
    # Each thread will have its own cache
    thread_infeasible_solutions = [set() for _ in range(n_jobs)]
    thread_feasible_solutions = [{best_solution[0].immutableDeployment():best_objective[0]} for _ in range(n_jobs)]
    
    lock = threading.Lock()
    threads = []
    
    temp = t_ini
    while temp > t_end:
        for ii in range(n_jobs):
            thread = threading.Thread(target = SAIteration, 
                                      args = (lock, thread_infeasible_solutions, thread_feasible_solutions, thread_incumbents, ii, temp, oper, best_solution, best_objective))
            thread.start()
            threads.append(thread)
        
        for thread in threads:
            thread.join()
        
        threads.clear()
        # Once finished, get the best found solution from the threads and set it as the next incumbent solution
        thread_costs = [thread_feasible_solutions[i][thread_incumbents[i].immutableDeployment()] for i in range(n_jobs)]
        best_incumbent_idx = thread_costs.index(max(thread_costs))
        
        # Add next incumbent to feasible solutions for each thread if not present
        for i in range(n_jobs):
            if thread_incumbents[best_incumbent_idx].immutableDeployment() not in thread_feasible_solutions[i]:
                thread_feasible_solutions[i][thread_incumbents[best_incumbent_idx].immutableDeployment()] = thread_costs[best_incumbent_idx]
        
        # Set next incumbent
        thread_incumbents = [thread_incumbents[best_incumbent_idx].copy() for _ in range(n_jobs)]

        temp = temp * alpha
        #print("Temperature:", temp, "-- Current best: ", best_objective[0])
    
    return best_solution[0], best_objective[0]