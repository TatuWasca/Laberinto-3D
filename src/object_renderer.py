import pygame as pg
from os import path
from src.settings import *

class ObjectRenderer:
    def __init__(self, game):
        self.game = game
        self.screen = game.screen
        self.wall_textures = self.load_wall_textures()

    def draw(self):
        self.render_game_objects()

    def render_game_objects(self):
        list_objects = sorted(self.game.raycasting.objects_to_render, key=lambda t: t[0], reverse=True)
        for depth, image, pos in list_objects:
            self.screen.blit(image, pos)

    @staticmethod
    def get_texture(path, res=(TEXTURE_SIZE, TEXTURE_SIZE)):
        texture = pg.image.load(path).convert_alpha()
        return pg.transform.scale(texture, res)

    def load_wall_textures(self):
        return {
            1: self.get_texture(path.join(self.game.root_file, 'resources/textures/1.png')),
            2: self.get_texture(path.join(self.game.root_file, 'resources/textures/2.png')),
            3: self.get_texture(path.join(self.game.root_file, 'resources/textures/3.png')),
            4: self.get_texture(path.join(self.game.root_file, 'resources/textures/4.png')),
            5: self.get_texture(path.join(self.game.root_file, 'resources/textures/5.png')),
            6: self.get_texture(path.join(self.game.root_file, 'resources/textures/6.png')),
            7: self.get_texture(path.join(self.game.root_file, 'resources/textures/7.png')),
            8: self.get_texture(path.join(self.game.root_file, 'resources/textures/8.png'))
        }