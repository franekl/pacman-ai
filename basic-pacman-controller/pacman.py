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

    def get_path_weight(start_node, end_node, pellet_positions):
        # Simplified check; adapt based on your game's logic and geometry
        for pellet_pos in pellet_positions:
            if is_between(start_node.position, end_node.position, pellet_pos):
                return 1  # Path has pellets, lower cost
        return 100  # Path doesn't have pellets, higher cost

    # def getDijkstraPath(self, directions):
    #     pacmanTarget = self.target
    #     previous_nodes, shortest_path = dijkstra(self.nodes, pacmanTarget)
    #     path = []
    #     node = lastGhostNode
    #     while node != pacmanTarget:
    #         path.append(node)
    #         node = previous_nodes[node]
    #     path.append(pacmanTarget)
    #     path.reverse()
    #     # print(path)
    #     return path
    
    def update(self, dt):	
        self.sprites.update(dt)
        self.position += self.directions[self.direction]*self.speed*dt
        directions = self.validDirections()
        direction = self.goalDirectionDij(directions=directions)
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

    def getDijkstraPath(self):
        # lastGhostNode = self.ghost.target
        # lastGhostNode = self.nodes.getVectorFromLUTNode(lastGhostNode)
        pacmanTarget = (self.target.x, self.target.y)
        # pacmanTarget = self.nodes.getVectorFromLUTNode(pacmanTarget)
        previous_nodes, shortest_path = dijkstra(self.nodes, pacmanTarget, self.pellets)
        path = []

        min_weight_node = None
        min_weight = float('inf')
        for node, weight in shortest_path.items():
            if weight < min_weight and weight > 0:
                min_weight = weight
                min_weight_node = node

        while min_weight_node != pacmanTarget:
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
        pacmanTarget = self.node
        pacmanTarget = self.nodes.getVectorFromLUTNode(pacmanTarget)
        # path.append(pacmanTarget)
        nextMoveNode = path[1]
        print(nextMoveNode)
        if pacmanTarget[0] > nextMoveNode[0] and 2 in directions : #left
            return 2
        if pacmanTarget[0] < nextMoveNode[0] and -2 in directions : #right
            return -2
        if pacmanTarget[1] > nextMoveNode[1] and 1 in directions : #up
            return 1
        if pacmanTarget[1] < nextMoveNode[1] and -1 in directions : #down
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

    def get_dijkstra_distance(self, ghost):
        pass

    def eatenPellet(self, pellet):
        self.pellets.remove((pellet.y, pellet.x))
        print(f"Pellets left: {len(self.pellets)}")
        print(f"REMOVED {pellet}")

