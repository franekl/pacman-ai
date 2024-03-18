import pygame
from pygame.locals import *
from vector import Vector2
from constants import *
from entity import Entity
from sprites import PacmanSprites
from algorithms import *

class Pacman(Entity):
    def __init__(self, node, nodes):
        Entity.__init__(self, node )
        self.name = PACMAN    
        self.color = YELLOW
        self.direction = LEFT
        self.setBetweenNodes(LEFT)
        self.alive = True
        self.sprites = PacmanSprites(self)
        self.nodes = nodes

    def reset(self):
        Entity.reset(self)
        self.direction = LEFT
        self.setBetweenNodes(LEFT)
        self.alive = True
        self.image = self.sprites.getStartImage()
        self.sprites.reset()

    def setGhostGroup(self, ghosts):
        self.ghosts = ghosts

    def die(self):
        self.alive = False
        self.direction = STOP

    def update(self, dt):	
        self.sprites.update(dt)
        self.position += self.directions[self.direction]*self.speed*dt
        # direction = self.getValidKey()
        direction = self.findPathToNearestPellet()
        if self.overshotTarget():
            self.node = self.target
            if self.node.neighbors[PORTAL] is not None:
                self.node = self.node.neighbors[PORTAL]
            self.target = self.getNewTarget(direction)
            if self.target is not self.node:
                self.direction = direction
            else:
                self.target = self.getNewTarget(self.direction)

            if self.target is self.node:
                self.direction = STOP
            self.setPosition()
        else: 
            if self.oppositeDirection(direction):
                self.reverseDirection()


    def findPathToNearestPellet(self):
        previous_nodes, shortest_path = dijkstra(self.nodes, self.node)
        nearest_pellet = None
        min_path_len = float('inf')

        for pellet in self.pellets:
            if pellet in shortest_path and shortest_path[pellet] < min_path_len:
                nearest_pellet = pellet
                min_path_len = shortest_path[pellet]

        if nearest_pellet is None:
            return None  # No path found

        # Backtrack from nearest pellet to start node to find path
        path = []
        current_node = nearest_pellet
        while current_node != self.node:
            path.insert(0, current_node)
            current_node = previous_nodes[current_node]
        # No need to insert the start_node in path as it's Pacman's current node

        if path:
            # Calculate direction to the first node in the path
            next_node_direction = self.calculateDirection(path[0])
            return next_node_direction
        else:
            return None


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
            if self.collideCheck(pellet):
                return pellet
        return None    
    
    def collideGhost(self, ghost):
        return self.collideCheck(ghost)

    def collideCheck(self, other):
        d = self.position - other.position
        dSquared = d.magnitudeSquared()
        rSquared = (self.collideRadius + other.collideRadius)**2
        if dSquared <= rSquared:
            return True
        return False

    def get_dijkstra_distance(self, ghost):
        pass