from instance import Instance
from deployment import Deployment
import copy
import random

def upgradeCells(current_solution):
    # Given a solution, it will upgrade a cell to a bigger one if possible
    neighbor = current_solution.copy()
    upgrade_idx = [i for i in range(current_solution.instance().ncandidates) if current_solution[i] != current_solution.instance().macro_id]

    if upgrade_idx:
       idx = random.choice(upgrade_idx)
       curr_cell = current_solution[idx]
       elegible_cells = [cell for cell in current_solution.instance().cells_ids if cell > curr_cell]

       neighbor[idx] = random.choice(elegible_cells)
    
    return neighbor

def downgradeCells(current_solution):
    # Given a solution, it will downgrade a cell to a smaller one if possible
    neighbor = current_solution.copy()
    downgrade_idx = [i for i in range(current_solution.instance().ncandidates) if current_solution[i] != 0]

    if downgrade_idx:
       idx = random.choice(downgrade_idx)
       curr_cell = current_solution[idx]
       elegible_cells = [cell for cell in current_solution.instance().cells_ids if cell < curr_cell]
       elegible_cells.append(0)

       neighbor[idx] = random.choice(elegible_cells)
    
    return neighbor



if __name__ == "__main__":
    ins = Instance()
    ins.loadInstance(file = "DS1", visualization = True)

    sol = Deployment(instance = ins)
    print(upgradeCells(sol))
    print(downgradeCells(sol))