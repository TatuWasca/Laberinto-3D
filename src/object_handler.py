import pygame as pg
from os import path
from src.map import *
from src.sprite_object import *
from src.npc import *

class ObjectHandler:
    def __init__(self, game):
        self.game = game
        self.sprite_list = []
        self.npc = NPC(game, path.join(self.game.root_file, self.game.curr_npc), self.game.map.npc_spawn, 0.9, 0.1, 90)
        self.key = SpriteObject(game, path.join(self.game.root_file,'resources/sprites/static/key.png'), self.game.map.key_spawn, 0.3, 0.7)
        self.key_rect = pg.Rect((self.game.map.key_spawn[0] - 0.25) * 100, (self.game.map.key_spawn[1] - 0.25) * 100, 25, 25)
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
            self.game.map.mini_map[self.game.map.door_spawn[0]][self.game.map.door_spawn[1]] = False
            self.game.map.world_map = {}
            self.game.map.get_map()

    def display_text(self):
        now = pg.time.get_ticks() 
        if now < self.text_time:
            self.game.draw_text('You picked up a golden key', 20, HALF_WIDTH, (HALF_HEIGHT / 2) * 3, 'center')

    def check_win(self):
        if self.game.player.map_pos == (self.game.map.door_spawn[1], self.game.map.door_spawn[0]):
            self.win()

    def game_over(self):
        self.game.curr_menu = self.game.gameover_menu
        self.game.playing = False
        self.game.curr_menu.display_menu()

    def win(self):
        self.game.curr_menu = self.game.win_menu
        self.game.playing = False
        self.game.curr_menu.display_menu()