
from entity import Entity


class Pacman(Entity):
    def __init__(self, node, nodes, pellets, mode='train', q_tab_path='qt.pkl', epsilon=1.0):
        ...
        self.q_table = {}
        self.epsilon = epsilon if mode == 'train' else 0.0 
        self.alpha = 0.2  
        self.gamma = 0.9  
        ...




        self.epsilon = 1.0
        self.epsilon_decay = 0.997
        self.min_epsilon = 0.05


def getState(self):
    pacman_tile = (int(self.node.position.x), int(self.node.position.y))
    nearest_pellet_distance, pellet_direction = self.getNearestPelletDistance(pacman_tile)
    nearest_ghost_distance, ghost_direction = self.getNearestGhostDistance(pacman_tile)
    ...
    state = (ghosts_in_fright_mode, binned_pellet_distance, binned_ghost_distance, pellet_direction, ghost_direction)
    return state

