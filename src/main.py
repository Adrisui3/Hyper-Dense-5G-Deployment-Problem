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

# DISCLAIMER: This file is only intended for demoing purposes, thus it will contain bad coding practices!

def algorithm(algorithm, parameters, instance, oper):

    match algorithm:
        case "LS":
            t_ini = time.time()
            best_solution, best_objective = localSearch(problem_instance = instance, iter = parameters["iter"], oper = oper, init = parameters["init"])
            t_end = time.time()
        case "SA":
            t_ini = time.time()
            best_solution, best_objective = simulatedAnnealing(problem_instance = instance, oper = oper, init = parameters["init"], t_ini = parameters["t_ini"], t_end = parameters["t_end"], alpha = parameters["alpha"], n_neighbors = parameters["n_neighbors"])
            t_end = time.time()
        case "SA-C":
            t_ini = time.time()
            best_solution, best_objective = simulatedAnnealingCache(problem_instance = instance, oper = oper, init = parameters["init"], t_ini = parameters["t_ini"], t_end = parameters["t_end"], alpha = parameters["alpha"], n_neighbors = parameters["n_neighbors"])
            t_end = time.time()
        case "COP-SA":
            t_ini = time.time()
            best_solution, best_objective = cooperativeSimulatedAnnealing(problem_instance = instance, oper = oper, init = parameters["init"], t_ini = parameters["t_ini"], t_end = parameters["t_end"], alpha = parameters["alpha"], n_jobs = parameters["n_jobs"])
            t_end = time.time()
        case "ALNS-TH":
            t_ini = time.time()
            best_solution, best_objective = adaptiveSearchThreshold(problem_instance = instance, oper = oper, init = parameters["init"], iter = parameters["iter"], segment = parameters["segment"], r = parameters["r"], beta = parameters["beta"])
            t_end = time.time()
        case "ALNS-TP":
            t_ini = time.time()
            best_solution, best_objective = adaptiveSearchTemperature(problem_instance = instance, oper = oper, init = parameters["init"], iter = parameters["iter"][dataset], segment = parameters["segment"], r = parameters["r"], t_ini = parameters["t_ini"], alpha = parameters["alpha"])
            t_end = time.time()
        case "ALNS-TB":
            t_ini = time.time()
            best_solution, best_objective = adaptiveSearchTABU(problem_instance = instance, oper = oper, init = parameters["init"], iter = parameters["iter"][dataset], segment = parameters["segment"], r = parameters["r"], t_ini = parameters["t_ini"], alpha = parameters["alpha"])
            t_end = time.time()
        case "COP-ALNS":
            t_ini = time.time()
            best_solution, best_objective = cooperativeALNS(problem_instance = instance, oper = oper, init = parameters["init"], n_jobs = parameters["n_jobs"], t_ini = parameters["t_ini"], t_end = parameters["t_end"], alpha = parameters["alpha"], segment = parameters["segment"], r = parameters["r"])
            t_end = time.time()

    return best_solution, best_objective, t_end - t_ini


if __name__=="__main__":
    
    oper = [upgradeCells, downgradeCells, swapCells, deployConnected]
    ls_params = {"iter":None, "init":None}
    sa_params = {"t_ini":None, "t_end":None, "alpha":None, "n_neighbors":None, "init":None}
    sac_params = {"t_ini":None, "t_end":None, "alpha":None, "n_neighbors":None, "init":None}
    copsa_params = {"t_ini":None, "t_end":None, "alpha":None, "n_jobs":None, "init":None}
    alnsth_params = {"iter":None, "segment":None, "r":None, "init":None, "beta":None}
    alnstp_params = {"iter":None, "segment":None, "r":None, "t_ini":None, "alpha":None, "init":None}
    alnstb_params = {"iter":None, "segment":None, "r":None, "t_ini":None, "alpha":None, "init":None}
    coopalns_params = {"t_ini":None, "t_end":None, "alpha":None, "n_jobs":None, "init":None, "segment":None, "r":None}
    parameters = {"LS":ls_params, "SA":sa_params, "SA-C":sac_params, "COP-SA":copsa_params, "ALNS-TH":alnsth_params, "ALNS-TP":alnstp_params, "ALNS-TB":alnstb_params, "COP-ALNS":coopalns_params}

    float_params = {"t_ini", "t_end", "r", "alpha", "beta"}
    int_params = {"iter", "segment", "n_neighbors", "n_jobs"}
    bool_params = {"init"}

    paths_ds = ["data/uniform/", "data/blobs/", "data/kml/"]
    ds_kind = int(input("Dataset topology (1-uniform, 2-blobs, 3-KML): "))
    path = paths_ds[ds_kind - 1]
    
    if ds_kind != 3:
        restricted = input("Compatibility restrictions (y/n): ")
        path = path + "non-restricted/" if restricted == 'n' else path + "restricted/"
    
    datasets = os.listdir(path)
    if not datasets:
        print("No datasets detected")
        exit()
    datasets.sort()

    print("Datasets available: ", ', '.join(datasets))
    ds_selected = list(map(int, input("Selected datasets: ").split()))
    ds_selected = [datasets[i-1] for i in ds_selected]
    
    algorithms = ["LS", "SA", "SA-C", "COP-SA", "ALNS-TH", "ALNS-TP", "ALNS-TB", "COP-ALNS"]
    print("Algorithms available:", ', '.join(algorithms))
    alg_selected = list(map(int, input("Selected algorithms: ").split()))
    alg_selected = [algorithms[i-1] for i in alg_selected]

    nruns = int(input("Number of runs: "))
    notes = input("Notes: ")
    
    date = str(datetime.datetime.now())
    date = date.replace(" ", "--")
    print("--- PARAMETER SELECTION ---")
    for alg in alg_selected:
        print("     " + alg + " parameters: ")
        cparams = parameters[alg]
        
        for key in cparams:
            val = input("       " + key + ": ")
            if key in float_params:
                cparams[key] = float(val)
            elif key in int_params:
                cparams[key] = int(val)
            elif key in bool_params:
                cparams[key] = val == "y"
            
        
    results = {}
    print("\n--- SIMULATION ---")
    for alg in alg_selected:
        print("Current algorithm: ", alg)
        
        with open("results/" + alg + "/" + date, "a") as f:
            print(" --- RESULTS --- ", file = f)
            print("Dataset topology: ", ds_kind, file = f)
            print("Runs per dataset: ", nruns, file = f)
            print("Algorithm: ", alg, file = f)
            print("Parameters:", parameters[alg], file = f)
            print("Notes: ", notes, "\n", file = f)
        
        for ds in ds_selected:
            print("     Current dataset: ", ds)
            instance = Instance()
            instance.loadInstance(file = ds, path = path)
            
            objectives = []
            split_objectives = []
            runtimes = []
            solutions = []

            for i in range(nruns):
                best_solution, best_objective, runtime = algorithm(algorithm = alg, parameters = parameters[alg], instance = instance, oper = oper)

                if not best_solution.isFeasible() or best_solution.objective() != best_objective:
                    print("EXECUTION FAILED IN DATASET: ", ds)
                    exit()
                
                solutions.append(best_solution)
                objectives.append(best_objective)
                split_objectives.append(best_solution.splitObjective())
                runtimes.append(runtime)

                print("          Iteration number:", i, "-", "Runtime:", runtime, "seconds", "-", "Best objective: ", best_objective)
            
            overall_obj = max(objectives)
            overall_sol = solutions[objectives.index(overall_obj)]
            split_res = list(map(np.mean, zip(*split_objectives)))
            results[ds] = [overall_sol, np.mean(objectives), np.std(objectives), split_res[0], split_res[1], split_res[2], np.mean(runtimes)]

            with open("results/" + alg + "/" + date, "a") as f:
                print(ds, ":", results[ds][1:], file = f)
                print("     Best solution:", results[ds][0], "\n", file = f)