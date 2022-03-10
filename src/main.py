from deployment import Deployment
from instance import Instance
from algorithms import *
import numpy as np
import time
import os
import datetime

if __name__ == "__main__":
    LSITER = 5000
    oper = [upgradeCells, downgradeCells]
    init_deployment = False

    path_ds = "./data/"
    ds_r = os.listdir(path_ds)
    datasets = [name for name in ds_r if "_coordinates" not in name]
    datasets.sort()

    print("Datasets available: ", datasets)
    nruns = int(input("Number of runs: "))
    algorithm = input("Algorithm: ")
    notes = input("Notes: ")

    results = {}

    for ds in datasets:
        print("Current dataset: ", ds)
        instance = Instance()
        instance.loadInstance(ds, visualization = True)
        
        objectives = []
        split_objectives = []
        runtimes = []
        solutions = []

        for i in range(nruns):

            tini = time.time()
            best_solution, best_objective = simulatedAnnealingTABU(problem_instance = instance, oper = oper, init = init_deployment)
            #best_solution, best_objective = localSearch(problem_instance = instance, iter = LSITER, oper = oper, init = init_deployment)
            tend = time.time()

            if not best_solution.isFeasible() or best_solution.objective() != best_objective:
                print("EXECUTION FAILED IN DATASET: ", ds)
                exit()
            
            solutions.append(best_solution)
            objectives.append(best_objective)
            split_objectives.append(best_solution.splitObjective())
            runtimes.append(tend - tini)

            print("     Iteration number:", i, "-", "Runtime:", tend - tini, "seconds")
        
        overall_obj = min(objectives)
        overall_sol = solutions[objectives.index(overall_obj)]
        split_res = list(map(np.mean, zip(*split_objectives)))
        results[ds] = [overall_sol, np.mean(objectives), np.std(objectives), split_res[0], split_res[1], split_res[2], np.mean(runtimes)]

    date = str(datetime.datetime.now())
    date = date.replace(" ", "--")
    with open("results/" + date, "w") as f:
        print(" --- RESULTS --- ", file = f)
        print("Runs per dataset: ", nruns, file = f)
        print("Algorithm: ", algorithm, file = f)
        print("Operators: ", oper, file = f)
        print("Initial deployment: ", init_deployment, file = f)
        print("Notes: ", notes, "\n", file = f)

        for ds in datasets:
            print(ds, ":", results[ds][1:], file = f)
        
        print("\n--- BEST FOUND SOLUTIONS --- \n", file = f)
        for ds in datasets:
            print(ds, ":", results[ds][0], file = f)
            


