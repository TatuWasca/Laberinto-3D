import pygame as pg
import math
from random import randrange, choice, randint, shuffle
from os import path
from src.settings import *
from src.sprite_object import *
from src.npc import *
from decimal import Decimal

class Map:
    def __init__(self, game):
        self.game = game
        self.difficulty = self.game.difficulty_menu.difficulty
        self.rows, self.cols = 8 + self.difficulty * 2, 8 + self.difficulty * 2
        self.map_height, self.map_width = self.rows * 2 + 1, self.cols * 2 + 1

        self.posible_spawns = [] 
        self.mini_map = []
        self.world_map = {}
        self.visited = []
        self.exit_spawn, self.door_spawn, self.key_spawn, self.npc_spawn, self.player_spawn = (), (), (), (), ()
        self.toggle_map = False
        self.get_spawns()
        self.get_map()   

    def get_map(self):
        for j, row in enumerate(self.mini_map):
            for i, value in enumerate(row):
                if value:
                    self.world_map[(i, j)] = value
    
    def add(self):
        if (self.game.player.map_pos) not in self.visited:
            self.visited.append((self.game.player.map_pos))

    def get_spawns(self):
        # Loop that doble checks if the map is valid
        while True:
            self.mini_map = self.generate_maze(self.map_height, self.map_width)
            self.posible_spawns = []
            self.world_map = {}
            self.exit_spawn, self.door_spawn, self.key_spawn, self.npc_spawn, self.player_spawn = (), (), (), (), ()

            # Get all exit positions and choose one, then filter it out
            for y in range(self.map_height):
                for x in range(self.map_width):
                    if self.mini_map[y][x] == 0:
                        exits = 0
                        e_posx, e_posy = x, y
                        if self.mini_map[y][x + 1] == 0:
                            exits += 1
                            e_posy, e_posx = y, x + 1
                        if self.mini_map[y][x - 1] == 0:
                            exits += 1
                            e_posy, e_posx = y, x - 1
                        if self.mini_map[y + 1][x] == 0:
                            exits += 1
                            e_posy, e_posx = y + 1, x
                        if self.mini_map[y - 1][x] == 0:
                            exits += 1
                            e_posy, e_posx = y - 1, x

                        if exits == 1:
                            exits = 0
                            if self.mini_map[e_posy][e_posx + 1] == 0:
                                exits += 1
                            if self.mini_map[e_posy][e_posx - 1] == 0:
                                exits += 1
                            if self.mini_map[e_posy + 1][e_posx] == 0:
                                exits += 1
                            if self.mini_map[e_posy - 1][e_posx] == 0:
                                exits += 1
                            
                            if exits == 2:
                                self.posible_spawns.append((x, y))
            
            # Check for exits with at least 2 tiles of depth
            valid_exit_spawns = []
            for spawn in self.posible_spawns:
                x, y = spawn
                if self.mini_map[y][x + 1] == 0:
                    if self.mini_map[y][x + 2] == 0:
                        valid_exit_spawns.append((x,y))
                if self.mini_map[y][x - 1] == 0:
                    if self.mini_map[y][x - 2] == 0:
                        valid_exit_spawns.append((x,y))
                if self.mini_map[y + 1][x] == 0:
                    if self.mini_map[y + 2][x] == 0:
                        valid_exit_spawns.append((x,y))
                if self.mini_map[y - 1][x] == 0:
                    if self.mini_map[y - 2][x] == 0:
                        valid_exit_spawns.append((x,y))
            self.exit_spawn = choice(valid_exit_spawns)
            self.mini_map[self.exit_spawn[1]][self.exit_spawn[0]] = 5
            self.posible_spawns = list(self.filter_spawns(self.exit_spawn, self.posible_spawns, self.map_width, self.map_height))

            # Based on exit position, get door position
            e_x, e_y = self.exit_spawn
            if self.mini_map[e_y - 1][e_x] not in [1, 2, 3]:
                self.door_spawn = (e_y - 1, e_x)
            elif self.mini_map[e_y][e_x + 1] not in [1, 2, 3]:
                self.door_spawn = (e_y, e_x + 1)
            elif self.mini_map[e_y + 1][e_x] not in [1, 2, 3]:
                self.door_spawn = (e_y + 1, e_x)
            elif self.mini_map[e_y][e_x - 1] not in [1, 2, 3]:
                self.door_spawn = (e_y, e_x - 1)
            self.mini_map[self.door_spawn[0]][self.door_spawn[1]] = 4

            # Get player spawn
            if len(self.posible_spawns) > 1:
                player_spawn = choice(self.posible_spawns)
                self.posible_spawns = list(self.filter_spawns(player_spawn, self.posible_spawns, self.map_width, self.map_height))
                self.player_spawn = float(Decimal(player_spawn[0]) + Decimal('0.5')), float(Decimal(player_spawn[1]) + Decimal('0.5'))

            # Get key spawn
            if len(self.posible_spawns) > 1:
                key_spawn = choice(self.posible_spawns)
                self.posible_spawns = list(self.filter_spawns(key_spawn, self.posible_spawns, self.map_width, self.map_height))
                self.key_spawn = float(Decimal(key_spawn[0]) + Decimal('0.5')), float(Decimal(key_spawn[1]) + Decimal('0.5'))

            # Get npc spawn
            if len(self.posible_spawns) > 1:
                npc_spawn = choice(self.posible_spawns)
                self.npc_spawn = float(Decimal(npc_spawn[0]) + Decimal('0.5')), float(Decimal(npc_spawn[1]) + Decimal('0.5'))
                break
    
    def generate_maze(self, width, height):
        maze = [[1] * width for _ in range(height)]  # initialize maze with all walls

        # create pathways starting from a random point
        x, y = 1, 1
        maze[y][x] = 0  # mark starting point as a pathway
        self.generate_path(x, y, maze)

        # Eliminate some walls randomly so the maze is fair
        for i in range(20 * ((self.rows - 5) // 2)):
            y = randint(1, self.map_height - 2)
            x = randint(1, self.map_width - 2)
            if maze[y][x] != 0:
                if maze[y][x + 1] == 0 and maze[y][x - 1] == 0:
                    if maze[y + 1][x] in [1, 2, 3] and maze[y - 1][x] in [1, 2, 3]:
                        maze[y][x] = 0
                elif maze[y + 1][x] == 0 and maze[y - 1][x] == 0:
                    if maze[y][x + 1] in [1, 2, 3] and maze[y][x - 1] in [1, 2, 3]:
                        maze[y][x] = 0
        return maze

    def generate_path(self, x, y, maze):
        directions = [(0, -2), (2, 0), (0, 2), (-2, 0)]  # possible directions to move

        shuffle(directions)  # randomize the order in which directions are tried

        for dx, dy in directions:
            next_x, next_y = x + dx, y + dy

            if 0 <= next_x < len(maze[0]) and 0 <= next_y < len(maze) and maze[next_y][next_x] == 1:
                # check if the next cell is a wall and is within bounds
                maze[y + dy // 2][x + dx // 2] = 0  # remove wall between current and next cell
                maze[next_y][next_x] = 0  # mark next cell as a pathway
                self.generate_path(next_x, next_y, maze)  # continue generating pathways from next cell

    def change_map_playing(self):
        self.get_spawns()
        self.visited = []

        if not(self.game.object_handler.npc.chaise_audio):
            self.game.effects_sounds['chase_music'].fadeout(1000)
            self.game.effects_sounds['ambient_music'].play(loops=-1)

        self.game.player.x, self.game.player.y = self.player_spawn
        self.game.object_handler.npc = NPC(self.game, path.join(self.game.root_file, self.game.curr_npc), self.npc_spawn, 0.9, 0.1, 90)

        if not(self.game.object_handler.picked):
            self.game.object_handler.key = SpriteObject(self.game, path.join(self.game.root_file,'resources/sprites/static/key.png'), self.key_spawn, 0.3, 0.7)
            self.game.object_handler.key_rect = pg.Rect((self.key_spawn[0] - 0.25) * 100, (self.key_spawn[1] - 0.25) * 100, 25, 25)  
        else:
            self.mini_map[self.door_spawn[0]][self.door_spawn[1]] = 0

        self.get_map()
        self.game.pathfinding.map = self.mini_map
        self.game.pathfinding.graph = {}
        self.game.pathfinding.path = []
        self.game.pathfinding.get_graph() 

        self.game.player.noise_pos = self.game.player.map_pos
        self.game.object_handler.npc.searching, self.game.object_handler.npc.roaming, self.game.object_handler.npc.chasing = True, False, False 
    
    def filter_spawns(self, target_spawn, spawns, m_width, m_height):
        # Filters out all the possible spawns that are not in the target spawn
        spawn = []
        if target_spawn[0] < m_width / 2:
            if target_spawn[1] < m_height / 2:
                spawn = filter(lambda y: (not(y[0] < m_width/2 and y[1] < m_height/2)), spawns) # Top Left Corner
            elif target_spawn[1] > m_height / 2:
                spawn = filter(lambda y: (not(y[0] < m_width/2 and y[1] > m_height/2)), spawns) # Bottom left Corner
        elif target_spawn[0] > m_width / 2:
            if target_spawn[1] < m_height / 2 :
                spawn = filter(lambda y: (not(y[0] > m_width/2 and y[1] < m_height/2)), spawns) # Top right Corner
            elif target_spawn[1] > m_height / 2:
                spawn = filter(lambda y: (not(y[0] > m_width/2 and y[1] > m_height/2)), spawns) # Bottom right Corner
        return spawn

    def draw(self):
        if self.toggle_map:
            # Draw map and visited tiles
            [pg.draw.rect(self.game.screen, 'black', (pos[0] * 14 + MONITOR_W/2 - self.map_width/2 * 14, pos[1] * 14 + MONITOR_H/2 - self.map_height/2 * 14, 14, 14))
            for pos in self.world_map]
            [pg.draw.rect(self.game.screen, 'white', (pos[0] * 14 + MONITOR_W/2 - self.map_width/2 * 14, pos[1] * 14 + MONITOR_H/2 - self.map_height/2 * 14, 14, 14))
            for pos in self.visited]

            # Draw player
            player_pos = self.game.player.map_pos
            pg.draw.circle(self.game.screen, 'blue', (player_pos[0] * 14 + MONITOR_W/2 - self.map_width/2 * 14 + 7, player_pos[1] * 14 + MONITOR_H/2 - self.map_height/2 * 14 + 7), 7)
            
            # Draw pathfinding tiles
            # if not(self.game.object_handler.npc.roaming):
            #     path = self.game.pathfinding.path
            #     for i in path:
            #         pg.draw.rect(self.game.screen, 'yellow', (i[0] * 14 + MONITOR_W/2 - self.map_width/2 * 14 + 3.5, i[1] * 14 + MONITOR_H/2 - self.map_height/2 * 14 + 3.5, 7, 7))
            
            # Draw NPC, exit and key
            # npc_pos = self.game.object_handler.npc.map_pos
            # pg.draw.circle(self.game.screen, 'red', (npc_pos[0] * 14 + MONITOR_W/2 - self.map_width/2 * 14 + 7, npc_pos[1] * 14 + MONITOR_H/2 - self.map_height/2 * 14 + 7), 7)
            # pg.draw.rect(self.game.screen, 'purple', ((self.key_spawn[0] - 0.5) * 14 + MONITOR_W/2 - self.map_width/2 * 14, (self.key_spawn[1] - 0.5) * 14 + MONITOR_H/2 - self.map_height/2 * 14, 14, 14))
            # pg.draw.rect(self.game.screen, 'yellow', (self.door_spawn[1] * 14 + MONITOR_W/2 - self.map_width/2 * 14, self.door_spawn[0] * 14 + MONITOR_H/2 - self.map_height/2 * 14, 14, 14))
            # pg.draw.rect(self.game.screen, 'brown', (self.exit_spawn[0] * 14 + MONITOR_W/2 - self.map_width/2 * 14, self.exit_spawn[1] * 14 + MONITOR_H/2 - self.map_height/2 * 14, 14, 14))