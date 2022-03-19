import sys
sys.path.insert(0, './src')
from instance import Instance
from algorithms import *
import time


if __name__ == "__main__":

    ins = Instance()
    ins.loadInstance(file = "DS2_U", path = "data/uniform/")
    oper = [downgradeCells, upgradeCells]
    init = True

    t_ini = time.time()
    #solution_ls, objective_ls = localSearch(problem_instance = ins, iter = 15000, oper = oper, init = init)
    solution_sa, objective_sa = simulatedAnnealingTABU(problem_instance = ins, oper = oper, init = init, T_ini = 6, T_end=0.0001, n_neighbors = 3, alpha=0.999)
    #solution_as, objective_as = adaptiveSearchTemperature(problem_instance = ins, oper = oper, init = init, iter = 15000, segment = 350, r = 0.05, T_ini = 6, T_end=0.0001, alpha = 0.9995)
    #solution_as, objective_as = adaptiveSearch(problem_instance = ins, oper = oper, init = init, iter = 15000, segment = 250, r = 0.1)
    t_end = time.time()

    print("Runtime: ", t_end - t_ini)

    debug = Deployment(instance = ins)
    print(" --- INITIAL SOLUTION DEBUG ---")
    debug.test()
    print("Initial solution: ", ins.generateInitDeployment())
    
    '''
    print(" --- BEST SOLUTION DEBUG SA --- ")
    solution_sa.test()
    print("Best solution found SA: ", solution_sa)

    print(" --- BEST SOLUTION DEBUG LS --- ")
    solution_ls.test()
    print("Best solution found LS: ", solution_ls)
    '''
    print(" --- BEST SOLUTION DEBUG ALNS --- ")
    solution_as.test()
    print("Best solution found ALNS: ", solution_as)