import pygame as pg
import sys
import configparser
from menu import *
from os import path
from settings import *
from map import *
from player import *
from raycasting import *
from object_renderer import *
from sprite_object import *
from object_handler import *
from pathfinding import *

class Game:
    def __init__(self):
        pg.init()
        pg.mouse.set_visible(False)
        pg.mixer.pre_init(frequency=44100, size=32, channels=2, buffer=512)
        pg.display.set_icon(pg.image.load(path.join(path.dirname(__file__), ICON)))
        pg.display.set_caption('Laberinto 3D')
        self.screen = pg.display.set_mode((0,0), pg.FULLSCREEN)
        self.clock = pg.time.Clock()
        self.delta_time = 1
        self.load_data()
    
    def load_data(self):
        # Starts the config parser
        self.configParser = configparser.ConfigParser()
        self.configFilePath = path.join(path.dirname(__file__), 'config.cfg')
        self.configParser.read(self.configFilePath)
        
        self.general_vol = int(self.configParser.get("info","GENERAL_VOLUME"))
        self.music_vol = int(self.configParser.get("info","MUSIC_VOLUME"))

        self.font = path.join(path.dirname(__file__), FONT)
        self.Titlefont = pg.font.Font(self.font, 20)
        self.Textfont = pg.font.Font(self.font, 15)
        self.Smalltextfont = pg.font.Font(self.font, 10)

        self.stamina_icon = pg.image.load(path.join(path.dirname(__file__), STAMINA_ICON)).convert_alpha()
        self.stamina_icon = pg.transform.smoothscale(self.stamina_icon, (40, 40))

        self.main_menu = MainMenu(self)
        self.options = OptionsMenu(self)
        self.credits = CreditsMenu(self)
        self.pause_menu = PauseMenu(self)
        self.gameover_menu = GameoverMenu(self)
        self.win_menu = WinMenu(self)
        self.curr_menu = self.main_menu

        self.effects_sounds = {}
        for type in EFFECT_SOUNDS:
            self.effects_sounds[type] = pg.mixer.Sound(path.join(path.dirname(__file__), EFFECT_SOUNDS[type]))
            self.effects_sounds[type].set_volume(self.general_vol / 100)

        self.playing = False

    def new_game(self):
        self.map = Map(self)
        self.player = Player(self)
        self.object_renderer = ObjectRenderer(self)
        self.raycasting = RayCasting(self)
        self.object_handler = ObjectHandler(self)
        self.pathfinding = PathFinding(self)
    
    def run(self):
        while self.playing:
            self.check_events()
            self.update()
            self.draw()

    def check_events(self):
        for event in pg.event.get():
            if event.type == pg.QUIT:
                pg.quit()
                sys.exit()
            if event.type == pg.KEYDOWN:
                if event.key == pg.K_ESCAPE:
                    self.playing = False
                    self.curr_menu = self.pause_menu
                    self.curr_menu.display_menu()

    def update(self):
        self.player.update()
        self.raycasting.update()
        self.object_handler.update()
        self.draw_text('FPS: ' +  "{:.0f}".format(self.clock.get_fps()),10, 5, 10, 'left')
        pg.display.flip()
        self.delta_time = self.clock.tick(FPS)

    def draw(self):
        if self.playing:
            self.screen.fill(BLACK)
            self.object_renderer.draw()
            self.draw_hud()
    
    def draw_hud(self):
        self.screen.blit(self.stamina_icon, (10, MONITOR_H - 50))
        pg.draw.rect(self.screen, 'white', pg.Rect(60, MONITOR_H - 40, int(self.player.stamina) * 2.5, 25))
        pg.draw.rect(self.screen, 'green', pg.Rect(60, MONITOR_H - 40, 250, 25) , 1)
    
    def draw_text(self, text, size, x, y, align):
        # Checks size
        if size == 20:
            text_surface = self.Titlefont.render(text, True, WHITE)
        if size == 15:
            text_surface = self.Textfont.render(text, True, WHITE)
        if size == 10:
            text_surface = self.Smalltextfont.render(text, True, WHITE)

        # Changes the position of text
        text_rect = text_surface.get_rect()

        # Checks align
        if align == "center":
            text_rect.center = (x,y)
        if align == "left":
            text_rect.left, text_rect.centery = x, y 

        self.screen.blit(text_surface, text_rect)

if __name__ == '__main__':
    g = Game()
    
    while (1):    
        g.run()
        g.curr_menu.display_menu()