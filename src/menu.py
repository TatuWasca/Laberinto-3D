import pygame as pg
import sys
from os import path
from src.settings import *

########################################(Menu superclass)########################################
class Menu:
    def __init__(self, game):
        self.game = game
        self.background_image = pg.image.load(path.join(self.game.root_file, 'resources/textures/background.png')).convert()
        self.go_image = pg.image.load(path.join(self.game.root_file, 'resources/textures/game_over.png')).convert_alpha()
        self.background_image = pg.transform.scale(self.background_image, (MONITOR_W, MONITOR_H))
        self.go_image = pg.transform.scale(self.go_image, (MONITOR_W, MONITOR_H))
        self.UP_KEY, self.DOWN_KEY, self.START_KEY, self.BACK_KEY, self.RIGHT_KEY, self.LEFT_KEY = False, False, False, False, False, False
        self.mid_w, self.mid_h = MONITOR_W / 2, MONITOR_H / 2
        self.run_display = True
        self.cursor_rect = pg.Rect(0, 0, 20, 20)
        self.offset = -50

    ############### draw cursor ###############
    def draw_cursor(self):
        self.game.draw_text('*', 20, self.cursor_rect.x, self.cursor_rect.y + 5, 'center')

    ############### blit screen ###############
    def blit_screen(self):
        self.game.draw_text('FPS: ' +  "{:.0f}".format(self.game.clock.get_fps()), 10, 5, 10, 'left')  
        self.UP_KEY, self.DOWN_KEY, self.START_KEY, self.BACK_KEY, self.RIGHT_KEY, self.LEFT_KEY = False, False, False, False, False, False

        # Fixes player and mob movement if the game is paused
        self.game.dt = self.game.clock.tick(FPS) / 1000.0# fix for Python 2.x

        pg.display.update()
    
    ############### events ###############
    def events(self):
        for event in pg.event.get():
            if event.type == pg.QUIT:
                self.game.quit()
            if event.type == pg.KEYDOWN:
                if event.key == pg.K_RETURN:
                    self.START_KEY = True
                if event.key == pg.K_BACKSPACE or event.key == pg.K_ESCAPE:
                    self.BACK_KEY = True
                if event.key == pg.K_DOWN or event.key == pg.K_s:
                    self.DOWN_KEY = True
                if event.key == pg.K_UP or event.key == pg.K_w:
                    self.UP_KEY = True
                if event.key == pg.K_LEFT or event.key == pg.K_a:
                    self.LEFT_KEY = True
                if event.key == pg.K_RIGHT or event.key == pg.K_d:
                    self.RIGHT_KEY = True

########################################(MainMenu class)########################################
class MainMenu(Menu):
    def __init__(self, game):
        Menu.__init__(self, game)
        self.state = "Start"
        self.startx, self.starty = self.mid_w, self.mid_h + 30
        self.optionsx, self.optionsy = self.mid_w, self.mid_h + 50
        self.creditsx, self.creditsy = self.mid_w, self.mid_h + 70
        self.exitx, self.exity = self.mid_w, self.mid_h + 90
        self.cursor_rect.midtop = (self.startx + self.offset, self.starty)

        pg.mixer.music.load(path.join(self.game.root_file, MENU_MUSIC))
        pg.mixer.music.set_volume(self.game.music_vol / 100)
        pg.mixer.music.play(loops=-1)
    
    ############### display menu ###############
    def display_menu(self):
        self.run_display = True

        self.game.screen.blit(self.background_image, (0,0))
        self.cursor_rect.midtop = (self.startx + self.offset, self.starty)
        self.state = 'Start'

        while self.run_display:
            self.events()
            self.check_input()

            self.game.screen.blit(self.background_image, (0,0))
            self.game.draw_text('Laberinto 3D', 20, self.mid_w, self.mid_h - 20, 'center')
            self.game.draw_text('Start Game', 15, self.startx, self.starty, 'center')
            self.game.draw_text('Options', 15, self.optionsx, self.optionsy, 'center')
            self.game.draw_text('Credits', 15, self.creditsx, self.creditsy, 'center')
            self.game.draw_text('Exit', 15, self.exitx, self.exity, 'center')

            self.draw_cursor()
            self.blit_screen()

    ############### move cursor ###############
    def move_cursor(self):
        if self.DOWN_KEY:
            if self.state == 'Start':
                self.cursor_rect.midtop = (self.optionsx + self.offset, self.optionsy)
                self.state = 'Options'
            elif self.state == 'Options':
                self.cursor_rect.midtop = (self.creditsx + self.offset, self.creditsy)
                self.state = 'Credits'
            elif self.state == 'Credits':
                self.cursor_rect.midtop = (self.exitx + self.offset, self.exity)
                self.state = 'Exit'
            elif self.state == 'Exit':
                self.cursor_rect.midtop = (self.startx + self.offset, self.starty)
                self.state = 'Start'
        elif self.UP_KEY:
            if self.state == 'Start':
                self.cursor_rect.midtop = (self.exitx + self.offset, self.exity)
                self.state = 'Exit'
            elif self.state == 'Options':
                self.cursor_rect.midtop = (self.startx + self.offset, self.starty)
                self.state = 'Start'
            elif self.state == 'Credits':
                self.cursor_rect.midtop = (self.optionsx + self.offset, self.optionsy)
                self.state = 'Options'
            elif self.state == 'Exit':
                self.cursor_rect.midtop = (self.creditsx + self.offset, self.creditsy)
                self.state = 'Credits'

    ############### check input ###############
    def check_input(self):
        self.move_cursor()
        if self.BACK_KEY:
            pg.quit()
            sys.exit()
        elif self.START_KEY:
            if self.state == 'Start':
                pg.mixer.music.fadeout(1500)
                self.game.effects_sounds['ambient_music'].play(loops=-1, fade_ms=2500)
                self.game.new_game()

                self.run_display = False
                self.game.playing = True
            elif self.state == 'Options':
                self.game.curr_menu = self.game.options
            elif self.state == 'Credits':
                self.game.curr_menu = self.game.credits
            elif self.state == 'Exit':
                pg.quit()
                sys.exit()
            self.run_display = False

########################################(OptionsMenu)########################################
class OptionsMenu(Menu):
    def __init__(self, game):
        Menu.__init__(self, game)
        self.state = 'Fps'
        self.genvolx, self.genvoly = self.mid_w - 140, self.mid_h  + 30
        self.musvolx, self.musvoly = self.mid_w - 140, self.mid_h  + 50
        self.appx, self.appy = self.mid_w - 150, self.mid_h + 80
        self.cursor_rect.midtop = (self.genvolx + self.offset, self.genvoly)

        # Variables
        self.new_general_vol = int(self.game.configParser.get("info","GENERAL_VOLUME"))
        self.new_music_vol = int(self.game.configParser.get("info","MUSIC_VOLUME"))

    ############### display menu ###############
    def display_menu(self):
        self.run_display = True

        self.cursor_rect.midtop = (self.genvolx + self.offset, self.genvoly)
        self.state = 'General volume'
            
        while self.run_display:
            self.events()

            self.game.screen.blit(self.background_image, (0,0))
            self.game.draw_text('Options', 20, self.mid_w, self.mid_h - 20, 'center')

            self.game.draw_text('General volume', 15, self.genvolx, self.genvoly, 'left')
            self.game.draw_text(str(self.new_general_vol), 15, self.genvolx + 200, self.genvoly, 'left')
            self.game.draw_text('Music volume', 15, self.musvolx, self.musvoly, 'left')
            self.game.draw_text(str(self.new_music_vol), 15, self.musvolx + 200, self.musvoly, 'left')

            self.game.draw_text('Apply changes', 15, self.appx, self.appy, 'left')

            self.check_input()
            self.draw_cursor()
            self.blit_screen()

    ############### move cursor ###############
    def move_cursor(self):
        if self.BACK_KEY:
            self.game.curr_menu = self.game.main_menu
            self.run_display = False
        elif self.DOWN_KEY:
            if self.state == 'General volume':
                self.cursor_rect.midtop = (self.musvolx + self.offset, self.musvoly)
                self.state = 'Music volume'
            elif self.state == 'Music volume':
                self.cursor_rect.midtop = (self.appx+ self.offset, self.appy)
                self.state = 'Apply'
            elif self.state == 'Apply':
                self.cursor_rect.midtop = (self.genvolx + self.offset, self.genvoly)
                self.state = 'General volume'
        elif self.UP_KEY:
            if self.state == 'General volume':
                self.cursor_rect.midtop = (self.appx+ self.offset, self.appy)
                self.state = 'Apply'
            elif self.state == 'Music volume':
                self.cursor_rect.midtop = (self.genvolx + self.offset, self.genvoly)
                self.state = 'General volume'
            elif self.state == 'Apply':
                self.cursor_rect.midtop = (self.musvolx + self.offset, self.musvoly)
                self.state = 'Music volume'

    ############### check input ###############
    def check_input(self):
        self.move_cursor()
        if self.LEFT_KEY:
            if self.state == 'General volume':
                if self.new_general_vol > 0:
                    self.new_general_vol -= 5
            elif self.state == 'Music volume':
                if self.new_music_vol > 0:
                    self.new_music_vol -= 5
        elif self.RIGHT_KEY:
            if self.state == 'General volume':
                if self.new_general_vol < 100:
                    self.new_general_vol += 5
            elif self.state == 'Music volume':
                if self.new_music_vol < 100:
                    self.new_music_vol += 5
        elif self.START_KEY:
            if self.state == 'Apply':
                # Setting the configuration
                self.game.configParser.set("info","GENERAL_VOLUME", str(self.new_general_vol)) 
                self.game.configParser.set("info","MUSIC_VOLUME", str(self.new_music_vol))

                # Writing the new config into the file
                with open(self.game.configFilePath, 'w') as configfile:
                    self.game.configParser.write(configfile)
                    configfile.close()

                # Reloading every variable
                self.game.general_vol = int(self.game.configParser.get("info","GENERAL_VOLUME"))
                self.game.music_vol = int(self.game.configParser.get("info","MUSIC_VOLUME"))

                # Change volume
                for type in self.game.effects_sounds:
                    if type in ['chase_music', 'ambient_music']:
                        self.game.effects_sounds[type].set_volume(self.game.music_vol / 100)
                    else:
                        self.game.effects_sounds[type].set_volume(self.game.general_vol / 100)
                pg.mixer.music.set_volume(self.game.music_vol / 100)

########################################(Credits menu)########################################
class CreditsMenu(Menu):
    def __init__(self,game):
        Menu.__init__(self, game)
        self.state = 'Credits'

    ############### display menu ###############
    def display_menu(self):
        self.run_display = True
        while self.run_display:
            self.events()
            if self.START_KEY or self.BACK_KEY:
                self.game.curr_menu = self.game.main_menu
                self.run_display = False
            self.game.screen.blit(self.background_image, (0,0))

            self.game.draw_text('Credits', 20, self.mid_w, self.mid_h - 20, 'center')
            self.game.draw_text('Programming by TatuWasca', 15, self.mid_w, self.mid_h + 10, 'center')
            self.game.draw_text('Textures by DoomManiac', 15, self.mid_w, self.mid_h + 30, 'center')

            self.blit_screen()

########################################(PauseMenu)########################################
class PauseMenu(Menu):
    def __init__(self, game):
        Menu.__init__(self, game)
        self.state = "Resume"
        self.resumex, self.resumey = self.mid_w, self.mid_h + 30
        self.exitx, self.exity = self.mid_w, self.mid_h + 50
        self.cursor_rect.midtop = (self.resumex + self.offset, self.resumey)
    
    ############### display menu ###############
    def display_menu(self):
        self.run_display = True

        self.cursor_rect.midtop = (self.resumex + self.offset, self.resumey)
        self.state = 'Resume'

        if self.game.player.walking:
            self.game.effects_sounds['steps'].stop()
            self.game.player.next_sound = 0
        elif self.game.player.running:
            self.game.effects_sounds['running'].stop()
            self.game.player.next_sound = 0
        elif self.game.player.standing_still:
            self.game.player.next_sound = 0

        if self.game.object_handler.npc.chasing:
            self.game.effects_sounds['chase_music'].set_volume(0.0)
        else:
            self.game.effects_sounds['ambient_music'].set_volume(0.0)

        while self.run_display:
            self.events()
            self.check_input()

            # Draws screen
            self.game.screen.blit(self.background_image, (0,0))
            
            self.game.draw_text('Paused', 20, self.mid_w, self.mid_h - 20, 'center')
            self.game.draw_text('Resume', 15, self.resumex, self.resumey, 'center')
            self.game.draw_text('Exit', 15, self.exitx, self.exity, 'center')

            self.draw_cursor()
            self.blit_screen()

    ############### move cursor ###############
    def move_cursor(self):
        if self.DOWN_KEY or self.UP_KEY:
            if self.state == 'Resume':
                self.cursor_rect.midtop = (self.exitx + self.offset, self.exity)
                self.state = 'Exit'
            elif self.state == 'Exit':
                self.cursor_rect.midtop = (self.resumex + self.offset, self.resumey)
                self.state = 'Resume'

    ############### check input ###############
    def check_input(self):
        self.move_cursor()
        if self.START_KEY:
            if self.state == 'Resume':
                if self.game.object_handler.npc.chasing:
                    self.game.effects_sounds['chase_music'].set_volume(self.game.music_vol / 100)
                else:
                    self.game.effects_sounds['ambient_music'].set_volume(self.game.music_vol / 100)
                self.game.playing = True
            elif self.state == 'Exit':
                if self.game.object_handler.npc.chasing:
                    self.game.effects_sounds['chase_music'].set_volume(self.game.music_vol / 100)
                    self.game.effects_sounds['chase_music'].stop()
                else:
                    self.game.effects_sounds['ambient_music'].set_volume(self.game.music_vol / 100)
                    self.game.effects_sounds['ambient_music'].stop()
                
                pg.mixer.music.load(path.join(self.game.root_file, MENU_MUSIC))
                pg.mixer.music.set_volume(self.game.music_vol / 100)
                pg.mixer.music.play(loops=-1)

                for y in range(MAP_HEIGHT - 1):
                    for x in range(MAP_WIDTH - 1):
                        if (x, y) in self.game.map.posible_spawns:
                            MINI_MAP[y][x] = 3
                        elif (x, y) in self.game.map.door_spawns:
                            MINI_MAP[y][x] = 2
                self.game.curr_menu = self.game.main_menu
            self.run_display = False

########################################(GameoverMenu)########################################
class GameoverMenu(Menu):
    def __init__(self, game):
        Menu.__init__(self, game)
        self.state = "Retry"
        self.retryx, self.retryy = self.mid_w, self.mid_h + 30
        self.exitx, self.exity = self.mid_w, self.mid_h + 50
        self.cursor_rect.midtop = (self.retryx + self.offset, self.retryy)
    
    ############### display menu ###############
    def display_menu(self):
        self.run_display = True
        
        self.cursor_rect.midtop = (self.retryx + self.offset, self.retryy)
        self.state = 'Retry'

        if self.game.player.walking:
            self.game.effects_sounds['steps'].stop()
            self.game.player.next_sound = 0
        elif self.game.player.running:
            self.game.effects_sounds['running'].stop()
            self.game.player.next_sound = 0
        elif self.game.player.standing_still:
            self.game.player.next_sound = 0

        self.game.effects_sounds['chase_music'].fadeout(2000)

        while self.run_display:
            self.events()
            self.check_input()

            # Draws screen
            self.game.screen.fill(BLACK)
            self.game.screen.blit(self.go_image, (0,0))

            self.game.draw_text('Game Over', 20, self.mid_w, self.mid_h - 20, 'center')
            self.game.draw_text('Retry', 15, self.retryx, self.retryy, 'center')
            self.game.draw_text('Exit', 15, self.exitx, self.exity, 'center')

            self.draw_cursor()
            self.blit_screen()

    ############### move cursor ###############
    def move_cursor(self):
        if self.DOWN_KEY or self.UP_KEY:
            if self.state == 'Retry':
                self.cursor_rect.midtop = (self.exitx + self.offset, self.exity)
                self.state = 'Exit'
            elif self.state == 'Exit':
                self.cursor_rect.midtop = (self.retryx + self.offset, self.retryy)
                self.state = 'Retry'

    ############### check input ###############
    def check_input(self):
        self.move_cursor()
        if self.START_KEY:
            if self.state == 'Retry':
                self.game.effects_sounds['ambient_music'].play(loops=-1)
                self.game.new_game()
                self.game.playing = True
            elif self.state == 'Exit':
                pg.mixer.music.load(path.join(self.game.root_file, MENU_MUSIC))
                pg.mixer.music.set_volume(self.game.music_vol / 100)
                pg.mixer.music.play(loops=-1)
                self.game.curr_menu = self.game.main_menu
            self.run_display = False

########################################(WinMenu)########################################
class WinMenu(Menu):
    def __init__(self, game):
        Menu.__init__(self, game)
        self.state = "Retry"
        self.retryx, self.retryy = self.mid_w, self.mid_h + 30
        self.exitx, self.exity = self.mid_w, self.mid_h + 50
        self.cursor_rect.midtop = (self.retryx + self.offset, self.retryy)
    
    ############### display menu ###############
    def display_menu(self):
        self.run_display = True

        self.cursor_rect.midtop = (self.retryx + self.offset, self.retryy)
        self.state = 'Retry'

        if self.game.player.walking:
            self.game.effects_sounds['steps'].stop()
            self.game.player.next_sound = 0
        elif self.game.player.running:
            self.game.effects_sounds['running'].stop()
            self.game.player.next_sound = 0
        elif self.game.player.standing_still:
            self.game.player.next_sound = 0
        
        if self.game.object_handler.npc.screen_effect:
            self.game.effects_sounds['chase_music'].fadeout(2000)
        else:
            self.game.effects_sounds['ambient_music'].fadeout(2000)

        while self.run_display:
            self.events()
            self.check_input()

            # Draws screen
            self.game.screen.blit(self.background_image, (0,0))

            self.game.draw_text('You Win!', 20, self.mid_w, self.mid_h - 20, 'center')
            self.game.draw_text('Retry', 15, self.retryx, self.retryy, 'center')
            self.game.draw_text('Exit', 15, self.exitx, self.exity, 'center')

            self.draw_cursor()
            self.blit_screen()

    ############### move cursor ###############
    def move_cursor(self):
        if self.DOWN_KEY or self.UP_KEY:
            if self.state == 'Retry':
                self.cursor_rect.midtop = (self.exitx + self.offset, self.exity)
                self.state = 'Exit'
            elif self.state == 'Exit':
                self.cursor_rect.midtop = (self.retryx + self.offset, self.retryy)
                self.state = 'Retry'

    ############### check input ###############
    def check_input(self):
        self.move_cursor()
        if self.START_KEY:
            if self.state == 'Retry':
                self.game.effects_sounds['ambient_music'].play(loops=-1)
                self.game.playing = True
                self.game.new_game()
            elif self.state == 'Exit':
                pg.mixer.music.load(path.join(self.game.root_file, MENU_MUSIC))
                pg.mixer.music.set_volume(self.game.music_vol / 100)
                pg.mixer.music.play(loops=-1)
                self.game.curr_menu = self.game.main_menu
            self.run_display = False