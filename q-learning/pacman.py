import pygame
from pygame.locals import *
from vector import Vector2
from constants import *
from entity import Entity
from sprites import PacmanSprites

class Pacman(Entity):
    def __init__(self, node, nodes, pellets):
        Entity.__init__(self, node )
        self.name = PACMAN    
        self.color = YELLOW
        self.direction = LEFT
        self.setBetweenNodes(LEFT)
        self.alive = True
        self.nodes = nodes
        self.sprites = PacmanSprites(self)
        self.pellets = pellets.getPellets()

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
        return pacman_tile, ghost_tiles
    
    def update(self, dt):	
        self.sprites.update(dt)
        self.position += self.directions[self.direction]*self.speed*dt
        direction = self.getValidKey()
        if self.overshotTarget():
            self.node = self.target
            pacman_tile, ghost_tiles = self.getState()
            print(f"PACMAN TILE: {pacman_tile}; GHOST TILES: {ghost_tiles}")
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

    def eatenPellet(self, pellet):
        self.pellets.remove((pellet.y, pellet.x))
        print(f"Pellets left: {len(self.pellets)}")
        print(f"REMOVED {pellet}")  
    
    def collideGhost(self, ghost):
        return self.collideCheck(ghost)

    def collideCheck(self, other):
        d = self.position - other.position
        dSquared = d.magnitudeSquared()
        rSquared = (self.collideRadius + other.collideRadius)**2
        if dSquared <= rSquared:
            return True
        return False

    def validDirection(self, direction):
        if direction is not STOP:
            if self.name in self.target.access[direction]:
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