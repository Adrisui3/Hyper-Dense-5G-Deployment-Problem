import sys
sys.path.insert(1, './src/algorithms')

from deployment import Deployment
from instance import Instance
from localSearch import *
from ALNS import *
from simulatedAnnealing import *

import numpy as np
import time
import os
import datetime

def algorithm(algorithm, parameters, instance):
    # Yes, this is Python code
    match algorithm:
        case "LS":
            t_ini = time.time()
            best_solution, best_objective = localSearch(problem_instance = instance, iter = parameters["iter"], oper = parameters["oper"], init = parameters["init"])
            t_end = time.time()
        case "SA":
            t_ini = time.time()
            best_solution, best_objective = simulatedAnnealing(problem_instance = instance, oper = parameters["oper"], init = parameters["init"], T_ini = parameters["t_ini"], T_end = parameters["t_end"], alpha = parameters["alpha"], n_neighbors = parameters["n_neighbors"])
            t_end = time.time()
        case "SA-T":
            t_ini = time.time()
            best_solution, best_objective = simulatedAnnealingTABU(problem_instance = instance, oper = parameters["oper"], init = parameters["init"], T_ini = parameters["t_ini"], T_end = parameters["t_end"], alpha = parameters["alpha"], n_neighbors = parameters["n_neighbors"])
            t_end = time.time()
        case "SA-P":
            t_ini = time.time()
            best_solution, best_objective = simulatedAnnealingParallel(problem_instance = instance, oper = parameters["oper"], init = parameters["init"], T_ini = parameters["t_ini"], T_end = parameters["t_end"], alpha = parameters["alpha"], n_jobs = parameters["n_jobs"])
            t_end = time.time()
        case "ALNS":
            t_ini = time.time()
            best_solution, best_objective = adaptiveSearch(problem_instance = instance, oper = parameters["oper"], init = parameters["init"], iter = parameters["iter"], segment = parameters["segment"], r = parameters["r"])
            t_end = time.time()
        case "ALNS-T":
            t_ini = time.time()
            best_solution, best_objective = adaptiveSearchTemperature(problem_instance = instance, oper = parameters["oper"], init = parameters["init"], iter = parameters["iter"], segment = parameters["segment"], r = parameters["r"], T_ini = parameters["t_ini"], alpha = parameters["alpha"])
            t_end = time.time()

    return best_solution, best_objective, t_end - t_ini


if __name__ == "__main__":
    oper = [upgradeCells, downgradeCells, swapCells, deployConnected] 
    init_deployment = True
    
    LSITER = 10000
    
    ASITER = 20000
    AS_T_INI = 10
    AS_ALPHA = 0.9995
    SEGMENT = 350
    R = 0.05

    T_INI = 10
    T_END = 0.0001
    ALPHA = 0.999
    N_JOBS = 4
    N_NEIGHBORS = 3

    ls_params = {"iter":LSITER, "init":init_deployment, "oper":oper}
    sa_params = {"t_ini":T_INI, "t_end":T_END, "alpha":ALPHA, "n_neighbors":N_NEIGHBORS, "init":init_deployment, "oper":oper}
    sat_params = {"t_ini":T_INI, "t_end":T_END, "alpha":ALPHA, "n_neighbors":N_NEIGHBORS, "init":init_deployment, "oper":oper}
    sap_params = {"t_ini":T_INI, "t_end":T_END, "alpha":ALPHA, "n_jobs":N_JOBS, "init":init_deployment, "oper":oper}
    alns_params = {"iter":ASITER, "segment":SEGMENT, "r":R, "init":init_deployment, "oper":oper}
    alnst_params = {"iter":ASITER, "segment":SEGMENT, "r":R, "t_ini":AS_T_INI, "alpha":AS_ALPHA, "init":init_deployment, "oper":oper}
    parameters = {"LS":ls_params, "SA":sa_params, "SA-T":sat_params, "SA-P":sap_params, "ALNS":alns_params, "ALNS-T":alnst_params, "init":init_deployment, "oper":oper}

    paths_ds = ["data/uniform/", "data/blobs/"]
    ds_kind = int(input("Dataset topology (1-uniform, 2-blobs): "))
    path = paths_ds[ds_kind - 1]
    restricted = input("Compatibility restrictions (y/n): ")
    path = path + "not-restricted/" if restricted == 'n' else path + "restricted/"
    datasets = os.listdir(path)
    if not datasets:
        print("No datasets detected")
        exit()
    datasets.sort()

    print("Datasets available: ", datasets)
    ds_selected = list(map(int, input("Datasets selected: ").split()))
    ds_selected = [datasets[i-1] for i in ds_selected]
    
    alg = input("Algorithm (LS, SA, SA-T, SA-P, ALNS, ALNS-T): ")
    nruns = int(input("Number of runs: "))
    notes = input("Notes: ")

    results = {}

    for ds in ds_selected:
        print("Current dataset: ", ds)
        instance = Instance()
        instance.loadInstance(file = ds, path = path)
        
        objectives = []
        split_objectives = []
        runtimes = []
        solutions = []

        for i in range(nruns):
            best_solution, best_objective, runtime = algorithm(algorithm = alg, parameters = parameters[alg], instance = instance)

            if not best_solution.isFeasible() or best_solution.objective() != best_objective:
                print("EXECUTION FAILED IN DATASET: ", ds)
                exit()
            
            solutions.append(best_solution)
            objectives.append(best_objective)
            split_objectives.append(best_solution.splitObjective())
            runtimes.append(runtime)

            print("     Iteration number:", i, "-", "Runtime:", runtime, "seconds", "-", "Best objective: ", best_objective)
        
        overall_obj = max(objectives)
        overall_sol = solutions[objectives.index(overall_obj)]
        split_res = list(map(np.mean, zip(*split_objectives)))
        results[ds] = [overall_sol, np.mean(objectives), np.std(objectives), split_res[0], split_res[1], split_res[2], np.mean(runtimes)]

    date = str(datetime.datetime.now())
    date = date.replace(" ", "--")
    with open("results/" + alg + "/" + date, "w") as f:
        print(" --- RESULTS --- ", file = f)
        print("Dataset topology: ", ds_kind, file = f)
        print("Runs per dataset: ", nruns, file = f)
        print("Algorithm: ", alg, file = f)
        print("Parameters: ", parameters[alg], file = f)
        print("Notes: ", notes, "\n", file = f)

        for ds in ds_selected:
            print(ds, ":", results[ds][1:], file = f)
        
        print("\n--- BEST FOUND SOLUTIONS --- \n", file = f)
        for ds in ds_selected:
            print(ds, ":", results[ds][0], file = f)