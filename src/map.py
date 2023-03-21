import pygame as pg
from random import randrange, choice, randint
from src.settings import *
from decimal import Decimal

class Map:
    def __init__(self, game):
        self.game = game
        self.posible_spawns = [] 
        self.mini_map = generate_grid_maze()
        self.world_map = {}
        self.visited = []
        self.exit_spawn, self.door_spawn, self.key_spawn, self.npc_spawn, self.player_spawn = (), (), (), (), ()
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
        # Get all exit positions and choose one, then filter it out
        for y in range(MAP_HEIGHT):
            for x in range(MAP_WIDTH):
                if self.mini_map[x][y] == False:
                    exits = 0
                    if self.mini_map[y][x + 1] == False:
                        exits += 1
                    if self.mini_map[y][x - 1] == False:
                        exits += 1
                    if self.mini_map[y + 1][x] == False:
                        exits += 1
                    if self.mini_map[y - 1][x] == False:
                        exits += 1

                    if exits == 1:
                        self.posible_spawns.append((x,y))
        spawns = self.posible_spawns
        self.exit_spawn = choice(spawns)
        self.mini_map[self.exit_spawn[1]][self.exit_spawn[0]] = 5
        spawns = list(self.filter_spawns(self.exit_spawn, spawns))

        # Based on exit position, get door position
        e_x, e_y = self.exit_spawn[0], self.exit_spawn[1]
        if  self.mini_map[e_y - 1][e_x] not in [1, 2, 3]:
            self.door_spawn = (e_y - 1, e_x)
        elif  self.mini_map[e_y][e_x + 1] not in [1, 2, 3]:
            self.door_spawn = (e_y, e_x + 1)
        elif  self.mini_map[e_y + 1][e_x] not in [1, 2, 3]:
            self.door_spawn = (e_y + 1, e_x)
        elif  self.mini_map[e_y][e_x - 1] not in [1, 2, 3]:
            self.door_spawn = (e_y, e_x - 1)

        # Get player spawn
        player_spawn = choice(spawns)
        self.player_spawn = float(Decimal(player_spawn[0]) + Decimal('0.5')), float(Decimal(player_spawn[1]) + Decimal('0.5'))
        spawns = list(self.filter_spawns(self.player_spawn, spawns))

        # Get key spawn
        key_spawn = choice(spawns)
        self.key_spawn = float(Decimal(key_spawn[0]) + Decimal('0.5')), float(Decimal(key_spawn[1]) + Decimal('0.5'))
        spawns = list(self.filter_spawns(self.key_spawn, spawns))

        # Get npc spawn
        npc_spawn = choice(spawns)
        self.npc_spawn = float(Decimal(npc_spawn[0]) + Decimal('0.5')), float(Decimal(npc_spawn[1]) + Decimal('0.5'))

        # Eliminate some walls randomly so the maze is fair
        for i in range(10):
            y = randint(1, MAP_HEIGHT - 3)
            x = randint(1, MAP_WIDTH - 3)
            if self.mini_map[y][x] != False:
                if self.mini_map[y][x + 1] == False and self.mini_map[y][x - 1] == False:
                    if self.mini_map[y + 1][x] in [1, 2, 3] and self.mini_map[y - 1][x] in [1, 2, 3]:
                        self.mini_map[y][x] = False
                elif self.mini_map[y + 1][x] == False and self.mini_map[y - 1][x] == False:
                    if self.mini_map[y][x + 1] in [1, 2, 3] and self.mini_map[y][x - 1] in [1, 2, 3]:
                        self.mini_map[y][x] = False

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

        # player_pos = self.game.player.map_pos
        # npc_pos = self.game.object_handler.npc.map_pos
        
        # Draw player and NPC
        # pg.draw.circle(self.game.screen, 'lightgrey', (npc_pos[0] * 14 + MONITOR_W/2 - MAP_WIDTH/2 * 14 + 7, npc_pos[1] * 14 + MONITOR_H/2 - MAP_HEIGHT/2 * 14 + 7), 7)
        pg.draw.circle(self.game.screen, 'green', (player_pos[0] * 14 + MONITOR_W/2 - MAP_WIDTH/2 * 14 + 7, player_pos[1] * 14 + MONITOR_H/2 - MAP_HEIGHT/2 * 14 + 7), 7)
        
        # Draw Exit and key
        # pg.draw.rect(self.game.screen, 'purple', ((self.key_spawn[0] - 0.5) * 14 + MONITOR_W/2 - MAP_WIDTH/2 * 14, (self.key_spawn[1] - 0.5) * 14 + MONITOR_H/2 - MAP_HEIGHT/2 * 14 - 0.5, 14, 14))
        # pg.draw.rect(self.game.screen, 'yellow', (self.door_spawn[1] * 14 + MONITOR_W/2 - MAP_WIDTH/2 * 14, self.door_spawn[0] * 14 + MONITOR_H/2 - MAP_HEIGHT/2 * 14, 14, 14))


class Cell:
    def __init__(self, x, y):
        self.x, self.y = x, y
        self.walls = {'top': True, 'right': True, 'bottom': True, 'left': True}
        self.visited = False
        self.thickness = 4

    def check_cell(self, x, y):
        find_index = lambda x, y: x + y * COLS
        if x < 0 or x > COLS - 1 or y < 0 or y > ROWS - 1:
            return False
        return self.grid_cells[find_index(x, y)]

    def check_neighbors(self, grid_cells):
        self.grid_cells = grid_cells
        neighbors = []
        top = self.check_cell(self.x, self.y - 1)
        right = self.check_cell(self.x + 1, self.y)
        bottom = self.check_cell(self.x, self.y + 1)
        left = self.check_cell(self.x - 1, self.y)
        if top and not top.visited:
            neighbors.append(top)
        if right and not right.visited:
            neighbors.append(right)
        if bottom and not bottom.visited:
            neighbors.append(bottom)
        if left and not left.visited:
            neighbors.append(left)
        return choice(neighbors) if neighbors else False


# Functions for generating the maze
def remove_walls(current, next):
    dx = current.x - next.x
    if dx == 1:
        current.walls['left'] = False
        next.walls['right'] = False
    elif dx == -1:
        current.walls['right'] = False
        next.walls['left'] = False
    dy = current.y - next.y
    if dy == 1:
        current.walls['top'] = False
        next.walls['bottom'] = False
    elif dy == -1:
        current.walls['bottom'] = False
        next.walls['top'] = False

def generate_maze():
    grid_cells = [Cell(col, row) for row in range(ROWS) for col in range(COLS)]
    current_cell = grid_cells[0]
    array = []
    break_count = 1

    while break_count != len(grid_cells):
        current_cell.visited = True
        next_cell = current_cell.check_neighbors(grid_cells)
        if next_cell:
            next_cell.visited = True
            break_count += 1
            array.append(current_cell)
            remove_walls(current_cell, next_cell)
            current_cell = next_cell
        elif array:
            current_cell = array.pop()
    return grid_cells

def generate_grid_maze():
    # Only way I could find of passing a cell map to a grid like map including walls
    grid_cells = generate_maze()

    list = []
    row = []
    # Generate a map taking in account the walls
    for y in range(ROWS * 2 + 1):
        for x in range(COLS * 2 + 1):
            row.append('u')
        list.append(row)
        row = []
    test = []
    # Get all cell positions and walls and sort them
    for i in grid_cells:
        test.append((i.x, i.y, i.walls))
    test.sort()

    # Generate the grid map
    ctr_y = 1
    ctr_x = 1
    mul = 1
    for i, cell in enumerate(test):
        num = randint(1,3)
        if (i + 1) % (ROWS * mul) == 0:
            list[cell[1] + ctr_x][cell[0] + ctr_y] = False
            if cell[2]['left']:
                list[cell[1] + ctr_x][cell[0] + ctr_y - 1] = num
            else:
                list[cell[1] + ctr_x][cell[0] + ctr_y - 1] = False
            if cell[2]['top']:
                list[cell[1] + ctr_x - 1][cell[0] + ctr_y] = num
            else:
                list[cell[1] + ctr_x - 1][cell[0] + ctr_y] = False

            ctr_y += 1
            ctr_x = 1
            mul += 1
        else:
            list[cell[1] + ctr_x][cell[0] + ctr_y] = False
            if cell[2]['left']:
                list[cell[1] + ctr_x][cell[0] + ctr_y - 1] = num
            else:
                list[cell[1] + ctr_x][cell[0] + ctr_y - 1] = False
            if cell[2]['top']:
                list[cell[1] + ctr_x - 1][cell[0] + ctr_y] = num
            else:
                list[cell[1] + ctr_x - 1][cell[0] + ctr_y] = False
            ctr_x += 1
    
    # Reeplace all remainding parts with walls
    for y in range(ROWS * 2 + 1):
        for x in range(COLS * 2 + 1):
            num = randint(1,3)
            if list[x][y] == 'u':        
               list[x][y] = num
    return list