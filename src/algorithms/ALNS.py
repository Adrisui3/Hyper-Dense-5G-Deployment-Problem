from deployment import Deployment
from instance import Instance
from operators import *
import random
import numpy as np
import threading

# ALNS threshold accepting
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
        # Select operator according to weights
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
        # Select operator according to weights
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
        # Select operator according to weights
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

def coALNSIter(lock, thread_infeasible_solutions, thread_feasible_solutions, thread_incumbents, idx, 
                    threads_temps, oper, best_solution, best_objective, thread_weights, segment, r, alpha):
    
    #print("Thread ", idx)

    # Initialize scores and number of calls for each segment
    nopers = len(oper)
    scores = [0 for _ in range(nopers)]
    times_exe = [0 for _ in range(nopers)]
    
    for _ in range(segment):
        #print("     Current iteration: ", _)
        #print("     Scores: ", scores)
        #print("     Call counter: ", times_exe)
        
        # Select operator according to weights      
        oper_idx = random.choices(range(nopers), weights = thread_weights[idx], k = 1)[0]
        current_solution = oper[oper_idx](thread_incumbents[idx])
        times_exe[oper_idx] += 1

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
                scores[oper_idx] += 1

            delta = thread_feasible_solutions[idx][thread_incumbents[idx].immutableDeployment()] - thread_feasible_solutions[idx][current_solution.immutableDeployment()]
            if delta < 0:
                # If the solution is an improvement, +1 point
                scores[oper_idx] += 1
                thread_incumbents[idx] = current_solution
                
                # Preventing race conditions...
                with lock:
                    if best_objective[0] < thread_feasible_solutions[idx][thread_incumbents[idx].immutableDeployment()]:
                        scores[oper_idx] += 1
                        best_solution[0] = thread_incumbents[idx]
                        best_objective[0] = thread_feasible_solutions[idx][thread_incumbents[idx].immutableDeployment()]
            
            elif random.uniform(0, 1) < np.exp(-delta/threads_temps[idx]):
                thread_incumbents[idx] = current_solution
            else:
                scores[oper_idx] -= 1
        else:
            # If infeasible but not visited, store it
            if current_solution.immutableDeployment() not in thread_infeasible_solutions[idx]:
                thread_infeasible_solutions[idx].add(current_solution.immutableDeployment())
            scores[oper_idx] -= 1
        
        threads_temps[idx] = threads_temps[idx]*alpha

    for j in range(nopers):
        if times_exe[j] == 0:
            continue
        thread_weights[idx][j] = thread_weights[idx][j] * (1 - r) + r * (scores[j] / times_exe[j])
            
        norm = sum(thread_weights[idx])
        thread_weights[idx] = [weight / norm for weight in thread_weights[idx]]



def cooperativeALNS(problem_instance, oper, init, t_ini, t_end, alpha, segment, r, n_jobs = 1, wobjective = (1, 1, 1)):
    
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

    # Each thread will have its own weights for the operators
    weights = [1/len(oper) for _ in range(len(oper))]
    thread_weights = [weights.copy() for _ in range(n_jobs)]

    # Lock and thread list
    lock = threading.Lock()
    threads = []
    
    # Each thread has its own temperature
    thread_temps = [t_ini for _ in range(n_jobs)]

    while thread_temps[0] > t_end:
        for ii in range(n_jobs):
            thread = threading.Thread(target = coALNSIter, 
                                      args = (lock, thread_infeasible_solutions, thread_feasible_solutions, thread_incumbents, 
                                              ii, thread_temps, oper, best_solution, best_objective, thread_weights, segment, r, alpha))
            thread.start()
            threads.append(thread)
        
        for thread in threads:
            thread.join()
        
        threads.clear()
        
        # Identify which thread found the best overall solution
        thread_costs = [thread_feasible_solutions[i][thread_incumbents[i].immutableDeployment()] for i in range(n_jobs)]
        best_incumbent_idx = thread_costs.index(max(thread_costs))
        
        # Add next incumbent to feasible solutions for each thread if not present
        for i in range(n_jobs):
            if thread_incumbents[best_incumbent_idx].immutableDeployment() not in thread_feasible_solutions[i]:
                thread_feasible_solutions[i][thread_incumbents[best_incumbent_idx].immutableDeployment()] = thread_costs[best_incumbent_idx]
        
        # Share best found solution between threads
        thread_incumbents = [thread_incumbents[best_incumbent_idx].copy() for _ in range(n_jobs)]

        # Share acquired knowledge of operators' performance between threads
        thread_weights = [thread_weights[best_incumbent_idx].copy() for _ in range(n_jobs)]
        
        #print("Temperature:", thread_temps[0], "-- Current best: ", best_objective[0])
        #print("Temperatures: ", thread_temps)
    
    return best_solution[0], best_objective[0]