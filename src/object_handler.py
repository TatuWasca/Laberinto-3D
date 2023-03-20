import pygame as pg
from os import path
from src.map import *
from src.sprite_object import *
from src.npc import *

class ObjectHandler:
    def __init__(self, game):
        self.game = game
        self.sprite_list = []
        self.npc = NPC(game, path.join(self.game.root_file,'resources/sprites/animated/enemy.png'), NPC_POS[0], 0.9, 0.1, 180)
        self.key = SpriteObject(game, path.join(self.game.root_file,'resources/sprites/static/key.png'), KEY_POS[0], 0.3, 0.7)
        self.key_rect = pg.Rect((KEY_POS[0][0] - 0.25) * 100, (KEY_POS[0][1] - 0.25) * 100, 25, 25)
        self.picked = False
        self.text_time = 0
    
    def update(self):
        self.npc.update()
        if not(self.picked): 
            self.key.update()
            self.check_pick_key()
        else:
            self.display_text()
            self.check_win()
            
    def check_pick_key(self):
        if self.key_rect.colliderect(self.game.player.player_rect):
            self.picked = True
            self.text_time = pg.time.get_ticks() + 4500
            self.game.effects_sounds['key_grab'].play()
            
            # Reloads map
            MINI_MAP[DOOR_POS[0][0]][DOOR_POS[0][1]] = False
            self.game.map.mini_map = MINI_MAP
            self.game.map.world_map = {}
            self.game.map.get_map()

    def display_text(self):
        now = pg.time.get_ticks() 
        if now < self.text_time:
            self.game.draw_text('You picked up a golden key', 20, HALF_WIDTH, (HALF_HEIGHT / 2) * 3, 'center')

    def check_win(self):
        if self.game.player.map_pos == (DOOR_POS[0][1], DOOR_POS[0][0]):
            self.win()

    def game_over(self):
        # Resets map
        for y in range(MAP_HEIGHT - 1):
            for x in range(MAP_WIDTH - 1):
                if (x, y) in self.game.map.posible_spawns:
                    MINI_MAP[y][x] = 3
                elif (x, y) in self.game.map.door_spawns:
                    MINI_MAP[y][x] = 2

        self.game.curr_menu = self.game.gameover_menu
        self.game.playing = False
        self.game.curr_menu.display_menu()

    def win(self):
        # Resets map
        for y in range(MAP_HEIGHT - 1):
            for x in range(MAP_WIDTH - 1):
                if (x, y) in self.game.map.posible_spawns:
                    MINI_MAP[y][x] = 3
                elif (x, y) in self.game.map.door_spawns:
                    MINI_MAP[y][x] = 2
                    
        self.game.curr_menu = self.game.win_menu
        self.game.playing = False
        self.game.curr_menu.display_menu()