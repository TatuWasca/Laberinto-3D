import pygame as pg
import random
from settings import *
from decimal import Decimal

class Map:
    def __init__(self, game):
        self.game = game
        self.posible_spawns = [] 
        self.door_spawns = []
        self.get_spawns()
        self.mini_map = MINI_MAP
        self.world_map = {}
        self.visited = []
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
        # Get all exit positions and choose one, then filter it out
        for y in range(MAP_HEIGHT - 1):
            for x in range(MAP_WIDTH - 1):
                if MINI_MAP[y][x] == 3:
                    self.posible_spawns.append((x,y))
                    MINI_MAP[y][x] = False
                elif MINI_MAP[y][x] == 2:
                    self.door_spawns.append((x,y))
        spawns = self.posible_spawns
        EXIT_POS[0] = random.choice(spawns)
        MINI_MAP[EXIT_POS[0][1]][EXIT_POS[0][0]] = 3
        spawns = list(self.filter_spawns(EXIT_POS[0], spawns))

        # Based on exit position, get door position
        e_x, e_y = EXIT_POS[0][0], EXIT_POS[0][1]
        if MINI_MAP[e_y - 1][e_x] == 2:
            DOOR_POS[0] = (e_y - 1, e_x)
        elif MINI_MAP[e_y][e_x + 1] == 2:
            DOOR_POS[0] = (e_y, e_x + 1)
        elif MINI_MAP[e_y + 1][e_x] == 2:
            DOOR_POS[0] = (e_y + 1, e_x)
        elif MINI_MAP[e_y][e_x - 1] == 2:
            DOOR_POS[0] = (e_y, e_x - 1)
        
        # Reeplace all door with path except the one thats in the exit
        for y in range(MAP_HEIGHT - 1):
            for x in range(MAP_WIDTH - 1):
                if MINI_MAP[y][x] == 2:
                    MINI_MAP[y][x] = False
        MINI_MAP[DOOR_POS[0][0]][DOOR_POS[0][1]] = 2

        player_spawn = random.choice(spawns)
        PLAYER_POS[0] = float(Decimal(player_spawn[0]) + Decimal('0.5')), float(Decimal(player_spawn[1]) + Decimal('0.5'))
        spawns = list(self.filter_spawns(PLAYER_POS[0], spawns))

        key_spawn = random.choice(spawns)
        KEY_POS[0] = float(Decimal(key_spawn[0]) + Decimal('0.5')), float(Decimal(key_spawn[1]) + Decimal('0.5'))
        spawns = list(self.filter_spawns(KEY_POS[0], spawns))

        npc_spawn = random.choice(spawns)
        NPC_POS[0] = float(Decimal(npc_spawn[0]) + Decimal('0.5')), float(Decimal(npc_spawn[1]) + Decimal('0.5'))

    def filter_spawns(self, target_spawn, spawns):
        # Filters out all the possible spawns that are not in the target spawn
        spawn = []
        if target_spawn[0] < MAP_WIDTH / 2:
            if target_spawn[1] < MAP_HEIGHT / 2:
                spawn = filter(lambda y: (not(y[0] < MAP_WIDTH/2 and y[1] < MAP_HEIGHT/2)), spawns) # Top Left Corner
            elif target_spawn[1] > MAP_HEIGHT / 2:
                spawn = filter(lambda y: (not(y[0] < MAP_WIDTH/2 and y[1] > MAP_HEIGHT/2)), spawns) # Bottom left Corner
        elif target_spawn[0] > MAP_WIDTH / 2:
            if target_spawn[1] < MAP_HEIGHT / 2 :
                spawn = filter(lambda y: (not(y[0] > MAP_WIDTH/2 and y[1] < MAP_HEIGHT/2)), spawns) # Top right Corner
            elif target_spawn[1] > MAP_HEIGHT / 2:
                spawn = filter(lambda y: (not(y[0] > MAP_WIDTH/2 and y[1] > MAP_HEIGHT/2)), spawns) # Bottom right Corner
        return spawn

    def draw(self):
        # Draw map and visited tiles
        [pg.draw.rect(self.game.screen, 'darkgray', (pos[0] * 14 + MONITOR_W/2 - MAP_WIDTH/2 * 14, pos[1] * 14 + MONITOR_H/2 - MAP_HEIGHT/2 * 14, 14, 14))
         for pos in self.world_map]
        [pg.draw.rect(self.game.screen, 'blue', (pos[0] * 14 + MONITOR_W/2 - MAP_WIDTH/2 * 14, pos[1] * 14 + MONITOR_H/2 - MAP_HEIGHT/2 * 14, 14, 14))
         for pos in self.visited]
        
        # Draw pathfinding tiles
        '''if not(self.game.object_handler.npc.roaming):
            path = self.game.pathfinding.path
            for i in path:
                pg.draw.rect(self.game.screen, 'yellow', (i[0] * 14 + MONITOR_W/2 - MAP_WIDTH/2 * 14 + 3.5, i[1] * 14 + MONITOR_H/2 - MAP_HEIGHT/2 * 14 + 3.5, 7, 7))'''

        player_pos = self.game.player.map_pos
        # npc_pos = self.game.object_handler.npc.map_pos
        
        # Draw player and NPC
        #pg.draw.circle(self.game.screen, 'lightgrey', (npc_pos[0] * 14 + MONITOR_W/2 - MAP_WIDTH/2 * 14 + 7, npc_pos[1] * 14 + MONITOR_H/2 - MAP_HEIGHT/2 * 14 + 7), 7)
        pg.draw.circle(self.game.screen, 'green', (player_pos[0] * 14 + MONITOR_W/2 - MAP_WIDTH/2 * 14 + 7, player_pos[1] * 14 + MONITOR_H/2 - MAP_HEIGHT/2 * 14 + 7), 7)
        
        # Draw Exit and key
        # pg.draw.rect(self.game.screen, 'purple', ((KEY_POS[0][0] - 0.5) * 14 + MONITOR_W/2 - MAP_WIDTH/2 * 14, (KEY_POS[0][1] - 0.5) * 14 + MONITOR_H/2 - MAP_HEIGHT/2 * 14 - 0.5, 14, 14))
        # pg.draw.rect(self.game.screen, 'yellow', (DOOR_POS[0][1] * 14 + MONITOR_W/2 - MAP_WIDTH/2 * 14, DOOR_POS[0][0] * 14 + MONITOR_H/2 - MAP_HEIGHT/2 * 14, 14, 14))