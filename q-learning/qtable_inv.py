#%%
import pandas as pd
import pickle


#%%
#load pickled file
with open('qt.pkl', 'rb') as f:
    q_table = pickle.load(f)
# %%
q_table
# %%
def getGrid(maze_file):
    """
    Create a grid representation of the maze where 0 is an empty cell and 1 is a wall.
    :param maze_file: path to the maze file
    :return: 2D list grid representation of the maze
    """
    with open(maze_file, 'r') as file:
        lines = file.readlines()
        
    grid = []
    for line in lines:
        row = []
        for char in line.strip():
            if char in {'X', 'n', '|', '=', '-', 'P'}:  # Assuming these are walls or portals
                row.append(1)
            else:
                row.append(0)
        grid.append(row)
    
    return grid

getGrid("maze1.txt")
# %%
