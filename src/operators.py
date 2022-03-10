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
    downgrade_idx = current_solution.getNonNullCells()

    if downgrade_idx:
       idx = random.choice(downgrade_idx)
       curr_cell = current_solution[idx]
       elegible_cells = [cell for cell in current_solution.instance().cells_ids if cell < curr_cell]
       elegible_cells.append(0)

       neighbor[idx] = random.choice(elegible_cells)
    
    return neighbor

def swapCells(current_solution):
    # Given a solution, it will swap two random cells. It will ensure at least one of them is non-null.
    neighbor = current_solution.copy()
    nnull_idx = current_solution.getNonNullCells()
    if nnull_idx:
        idxA = random.choice(nnull_idx)
        idxB = random.choice([i for i in range(current_solution.instance().ncandidates) if i != idxA])

        neighbor[idxA] = current_solution[idxB]
        neighbor[idxB] = current_solution[idxA]

    return neighbor

def deployConnected(current_solution):
    # Given a solution, it will insert a small cell in the boundaries of a deployed cell's range
    neighbor = current_solution.copy()
    nnull_idx = current_solution.getNonNullCells()
    null_idx = current_solution.getNullCells()
    cells = current_solution.instance().cells_ids[1:]

    if nnull_idx:
        for idx in nnull_idx:
            cell_range = current_solution.instance().cells[current_solution[idx]][1]
            cell_dist = current_solution.instance().dmatrix_candidates[idx]
            
            in_range = [n_idx for n_idx in null_idx if cell_dist[n_idx] <= cell_range]
            if not in_range:
                continue     
            
            in_range_d = [cell_dist[i] for i in in_range]
            f_idx = in_range[in_range_d.index(max(in_range_d))]
            neighbor[f_idx] = random.choice(cells)
            break
    
    return neighbor

def deployMacrocell(current_solution):
    # Given a solution, it will deploy a macrocell in a random location to improve conectivity
    neighbor = current_solution.copy()
    null_idx = current_solution.getNullCells()
    if null_idx:
        neighbor[random.choice(null_idx)] = neighbor.instance().macro_id
    
    return neighbor


if __name__ == "__main__":
    ins = Instance()
    ins.loadInstance(file = "DS1", visualization = True)

    sol = Deployment(instance = ins)
    print(sol)
    print(upgradeCells(sol))
    print(downgradeCells(sol))
    print(swapCells(sol))
    print(deployConnected(sol))
    print(deployMacrocell(sol))