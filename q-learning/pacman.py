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
    def __init__(self, node, nodes, pellets, mode='train', q_tab_path='qt.pkl'):
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

        self.q_tab_path = q_tab_path
        self.mode = mode
        self.q_table = {}
        self.epsilon = 1.0 if mode == 'train' else 0.0 
        self.alpha = 0.1  
        self.gamma = 0.9  
        if os.path.exists(q_tab_path):
            with open(q_tab_path, 'rb') as f:
                self.q_table = pickle.load(f)
        

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
        # print(f"Pacman tile: {pacman_tile}, Ghost positions: {ghost_positions}")
        min_distance = self.bfs_distance(pacman_tile, ghost_positions)
        # print(f"Nearest ghost distance: {min_distance}")
        return min_distance

    def getNearestPelletDistance(self, pacman_tile):
        pellet_positions = [(int(pellet.position.x), int(pellet.position.y)) for pellet in self.pellets]
        # print(f"Pacman tile: {pacman_tile}, Pellet positions: {pellet_positions}")
        min_distance = self.bfs_distance(pacman_tile, pellet_positions)
        # print(f"Nearest pellet distance: {min_distance}")
        return min_distance

    def getState(self):
        pacman_tile = (int(self.node.position.x), int(self.node.position.y))

        nearest_pellet_distance = self.getNearestPelletDistance(pacman_tile)
        nearest_ghost_distance = self.getNearestGhostDistance(pacman_tile)
        # print(f"Nearest ghost distance: {nearest_ghost_distance}")
        ghosts_in_fright_mode = any(ghost.mode.current == FREIGHT for ghost in self.ghosts)
    
        return (ghosts_in_fright_mode, nearest_pellet_distance, nearest_ghost_distance)


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

    def getReward(self):
        reward = -1
        if self.direction != self.previous_direction:
            # print("PENALTY FOR CHANGING DIRECTIONS APPLIED -5")
            reward -= 5

        for ghost in self.ghosts:
            if self.collideGhost(ghost):
                # print("PENALTY FOR GHOST COLLISSION -500")
                reward -= 500
        pellet = self.eatPellets(self.pellets)
        if pellet:
            # print("+10 for eating a pellet")
            reward += 10
        return reward
    
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

    def update(self, dt):

        self.sprites.update(dt)
        self.position += self.directions[self.direction] * self.speed * dt
        reward = self.getReward()        
        if self.overshotTarget():

            self.node = self.target
            if self.node.neighbors[PORTAL] is not None:
                self.node = self.node.neighbors[PORTAL]
                self.setPosition()
                self.target = self.getNewTarget(self.direction)
            state = self.getState()
            action = self.chooseAction(state)
            self.executeAction(action)
            new_state = self.getState()
            # reward = self.getReward()
            # print(f"State: {state}, Action: {action}, New State: {new_state}, Reward: {reward}")
            print(f"Updating Q-Table with State: {state}, Action: {action}, New State: {new_state}, Reward: {reward}")
            self.updateQTable(state, action, reward, new_state)
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
            # print("EATING PELLET")
            # print(f"Pellets left: {len(self.pellets)}")
            self.pellets.remove(pellet_to_remove)
            # print(f"REMOVED {pellet_to_remove}")
        
    def collideGhost(self, ghost):
        collision = self.collideCheck(ghost)
        if collision:
            print(f"Collision detected with ghost at position {ghost.position}")
        return collision

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
