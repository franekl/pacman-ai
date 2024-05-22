import pygame
from pygame.locals import *
from vector import Vector2
from constants import *
from entity import Entity
from sprites import PacmanSprites
import numpy  as np
import os

class Pacman(Entity):
    def __init__(self, node, nodes, pellets, mode='train', q_tab_path='qt.npy'):
        Entity.__init__(self, node )
        self.name = PACMAN    
        self.color = YELLOW
        self.direction = LEFT
        self.setBetweenNodes(LEFT)
        self.alive = True
        self.nodes = nodes
        self.sprites = PacmanSprites(self)
        self.pellets = pellets.getPellets()
        self.actions = [UP, DOWN, LEFT, RIGHT, STOP]
        self.q_tab_path = q_tab_path
        self.mode = mode
        self.q_table = np.zeros((28, 33, len(self.actions)))
        self.epsilon = 1.0 if mode == 'train' else 0.0 
        self.alpha = 0.1  
        self.gamma = 0.9  
        if os.path.exists(q_tab_path):
            self.q_table = np.load(q_tab_path)
        

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

    def getState(self):
        pacman_tile = self.node.position
        ghost_tiles = tuple(ghost.node.position for ghost in self.ghosts)
        return (pacman_tile, ghost_tiles)
    
    def chooseAction(self, state):
        if np.random.rand() < self.epsilon:
            return np.random.choice(self.actions)
        else:
            state_index = self.state_to_index(state)
            return np.argmax(self.q_table[state_index])
        
    def executeAction(self, action):
        if self.validDirection(action):
            self.direction = action

    def getReward(self):
        reward = -1
        for ghost in self.ghosts:
            if self.collideGhost(ghost):
                reward -= 500
        pellet = self.eatPellets(self.pellets)
        if pellet:
            reward += 10
        return reward
    
    def updateQTable(self, state, action, reward, new_state):
        state_index = self.state_to_index(state)
        new_state_index = self.state_to_index(new_state)
        self.q_table[state_index, action] = (self.q_table[state_index, action] +
                                             self.alpha * (reward + self.gamma * np.max(self.q_table[new_state_index]) - self.q_table[state_index, action]))

    def state_to_index(self, state):
        pacman_tile, ghost_tiles = state
        pacman_index = pacman_tile[0] + pacman_tile[1]
        ghost_indices = [ghost[0] + ghost[1] for ghost in ghost_tiles]
        return (pacman_index, tuple(ghost_indices))

    
    def save_q_table(self):
        np.save(self.q_tab_path, self.q_table)
    
    def update(self, dt):	
        self.sprites.update(dt)
        self.position += self.directions[self.direction]*self.speed*dt
        state = self.getState()
        action = self.chooseAction(state)
        self.executeAction(action)
        new_state = self.getState()
        reward = self.getReward()
        self.updateQTable(state, action, reward, new_state)
        if self.overshotTarget():
            self.node = self.target
            pacman_tile, ghost_tiles = self.getState()
            print(f"PACMAN TILE: {pacman_tile}; GHOST TILES: {ghost_tiles[0]}")
            if self.node.neighbors[PORTAL] is not None:
                self.node = self.node.neighbors[PORTAL]
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

    def getValidKey(self):
        key_pressed = pygame.key.get_pressed()
        if key_pressed[K_UP]:
            return UP
        if key_pressed[K_DOWN]:
            return DOWN
        if key_pressed[K_LEFT]:
            return LEFT
        if key_pressed[K_RIGHT]:
            return RIGHT
        return STOP  

    def eatPellets(self, pelletList):
        for pellet in pelletList:
            print(pellet, type(pellet))
            if self.collideCheck(pellet):
                return pellet
        return None  

    def eatenPellet(self, pellet):
        self.pellets.remove((pellet.y, pellet.x))
        # print(f"Pellets left: {len(self.pellets)}")
        # print(f"REMOVED {pellet}")  
    
    def collideGhost(self, ghost):
        return self.collideCheck(ghost)

    def collideCheck(self, other):
        # print(self.position, other)
        # print(self.position, other.position)
        d = self.position - other.position
        dSquared = d.magnitudeSquared()
        rSquared = (self.collideRadius + other.collideRadius)**2
        if dSquared <= rSquared:
            return True
        return False

    def validDirection(self, direction):
        if self.target is not None and direction in self.target.access:
            if self.target.neighbors[direction] is not None:
                return True
        return False

    
    def is_ghost_ahead(self):
        # checks whether the ghost is heading into pacman's direction and pacman's heading into ghost's direction 
        # basically checks for collision

        for ghost in self.ghosts:

            # check horizontal alignment and opposite directions
            align_horizontally = self.position.y == ghost.position.y
            opp_dir_horizontally = ((self.direction == LEFT and ghost.direction == RIGHT) or
                                                (self.direction == RIGHT and ghost.direction == LEFT))

            # check vertical alignment and opposite directions
            align_vertically = self.position.x == ghost.position.x
            opp_dir_vertically = ((self.direction == UP and ghost.direction == DOWN) or
                                            (self.direction == DOWN and ghost.direction == UP))

            if ((align_horizontally and opp_dir_horizontally) or
                (align_vertically and opp_dir_vertically)):
                    return True
        return False
    