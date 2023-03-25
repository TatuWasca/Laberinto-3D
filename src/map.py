import pygame as pg
from random import randrange, choice, randint
from src.settings import *
from decimal import Decimal
from colorama import init, Fore

init()

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
            self.mini_map = generate_grid_maze(self.rows, self.cols, self.map_height, self.map_width)
            self.posible_spawns = []
            self.world_map = {}

            # Get all exit positions and choose one, then filter it out
            for y in range(self.map_height):
                for x in range(self.map_width):
                    if self.mini_map[y][x] == 0:
                        exits = 0
                        if self.mini_map[y][x + 1] == 0:
                            exits += 1
                        if self.mini_map[y][x - 1] == 0:
                            exits += 1
                        if self.mini_map[y + 1][x] == 0:
                            exits += 1
                        if self.mini_map[y - 1][x] == 0:
                            exits += 1

                        if exits == 1:
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
            self.posible_spawns = list(filter_spawns(self.exit_spawn, self.posible_spawns, self.map_width, self.map_height))

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
                self.posible_spawns = list(filter_spawns(player_spawn, self.posible_spawns, self.map_width, self.map_height))
                self.player_spawn = float(Decimal(player_spawn[0]) + Decimal('0.5')), float(Decimal(player_spawn[1]) + Decimal('0.5'))

            # Get key spawn
            if len(self.posible_spawns) > 1:
                key_spawn = choice(self.posible_spawns)
                self.posible_spawns = list(filter_spawns(key_spawn, self.posible_spawns, self.map_width, self.map_height))
                self.key_spawn = float(Decimal(key_spawn[0]) + Decimal('0.5')), float(Decimal(key_spawn[1]) + Decimal('0.5'))

            # Get npc spawn
            if len(self.posible_spawns) > 1:
                npc_spawn = choice(self.posible_spawns)
                self.npc_spawn = float(Decimal(npc_spawn[0]) + Decimal('0.5')), float(Decimal(npc_spawn[1]) + Decimal('0.5'))
                break
        
    def draw(self):
        if self.toggle_map:
            # Draw map and visited tiles
            [pg.draw.rect(self.game.screen, 'darkgray', (pos[0] * 14 + MONITOR_W/2 - self.map_width/2 * 14, pos[1] * 14 + MONITOR_H/2 - self.map_height/2 * 14, 14, 14))
            for pos in self.world_map]
            [pg.draw.rect(self.game.screen, 'blue', (pos[0] * 14 + MONITOR_W/2 - self.map_width/2 * 14, pos[1] * 14 + MONITOR_H/2 - self.map_height/2 * 14, 14, 14))
            for pos in self.visited]

            # Draw player
            player_pos = self.game.player.map_pos
            pg.draw.circle(self.game.screen, 'green', (player_pos[0] * 14 + MONITOR_W/2 - self.map_width/2 * 14 + 7, player_pos[1] * 14 + MONITOR_H/2 - self.map_height/2 * 14 + 7), 7)
            
            # Draw pathfinding tiles
            # if not(self.game.object_handler.npc.roaming):
            #   path = self.game.pathfinding.path
            #   for i in path:
            #       pg.draw.rect(self.game.screen, 'yellow', (i[0] * 14 + MONITOR_W/2 - self.map_width/2 * 14 + 3.5, i[1] * 14 + MONITOR_H/2 - self.map_height/2 * 14 + 3.5, 7, 7))
            
            # Draw NPC, exit and key
            # npc_pos = self.game.object_handler.npc.map_pos
            # pg.draw.circle(self.game.screen, 'lightgrey', (npc_pos[0] * 14 + MONITOR_W/2 - self.map_width/2 * 14 + 7, npc_pos[1] * 14 + MONITOR_H/2 - self.map_height/2 * 14 + 7), 7)
            # pg.draw.rect(self.game.screen, 'purple', ((self.key_spawn[0] - 0.5) * 14 + MONITOR_W/2 - self.map_width/2 * 14, (self.key_spawn[1] - 0.5) * 14 + MONITOR_H/2 - self.map_height/2 * 14 - 0.5, 14, 14))
            # pg.draw.rect(self.game.screen, 'yellow', (self.door_spawn[1] * 14 + MONITOR_W/2 - self.map_width/2 * 14, self.door_spawn[0] * 14 + MONITOR_H/2 - self.map_height/2 * 14, 14, 14))


class Cell:
    def __init__(self, x, y, cols, rows):
        self.x, self.y = x, y
        self.cols, self.rows = cols, rows
        self.walls = {'top': True, 'right': True, 'bottom': True, 'left': True}
        self.visited = False
        self.thickness = 4

    def check_cell(self, x, y):
        find_index = lambda x, y: x + y * self.cols
        if x < 0 or x > self.cols - 1 or y < 0 or y > self.rows - 1:
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
def filter_spawns(target_spawn, spawns, m_width, m_height):
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

def generate_maze(rows, cols):
    grid_cells = [Cell(col, row, cols, rows) for row in range(rows) for col in range(cols)]
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

def generate_grid_maze(rows, cols, m_height, m_width):
    map = []
    
    # Loop for creating a map and keeping it if its valid
    while True:
        map = []
        # Only way I could find of passing a cell map to a grid like map including walls
        grid_cells = generate_maze(rows, cols)
        row = []
        # Generate a map taking in account the walls
        for y in range(m_height):
            for x in range(m_width):
                row.append('u')
            map.append(row)
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
            if (i + 1) % (rows * mul) == 0:
                map[cell[1] + ctr_x][cell[0] + ctr_y] = 0
                if cell[2]['left']:
                    map[cell[1] + ctr_x][cell[0] + ctr_y - 1] = num
                else:
                    map[cell[1] + ctr_x][cell[0] + ctr_y - 1] = 0
                if cell[2]['top']:
                    map[cell[1] + ctr_x - 1][cell[0] + ctr_y] = num
                else:
                    map[cell[1] + ctr_x - 1][cell[0] + ctr_y] = 0

                ctr_y += 1
                ctr_x = 1
                mul += 1
            else:
                map[cell[1] + ctr_x][cell[0] + ctr_y] = 0
                if cell[2]['left']:
                    map[cell[1] + ctr_x][cell[0] + ctr_y - 1] = num
                else:
                    map[cell[1] + ctr_x][cell[0] + ctr_y - 1] = 0
                if cell[2]['top']:
                    map[cell[1] + ctr_x - 1][cell[0] + ctr_y] = num
                else:
                    map[cell[1] + ctr_x - 1][cell[0] + ctr_y] = 0
                ctr_x += 1
        
        # Reeplace all remainding parts with walls
        for y in range(m_height):
            for x in range(m_width):
                num = randint(1,3)
                if map[x][y] == 'u':        
                    map[x][y] = num
        
        # Eliminate some walls randomly so the maze is fair
        for i in range(10 * ((rows - 5) // 2)):
            y = randint(1, m_height - 2)
            x = randint(1, m_width - 2)
            if map[y][x] != 0:
                if map[y][x + 1] == 0 and map[y][x - 1] == 0:
                    if map[y + 1][x] in [1, 2, 3] and map[y - 1][x] in [1, 2, 3]:
                        map[y][x] = 0
                elif map[y + 1][x] == 0 and map[y - 1][x] == 0:
                    if map[y][x + 1] in [1, 2, 3] and map[y][x - 1] in [1, 2, 3]:
                        map[y][x] = 0
        
        # Get all exit positions
        posible_exits = []
        for y in range(m_height):
            for x in range(m_width):
                if map[y][x] == 0:
                    exits = 0
                    if map[y][x + 1] == 0:
                        exits += 1
                    if map[y][x - 1] == 0:
                        exits += 1
                    if map[y + 1][x] == 0:
                        exits += 1
                    if map[y - 1][x] == 0:
                        exits += 1

                    if exits == 1:
                        posible_exits.append((x,y))    

        # Make sure there is at least one possible exit in all 4 quadrants, else remake the map
        if len(posible_exits) > 8:
            posible_exits = list(filter_spawns(choice(posible_exits), posible_exits, m_width, m_height))

            if len(posible_exits) > 6:
                posible_exits = list(filter_spawns(choice(posible_exits), posible_exits, m_width, m_height))

                if len(posible_exits) > 4:
                    posible_exits = list(filter_spawns(choice(posible_exits), posible_exits, m_width, m_height))

                    if len(posible_exits) > 2:
                        posible_exits = list(filter_spawns(choice(posible_exits), posible_exits, m_width, m_height))

                        if len(posible_exits) == 0:
                            break
    return map