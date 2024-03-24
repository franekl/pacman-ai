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
        Entity.__init__(self, node)
        self.name = PACMAN    
        self.color = YELLOW
        self.direction = LEFT
        self.setBetweenNodes(LEFT)
        self.alive = True
        self.sprites = PacmanSprites(self)
        self.nodes = nodes
        self.directionMethod = self.goalDirectionDij 
        self.pellets = pellets.getPellets()


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
        print(f"self_node: {self.node}")
        print(f"self_target: {self.target}")
        print(f"self_position: {self.position}")
        if self.overshotTarget():
            print("TARGET OVERSHOT - PACMAN")
            
            if self.node.neighbors[PORTAL] is not None:
                self.node = self.node.neighbors[PORTAL]
            directions = self.validDirections()
            direction = self.goalDirectionDij(directions=directions)
            self.node = self.target
            self.target = self.getNewTarget(direction)
            if self.target is not self.node:
                self.direction = direction
            else:
                self.target = self.getNewTarget(self.direction)

            if self.target is self.node:
                self.direction = STOP
            self.setPosition()
        # else: 
        #     directions = self.validDirections()
        #     direction = self.goalDirectionDij(directions=directions)
        #     if self.oppositeDirection(direction):
        #         self.reverseDirection()

    def getDijkstraPath(self):
        # lastGhostNode = self.ghost.target
        # lastGhostNode = self.nodes.getVectorFromLUTNode(lastGhostNode)
        pacmanNode = (self.node.x, self.node.y)
        pacmanTarget = (self.target.x, self.target.y)
        # pacmanTarget = self.nodes.getVectorFromLUTNode(pacmanTarget)
        previous_nodes, shortest_path = dijkstra(self.nodes, pacmanTarget, self.pellets)
        path = []

        min_weight_node = None
        min_weight = float('inf')
        for node, weight in shortest_path.items():
            if node != pacmanNode:
                if weight < min_weight and weight > 0:
                    min_weight = weight
                    min_weight_node = node

        while min_weight_node != pacmanTarget:
            # print("Is equal: ", min_weight_node, pacmanTarget)
            path.append(min_weight_node)
            min_weight_node = previous_nodes[min_weight_node]
        path.append(pacmanTarget)
        path.reverse()
        # print(path)
        return path


    # Chooses direction in which to turn based on the dijkstra
    # returned path
    def goalDirectionDij(self, directions):
        path = self.getDijkstraPath()
        print(f"\nPATH: {path}")
        pacman_start = self.target
        pacman_start = self.nodes.getVectorFromLUTNode(pacman_start)


        nextMoveNode = path[1]
        print(f"NEXT MOVE NODE: {nextMoveNode}, PACMAN START: {pacman_start}")

        if pacman_start[0] > nextMoveNode[0] and 2 in directions : #left
            return 2
        if pacman_start[0] < nextMoveNode[0] and -2 in directions : #right
            return -2
        if pacman_start[1] > nextMoveNode[1] and 1 in directions : #up
            return 1
        if pacman_start[1] < nextMoveNode[1] and -1 in directions : #down
            return -1
        else: 
            print("random choice decision activated")
            return choice(directions)
        # else:
        #     # print(f"Else activated, self pacman direction: {self.ghost.direction}")
        #     # print(f"Directions -> {directions}")
        #     if -1 * self.ghost.direction in directions:
        #         return -1 * self.ghost.direction
        #     else: 
        #         return choice(directions)
        
        # up 1, down -1, left 2, right -2

    def eatPellets(self, pelletList):
        for pellet in pelletList:
            # print(pellet.position)
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

    def eatenPellet(self, pellet):
        self.pellets.remove((pellet.y, pellet.x))
        print(f"Pellets left: {len(self.pellets)}")
        print(f"REMOVED {pellet}")

