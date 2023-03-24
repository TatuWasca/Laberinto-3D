import pygame as pg
import sys
import configparser
from os import path
from src.menu import *
from src.settings import *
from src.map import *
from src.player import *
from src.raycasting import *
from src.object_renderer import *
from src.sprite_object import *
from src.object_handler import *
from src.pathfinding import *

class Game:
    def __init__(self, root_path):
        pg.init()
        pg.mouse.set_visible(False)
        pg.mixer.pre_init(frequency=44100, size=32, channels=2, buffer=512)
        pg.display.set_icon(pg.image.load(path.join(root_path, ICON)))
        pg.display.set_caption('Laberinto 3D')
        self.screen = pg.display.set_mode((0,0), pg.FULLSCREEN)
        self.clock = pg.time.Clock()
        self.delta_time = 1
        self.root_file = root_path
        self.load_data()
    
    def load_data(self):
        # Starts the config parser
        self.configParser = configparser.ConfigParser()
        self.configFilePath = path.join(self.root_file, 'config.cfg')
        self.configParser.read(self.configFilePath)
        
        self.sensitivity = int(self.configParser.get("info","SENSITIVITY"))
        self.general_vol = int(self.configParser.get("info","GENERAL_VOLUME"))
        self.music_vol = int(self.configParser.get("info","MUSIC_VOLUME"))

        self.font = path.join(self.root_file, FONT)
        self.Titlefont = pg.font.Font(self.font, 20)
        self.Textfont = pg.font.Font(self.font, 15)
        self.Smalltextfont = pg.font.Font(self.font, 10)

        self.stamina_icon = pg.image.load(path.join(self.root_file, STAMINA_ICON)).convert_alpha()
        self.stamina_icon = pg.transform.smoothscale(self.stamina_icon, (40, 40))

        self.main_menu = MainMenu(self)
        self.difficulty_menu = DifficultyMenu(self)
        self.options = OptionsMenu(self)
        self.credits = CreditsMenu(self)
        self.about_menu = AboutMenu(self)
        self.pause_menu = PauseMenu(self)
        self.gameover_menu = GameoverMenu(self)
        self.win_menu = WinMenu(self)
        self.curr_menu = self.main_menu

        self.effects_sounds = {}
        for type in EFFECT_SOUNDS:
            self.effects_sounds[type] = pg.mixer.Sound(path.join(self.root_file, EFFECT_SOUNDS[type]))
            if type in ['chase_music', 'ambient_music']:
                self.effects_sounds[type].set_volume(self.music_vol / 100)
            else:
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
                if event.key == pg.K_TAB:
                    self.map.toggle_map = not(self.map.toggle_map)

    def update(self):
        self.player.update()
        self.raycasting.update()
        self.object_handler.update()
        pg.display.flip()
        self.delta_time = self.clock.tick(FPS)

    def draw(self):
        if self.playing:
            self.screen.fill(DARKGREY)
            self.object_renderer.draw()
            self.draw_hud()
    
    def draw_hud(self):
        # Fps
        self.draw_text('FPS: ' +  "{:.0f}".format(self.clock.get_fps()),10, 5, 10, 'left')
        # Map
        self.map.draw()
        # Stamina bar
        self.pathfinding.get_path(self.object_handler.npc.map_pos, self.player.map_pos)
        color = 'white'
        if len(self.pathfinding.path) <= 15:
            color = 'red'
        elif len(self.pathfinding.path) <= 30:
            color = 'yellow'
        else:
            color = 'white'
        self.screen.blit(self.stamina_icon, (10, MONITOR_H - 50))
        pg.draw.rect(self.screen, color, pg.Rect(60, MONITOR_H - 40, int(self.player.stamina) * 2.5, 25))
        pg.draw.rect(self.screen, 'green', pg.Rect(60, MONITOR_H - 40, 375, 25) , 1)
    
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