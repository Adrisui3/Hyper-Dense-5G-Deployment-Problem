from deployment import Deployment
from instance import Instance
from algorithms import *
import numpy as np
import time
import os
import datetime

if __name__ == "__main__":
    oper = [upgradeCells, downgradeCells, swapCells, deployConnected]
    init_deployment = True
    
    LSITER = 1000
    
    ASITER = {"DS1_U":15000, "DS2_U":15000, "DS3_U":15000, "DS4_U":15000, "DS5_U":15000, "DS6_U":15000, "DS7_U":15000, "DS8_U":15000,
              "DS1_B":15000, "DS2_B":15000, "DS3_B":15000, "DS4_B":15000, "DS5_B":15000, "DS6_B":15000, "DS7_B":15000, "DS8_B":15000}
    AS_SEGMMENT = 250
    AS_R = 0.05

    T_INI = 10
    T_END = 0.0001
    ALPHA = 0.999
    N_THREADS = 4
    N_NEIGHBORS = 3

    paths_ds = ["data/uniform/", "data/blobs/"]
    ds_kind = int(input("Dataset topology (1-uniform, 2-blobs): "))
    path = paths_ds[ds_kind - 1]
    datasets = os.listdir(path)
    if not datasets:
        print("No datasets detected")
        exit()
    datasets.sort()

    print("Datasets available: ", datasets)
    ds_selected = list(map(int, input("Datasets selected: ").split()))
    ds_selected = [datasets[i-1] for i in ds_selected]

    nruns = int(input("Number of runs: "))
    algorithm = input("Algorithm: ")
    notes = input("Notes: ")

    results = {}

    for ds in ds_selected:
        print("Current dataset: ", ds)
        ITER = ASITER[ds]
        instance = Instance()
        instance.loadInstance(file = ds, path = path)
        
        objectives = []
        split_objectives = []
        runtimes = []
        solutions = []

        for i in range(nruns):

            tini = time.time()
            
            #best_solution, best_objective = localSearch(problem_instance = instance, iter = LSITER, oper = oper, init = init_deployment)
            
            best_solution, best_objective = simulatedAnnealing(problem_instance = instance, oper = oper, init = init_deployment, T_ini = T_INI, T_end = T_END, alpha = ALPHA, n_neighbors = N_NEIGHBORS)
            #best_solution, best_objective = simulatedAnnealingTABU(problem_instance = instance, oper = oper, init = init_deployment, T_ini = T_INI, T_end = T_END, alpha = ALPHA, n_neighbors = N_NEIGHBORS)
            #best_solution, best_objective = simulatedAnnealingParallel(problem_instance = instance, oper = oper, init = init_deployment, T_ini = T_INI, T_end = T_END, alpha = ALPHA, n_jobs = N_THREADS)
            
            #best_solution, best_objective = adaptiveSearch(problem_instance = instance, oper = oper, init = init_deployment, iter = ITER, segment = AS_SEGMMENT, r = AS_R)
            
            tend = time.time()

            if not best_solution.isFeasible() or best_solution.objective() != best_objective:
                print("EXECUTION FAILED IN DATASET: ", ds)
                exit()
            
            solutions.append(best_solution)
            objectives.append(best_objective)
            split_objectives.append(best_solution.splitObjective())
            runtimes.append(tend - tini)

            print("     Iteration number:", i, "-", "Runtime:", tend - tini, "seconds", "-", "Best objective: ", best_objective)
        
        overall_obj = max(objectives)
        overall_sol = solutions[objectives.index(overall_obj)]
        split_res = list(map(np.mean, zip(*split_objectives)))
        results[ds] = [overall_sol, np.mean(objectives), np.std(objectives), split_res[0], split_res[1], split_res[2], np.mean(runtimes)]

    date = str(datetime.datetime.now())
    date = date.replace(" ", "--")
    with open("results/" + algorithm + "-" + date, "w") as f:
        print(" --- RESULTS --- ", file = f)
        print("Dataset topology: ", ds_kind, file = f)
        print("Runs per dataset: ", nruns, file = f)
        print("Algorithm: ", algorithm, file = f)
        print("Operators: ", oper, file = f)
        print("Initial deployment: ", init_deployment, file = f)
        print("Notes: ", notes, "\n", file = f)

        for ds in ds_selected:
            print(ds, ":", results[ds][1:], file = f)
        
        print("\n--- BEST FOUND SOLUTIONS --- \n", file = f)
        for ds in ds_selected:
            print(ds, ":", results[ds][0], file = f)