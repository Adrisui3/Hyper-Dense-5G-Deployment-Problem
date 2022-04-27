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



# DISCLAIMER: This file is aimed for testing and it should not be used to generate solutions.
# If you really want to solve a problem using these algorithms, I encourage you to
# write your own framework. 
#
# On the other hand, this file will suffer changes almost every commit.
# I do not recommend to follow those changes, since they will generaly be irrelevant
# for the project.

def algorithm(algorithm, dataset, parameters, instance):
    # Yes, this is Python code
    match algorithm:
        case "LS":
            t_ini = time.time()
            best_solution, best_objective = localSearch(problem_instance = instance, iter = parameters["iter"][dataset], oper = parameters["oper"], init = parameters["init"])
            t_end = time.time()
        case "SA":
            t_ini = time.time()
            best_solution, best_objective = simulatedAnnealing(problem_instance = instance, oper = parameters["oper"], init = parameters["init"], t_ini = parameters["t_ini"], t_end = parameters["t_end"], alpha = parameters["alpha"][parameters["n_neighbors"]][dataset], n_neighbors = parameters["n_neighbors"])
            t_end = time.time()
        case "SA-C":
            t_ini = time.time()
            best_solution, best_objective = simulatedAnnealingCache(problem_instance = instance, oper = parameters["oper"], init = parameters["init"], t_ini = parameters["t_ini"], t_end = parameters["t_end"], alpha = parameters["alpha"][parameters["n_neighbors"]][dataset], n_neighbors = parameters["n_neighbors"])
            t_end = time.time()
        case "SA-P":
            t_ini = time.time()
            best_solution, best_objective = simulatedAnnealingParallel(problem_instance = instance, oper = parameters["oper"], init = parameters["init"], t_ini = parameters["t_ini"], t_end = parameters["t_end"], alpha = parameters["alpha"][parameters["n_jobs"]][dataset], n_jobs = parameters["n_jobs"])
            t_end = time.time()
        case "ALNS-TH":
            t_ini = time.time()
            best_solution, best_objective = adaptiveSearchThreshold(problem_instance = instance, oper = parameters["oper"], init = parameters["init"], iter = parameters["iter"][dataset], segment = parameters["segment"], r = parameters["r"], beta = parameters["beta"])
            t_end = time.time()
        case "ALNS-TP":
            t_ini = time.time()
            best_solution, best_objective = adaptiveSearchTemperature(problem_instance = instance, oper = parameters["oper"], init = parameters["init"], iter = parameters["iter"][dataset], segment = parameters["segment"], r = parameters["r"], t_ini = parameters["t_ini"], alpha = parameters["alpha"][dataset])
            t_end = time.time()
        case "ALNS-TB":
            t_ini = time.time()
            best_solution, best_objective = adaptiveSearchTABU(problem_instance = instance, oper = parameters["oper"], init = parameters["init"], iter = parameters["iter"][dataset], segment = parameters["segment"], r = parameters["r"], t_ini = parameters["t_ini"], alpha = parameters["alpha"][dataset])
            t_end = time.time()

    return best_solution, best_objective, t_end - t_ini


if __name__ == "__main__":
    oper = [upgradeCells, downgradeCells, swapCells, deployConnected] 
    init_deployment = True
    
    ITER = {"DS1_U":20000, "DS2_U":20000, "DS3_U":30000, "DS4_U":30000, 
            "DS5_U":40000, "DS6_U":40000, "DS7_U":50000, "DS8_U":50000}

    ALPHAS_1T = {"DS1_U":0.99962545, "DS2_U":0.99962545, "DS3_U":0.999750285, "DS4_U":0.999750285, 
                 "DS5_U":0.99981271, "DS6_U":0.99981271, "DS7_U":0.999850163, "DS8_U":0.999850163}

    ALPHAS_4T = {"DS1_U":0.9985024, "DS2_U":0.9985024, "DS3_U":0.9990015, "DS4_U":0.9990015, 
                 "DS5_U":0.999251, "DS6_U":0.999251, "DS7_U":0.99940076, "DS8_U":0.99940076}
    
    ALPHAS_8T = {"DS1_U":0.997007, "DS2_U":0.997007, "DS3_U":0.998004, "DS4_U":0.998004, 
                 "DS5_U":0.9985024, "DS6_U":0.9985024, "DS7_U":0.9988018, "DS8_U":0.9988018}

    ALPHAS = {1:ALPHAS_1T, 4:ALPHAS_4T, 8:ALPHAS_8T}

    AS_T_INI = 6.1
    SEGMENT = 350
    R = 0.05
    BETA = 0.15

    '''
    Pmax = 90%      // Pmax = 85%
    T_INI = 9.4     // T_INI = 6.1

    Pmin = 5%
    T_END = 0.0034
    '''

    T_INI = 6.1
    T_END = 0.0034
    N_JOBS = 4
    N_NEIGHBORS = 4

    ls_params = {"iter":ITER, "init":init_deployment, "oper":oper}
    sa_params = {"t_ini":T_INI, "t_end":T_END, "alpha":ALPHAS, "n_neighbors":N_NEIGHBORS, "init":init_deployment, "oper":oper}
    sac_params = {"t_ini":T_INI, "t_end":T_END, "alpha":ALPHAS, "n_neighbors":N_NEIGHBORS, "init":init_deployment, "oper":oper}
    sap_params = {"t_ini":T_INI, "t_end":T_END, "alpha":ALPHAS, "n_jobs":N_JOBS, "init":init_deployment, "oper":oper}
    alnsth_params = {"iter":ITER, "segment":SEGMENT, "r":R, "init":init_deployment, "oper":oper, "beta":BETA}
    alnstp_params = {"iter":ITER, "segment":SEGMENT, "r":R, "t_ini":AS_T_INI, "alpha":ALPHAS_1T, "init":init_deployment, "oper":oper}
    alnstb_params = {"iter":ITER, "segment":SEGMENT, "r":R, "t_ini":AS_T_INI, "alpha":ALPHAS_1T, "init":init_deployment, "oper":oper}
    parameters = {"LS":ls_params, "SA":sa_params, "SA-C":sac_params, "SA-P":sap_params, "ALNS-TH":alnsth_params, "ALNS-TP":alnstp_params, "ALNS-TB":alnstb_params, "init":init_deployment, "oper":oper}

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
    
    algorithms = ["LS", "SA", "SA-C", "SA-P", "ALNS-TH", "ALNS-TP", "ALNS-TB"]
    print("Algorithms available:", ', '.join(algorithms))
    alg_selected = list(map(int, input("Selected algorithms: ").split()))
    alg_selected = [algorithms[i-1] for i in alg_selected]

    nruns = int(input("Number of runs: "))
    notes = input("Notes: ")
    
    date = str(datetime.datetime.now())
    date = date.replace(" ", "--")
    for alg in alg_selected:
        with open("results/" + alg + "/" + date, "a") as f:
            print(" --- RESULTS --- ", file = f)
            print("Dataset topology: ", ds_kind, file = f)
            print("Runs per dataset: ", nruns, file = f)
            print("Algorithm: ", alg, file = f)
            
            if "SA" in alg:
                print("t_ini: ", T_INI, file = f)
                print("t_end: ", T_END, file = f)
                if alg == "SA-P":
                    print("n_jobs: ", N_JOBS, file = f)
                else:
                    print("n_neighbors: ", N_NEIGHBORS, file = f)
            
            if alg == "ALNS-TP" or alg == "ALNS-TB":
                print("t_ini: ", T_INI, file = f)
            
            print("Notes: ", notes, "\n", file = f)

    results = {}
    print("--- SIMULATION ---")
    for alg in alg_selected:
        print("Current algorithm: ", alg)
                        
        for ds in ds_selected:
            print("     Current dataset: ", ds)
            print("     Evaluations: ", ITER[ds])
            if "SA" in alg:
                if alg == "SA-C" or alg == "SA":
                    print("     Alpha: ", ALPHAS[N_NEIGHBORS][ds])
                else:
                    print("     Alpha: ", ALPHAS[N_JOBS][ds])
            elif alg == "ALNS-TP" or alg == "ALNS-TB":
                print("     Alpha: ", ALPHAS_1T[ds])

            instance = Instance()
            instance.loadInstance(file = ds, path = path)
            
            objectives = []
            split_objectives = []
            runtimes = []
            solutions = []

            for i in range(nruns):
                best_solution, best_objective, runtime = algorithm(algorithm = alg, dataset = ds, parameters = parameters[alg], instance = instance)

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