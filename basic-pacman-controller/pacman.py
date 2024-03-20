import pygame
from pygame.locals import *
from vector import Vector2
from constants import *
from entity import Entity
from sprites import PacmanSprites
from algorithms import *
from random import choice
import sys

class Pacman(Entity):
    def __init__(self, node, nodes, pellets):
        Entity.__init__(self, node )
        self.name = PACMAN    
        self.color = YELLOW
        self.direction = LEFT
        self.setBetweenNodes(LEFT)
        self.alive = True
        self.sprites = PacmanSprites(self)
        self.nodes = nodes
        self.directionMethod = self.randomDirection 
        self.pellets = pellets

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
        directions = self.validDirections()
        # direction = self.directionMethod(directions=directions)
        direction = self.directionMethod(directions=directions)
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


    def goalDirection(self):
        # Find the closest pellet using the Dijkstra algorithm
        previous_nodes, _ = dijkstra(self.pellets, self.node)

        # Set the goal to the position of the closest pellet
        closest_pellet = None
        closest_distance = sys.maxsize
        for pellet in self.pellets:
            if pellet.node in previous_nodes:
                distance = previous_nodes[pellet.node]
                if distance < closest_distance:
                    closest_pellet = pellet
                    closest_distance = distance

        if closest_pellet:
            self.goal = self.nodes.getVectorFromLUTNode(closest_pellet.node)

        # Calculate the directions to the goal
        directions = []
        for direction in self.directions.values():
            vec = self.node.position + direction*TILEWIDTH - self.goal
            if vec.magnitudeSquared() < TILEWIDTH**2:
                directions.append(direction)

        # Choose the direction based on the Dijkstra path
        if closest_pellet:
            next_node = closest_pellet.node
            if self.node.position[0] > next_node.position[0] and 2 in directions:
                return 2
            if self.node.position[0] < next_node.position[0] and -2 in directions:
                return -2
            if self.node.position[1] > next_node.position[1] and 1 in directions:
                return 1
            if self.node.position[1] < next_node.position[1] and -1 in directions:
                return -1

        return choice(directions)

    # # Chooses direction in which to turn based on the dijkstra
    # # returned path
    # def goalDirectionDij(self, directions):
    #     path = self.getDijkstraPath(directions)
    #     print(f"\nPATH: {path}")
    #     pacmanTarget = self.target
    #     pacmanTarget = self.nodes.getVectorFromLUTNode(pacmanTarget)
    #     path.append(pacmanTarget)
    #     nextGhostNode = path[1]
    #     if pacmanTarget[0] > nextGhostNode[0] and 2 in directions : #left
    #         return 2
    #     if pacmanTarget[0] < nextGhostNode[0] and -2 in directions : #right
    #         return -2
    #     if pacmanTarget[1] > nextGhostNode[1] and 1 in directions : #up
    #         return 1
    #     if pacmanTarget[1] < nextGhostNode[1] and -1 in directions : #down
    #         return -1
    #     else:
    #         print(f"Else activated, self pacman direction: {self.ghost.direction}")
    #         print(f"Directions -> {directions}")
    #         if -1 * self.ghost.direction in directions:
    #             return -1 * self.ghost.direction
    #         else: 
    #             return choice(directions)
        
    #     # up 1, down -1, left 2, right -2



    # def goalDirection(self, directions):
    #     distances = []
    #     for direction in directions:
    #         vec = self.node.position  + self.directions[direction]*TILEWIDTH - self.goal
    #         distances.append(vec.magnitudeSquared())
    #     index = distances.index(max(distances))
    #     return directions[index]

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
            print(pellet.position)
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