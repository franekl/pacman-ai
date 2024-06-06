import pygame
from pygame.locals import *
from vector import Vector2
from constants import *
from entity import Entity
from sprites import PacmanSprites
import numpy  as np
import os
import pickle
import math
from collections import deque


### FEATURE EXTRACTION ###

# - are ghosts in fright mode
# - distance to the closest pellet (mn)
# - distance to the closest ghost (mn)
# - number of ghosts 1 step away
# - number of ghosts 2 steps away


class Pacman(Entity):
    def __init__(self, node, nodes, pellets, mode='train', q_tab_path='qt.pkl', epsilon=1.0):
        Entity.__init__(self, node )
        self.name = PACMAN    
        self.color = YELLOW
        self.direction = LEFT
        self.setBetweenNodes(LEFT)
        self.previous_direction = LEFT
        self.previous_state = None
        self.previous_action = None
        self.alive = True
        self.nodes = nodes
        self.sprites = PacmanSprites(self)
        self.pellets = pellets.getPellets()
        self.actions = [UP, DOWN, LEFT, RIGHT, STOP]
        self.setSpeed(200)
        self.current_tile = (int(self.node.position.x // TILEWIDTH), int(self.node.position.y // TILEHEIGHT))
        self.accumulated_reward = -1
        self.collided_with_ghost = False
        self.collided_with_ghost_in_fright_mode = False
        self.eaten_pellet = False
        self.reversed_direction = False

        self.q_tab_path = q_tab_path
        self.mode = mode
        self.q_table = {}
        self.epsilon = epsilon if mode == 'train' else 0.0 
        print(f"NEW EPSILON: {self.epsilon}")
        self.alpha = 0.2  
        self.gamma = 0.9  
        if os.path.exists(q_tab_path):
            with open(q_tab_path, 'rb') as f:
                self.q_table = pickle.load(f)

        print(len(self.q_table))
        self.action_names = {
                0: "STOP",
                1: "UP",
                -1: "DOWN",
                2: "LEFT",
                -2: "RIGHT",
                3: "PORTAL"
            }
        

    def setGhostGroup(self, ghosts):
        self.ghosts = ghosts

    def reset(self):
        Entity.reset(self)
        self.direction = LEFT
        self.setBetweenNodes(LEFT)
        self.alive = True
        self.image = self.sprites.getStartImage()
        self.sprites.reset()

    def die(self):
        self.alive = False
        self.direction = STOP


    ### FEATURES ####


    ### TESTING PHASE 
    def bfs_distance(self, start, targets, debug=False):
        queue = deque([(start, 0)])
        visited = set()
        visited.add(start)
        if debug:
            print(f"BFS started from {start} to targets {targets}")

        while queue:
            current, dist = queue.popleft()
            if debug:
                print(f"Visiting: {current}, Distance: {dist}")
            if current in targets:
                if debug:
                    print(f"Target {current} found at distance {dist}")
                return dist

            neighbors = self.nodes.getNeighbors(current)
            for neighbor in neighbors:
                if neighbor not in visited:
                    visited.add(neighbor)
                    queue.append((neighbor, dist + 1))
                    if debug:
                        print(f"Neighbor {neighbor} added to queue with distance {dist + 1}")

        return float('inf')
    
    def getNearestGhostDistance(self, pacman_tile):
        ghost_positions = [(int(ghost.node.x), int(ghost.node.y)) for ghost in self.ghosts]
        min_distance = self.bfs_distance(pacman_tile, ghost_positions)
        return min_distance, self.getDirectionToNearest(pacman_tile, ghost_positions)

    def getNearestPelletDistance(self, pacman_tile):
        pellet_positions = [(int(pellet.position.x), int(pellet.position.y)) for pellet in self.pellets]
        min_distance = self.bfs_distance(pacman_tile, pellet_positions)
        return min_distance, self.getDirectionToNearest(pacman_tile, pellet_positions)

    def getBinnedDistance(self, distance, bins):
        for b in bins:
            if distance <= b:
                return b
        return bins[-1]

    def getDirectionToNearest(self, start, targets):
        queue = deque([(start, None)])  # Store direction as well
        visited = set()
        visited.add(start)

        while queue:
            current, first_dir = queue.popleft()
            if current in targets:
                return first_dir

            neighbors = self.nodes.getNeighbors(current)
            for neighbor in neighbors:
                if neighbor not in visited:
                    visited.add(neighbor)
                    if first_dir is None:
                        direction = self.getDirection(current, neighbor)
                    else:
                        direction = first_dir
                    queue.append((neighbor, direction))

        return STOP  # If no path found

    def getDirection(self, start, end):
        if start[0] < end[0]:
            return RIGHT
        elif start[0] > end[0]:
            return LEFT
        elif start[1] < end[1]:
            return DOWN
        elif start[1] > end[1]:
            return UP
        return STOP

    def getState(self):
        pacman_tile = (int(self.node.position.x), int(self.node.position.y))
        nearest_pellet_distance, pellet_direction = self.getNearestPelletDistance(pacman_tile)
        nearest_ghost_distance, ghost_direction = self.getNearestGhostDistance(pacman_tile)
        
        pellet_bins = [1,2,3,4,5,6,7, 8, 9, 10, 15, 30, 45]
        ghost_bins = [1,2,3,4,5,6,7, 8, 9, 10, 15, 30, 45]
        
        binned_pellet_distance = self.getBinnedDistance(nearest_pellet_distance, pellet_bins)
        binned_ghost_distance = self.getBinnedDistance(nearest_ghost_distance, ghost_bins)
        
        state = (binned_pellet_distance, binned_ghost_distance, pellet_direction, ghost_direction)
        return state
    
    
   

    ###
    # def manhattanDistance(self, tile1, tile2):
    #     return abs(tile1[0] - tile2[0]) + abs(tile1[1] - tile2[1]) // TILEWIDTH
    
    
    # def getNearestGhostDistance(self, pacman_tile):
    #     distances = [self.manhattanDistance(pacman_tile, (ghost.position.x, ghost.position.y)) for ghost in self.ghosts]
    #     # print(sorted(distances)[0])
    #     return min(distances) if distances else float('inf')

    # def getNearestPelletDistance(self, pacman_tile):
    #     distances = [self.manhattanDistance(pacman_tile, (int(pellet.position.x), int(pellet.position.y))) for pellet in self.pellets]
        
    #     return min(distances) if distances else float('inf')

    # def euclideanDistance(self, pos1, pos2):
    #     dx = pos1[0] - pos2[0]
    #     dy = pos1[1] - pos2[1]
    #     return math.sqrt(dx * dx + dy * dy) // TILEWIDTH

    # def getNearestGhostDistance(self, pacman_tile):
    #     distances = [self.euclideanDistance(pacman_tile, (ghost.target.x, ghost.target.y)) for ghost in self.ghosts]
    #     # print(min(distances))
    #     return min(distances) if distances else float('inf')

    # def getNearestPelletDistance(self, pacman_tile):
    #     distances = [self.euclideanDistance(pacman_tile, (int(pellet.position.x), int(pellet.position.y))) for pellet in self.pellets]
    #     # print(min(distances))
    #     return min(distances) if distances else float('inf')

    def getStateActionKey(self, state, action):
        return (state, action)
    
    def executeAction(self, action):
        if self.validDirection(action):
            self.previous_direction = self.direction 
            self.direction = action
        else:
            self.direction = STOP

    def chooseAction(self, state):
        valid_actions = [action for action in self.actions if self.validDirection(action)]
        
        if not valid_actions:
            valid_actions = [STOP] 
        
        if np.random.rand() < self.epsilon:
            return np.random.choice(valid_actions)
        else:
            state_actions = [(action, self.q_table.get(self.getStateActionKey(state, action), 0)) for action in valid_actions]
            max_value = max(state_actions, key=lambda x: x[1])[1]
            best_actions = [action for action, value in state_actions if value == max_value]
            
            if self.direction in best_actions:
                return self.direction
            else:
                return np.random.choice(best_actions)
    
    def updateQTable(self, state, action, reward, new_state):
        state_action_key = self.getStateActionKey(state, action)
        next_state_values = [self.q_table.get(self.getStateActionKey(new_state, a), 0) for a in self.actions]
        self.q_table[state_action_key] = self.q_table.get(state_action_key, 0) + self.alpha * (
            reward + self.gamma * max(next_state_values) - self.q_table.get(state_action_key, 0)
        )

    def state_to_index(self, state):
        pacman_tile, ghost_tiles = state
        pacman_index = (int(pacman_tile.x), int(pacman_tile.y))
        ghost_indices = tuple((int(ghost.x), int(ghost.y)) for ghost in ghost_tiles)
        return (pacman_index, ghost_indices)
    
    def save_q_table(self):
        with open(self.q_tab_path, 'wb') as f:
            pickle.dump(self.q_table, f)

    def oppositeDirection_ques(self, direction):
        opposite_directions = {UP: DOWN, DOWN: UP, LEFT: RIGHT, RIGHT: LEFT}
        return self.previous_direction == opposite_directions.get(direction, None)

    def update(self, dt):

        self.sprites.update(dt)
        self.position += self.directions[self.direction] * self.speed * dt

        if self.oppositeDirection_ques(self.direction):
                self.reversed_direction = True
        for ghost in self.ghosts:
            if self.collideGhost(ghost):
                # if ghost.mode.current == FREIGHT:
                    # self.collided_with_ghost_in_fright_mode = True
                # else:
                    self.collided_with_ghost = True

        if self.eatPellets(self.pellets):
            self.eaten_pellet = True

        if self.overshotTarget():
        # Calculate reward for the previous state-action pair
            reward = self.accumulated_reward
            

            if self.reversed_direction:
                reward -= 6
            if self.collided_with_ghost:
                reward -= 350
            # if self.collided_with_ghost_in_fright_mode:
            #     reward += 20
            if self.eaten_pellet:
                reward += 12

            if self.previous_state is not None and self.previous_action is not None:
                action_name = self.action_names.get(self.previous_action, "UNKNOWN")
                new_state = self.getState()
                # print(f"TILE: {self.node.position}, State: {self.previous_state}, Action: {action_name}, New State: {new_state}, Accumulated Reward: {reward}")
                self.updateQTable(self.previous_state, self.previous_action, reward, new_state)


            # Reset accumulated rewards and flags
            self.accumulated_reward = -5
            self.collided_with_ghost = False
            self.collided_with_ghost_in_fright_mode = False
            self.eaten_pellet = False
            self.reversed_direction = False

            # Update the node and target
            self.node = self.target
            if self.node.neighbors[PORTAL] is not None:
                self.node = self.node.neighbors[PORTAL]
                self.setPosition()
                self.target = self.getNewTarget(self.direction)

            # Determine new state and choose action
            new_state = self.getState()
            action = self.chooseAction(new_state)
            self.executeAction(action)

            # Store the new state and action as previous for the next iteration
            self.previous_state = new_state
            self.previous_action = action

            self.target = self.getNewTarget(self.direction)
            if self.target is not self.node:
                self.direction = self.direction
            else:
                self.target = self.getNewTarget(self.direction)

            if self.target is self.node:
                self.direction = STOP
            self.setPosition()
        else:
            if self.oppositeDirection(self.direction):
                self.reverseDirection()




    def eatPellets(self, pelletList):
        for pellet in pelletList:
            if self.collideCheck(pellet):
                # print("EATING PELLET", pellet)
                self.eatenPellet(pellet)
                return pellet
        return None  
    
    def eatenPellet(self, pellet):
        pellet_to_remove = next((p for p in self.pellets if (int(p.position.x), int(p.position.y)) == (int(pellet.position.x), int(pellet.position.y))), None)

        if pellet_to_remove:
            self.pellets.remove(pellet_to_remove)
            self.eaten_pellet = True
            # print(f"Eating Pellet at position {pellet.position}")
        
    def collideGhost(self, ghost):
        if self.collideCheck(ghost): 
            self.collided_with_ghost = True
            # print(f"Collision detected with ghost at position {ghost.position}")
            return True
        return False
    

    def collideCheck(self, other):
        # print(self.position, other)
        # print(self.position, other.position)
        d = self.position - other.position
        dSquared = d.magnitudeSquared()
        rSquared = (self.collideRadius + other.collideRadius)**2
        if dSquared <= rSquared:
            # print("COLLISSION")
            return True
        return False
    

    def validDirection(self, direction):
        if direction is not STOP:
            if self.name in self.target.access[direction]:
                if self.target.neighbors[direction] is not None:
                    return True
        return False
