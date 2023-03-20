import pygame as pg
import math
from decimal import Decimal
from src.settings import *

class Player:
    def __init__(self, game):
        self.game = game
        self.x, self.y = PLAYER_POS[0]
        self.angle = PLAYER_ANGLE
        self.rel = 0
        self.time_prev = pg.time.get_ticks()
        self.noise_pos = self.map_pos
        self.stamina = Decimal('150')
        self.player_rect = pg.Rect(self.x * 100 - 16, self.y * 100 - 16, 50, 50)
        self.standing_still, self.walking, self.running = False, True, False
        self.next_sound = 0
        self.resting = False

    def movement(self):
        sin_a = math.sin(self.angle)
        cos_a = math.cos(self.angle)
        dx, dy = 0, 0
        speed = PLAYER_WALKING_SPEED * self.game.delta_time
        speed_sin = speed * sin_a
        speed_cos = speed * cos_a

        keys = pg.key.get_pressed()

        if keys[pg.K_LSHIFT] and float(self.stamina) > 0 and not self.resting:
            # Change speed
            speed = PLAYER_RUNNING_SPEED * self.game.delta_time
            speed_sin = speed * sin_a
            speed_cos = speed * cos_a

            if not(self.game.object_handler.npc.chasing):
                self.noise_pos = self.map_pos
                self.game.object_handler.npc.roaming, self.game.object_handler.npc.searching = False, True
            self.stamina -= Decimal('0.5')
        elif float(self.stamina) < 150:
            self.stamina += Decimal('0.25')
            self.resting = True
            if float(self.stamina) > 20:
                self.resting = False

        if keys[pg.K_w]:
            dx += speed_cos
            dy += speed_sin
        if keys[pg.K_s]:
            dx += -speed_cos
            dy += -speed_sin
        if keys[pg.K_a]:
            dx += speed_sin
            dy += -speed_cos
        if keys[pg.K_d]:
            dx += -speed_sin
            dy += speed_cos
        if keys[pg.K_m]:
            self.game.map.draw()

        # Running
        now = pg.time.get_ticks()
        if keys[pg.K_LSHIFT] and float(self.stamina) >= 20 and (dx != 0 or dy != 0):
            # Check if the player was walking
            if self.walking:
                self.game.effects_sounds['steps'].stop()
                self.game.effects_sounds['running'].play()
                self.next_sound = now + 2500
                self.standing_still, self.walking, self.running = False, False, True
            # This plays the sounds every 2.5 seconds
            elif now > self.next_sound:
                self.next_sound = now + 2500
                self.game.effects_sounds['running'].play()
        # Walking
        elif (not(keys[pg.K_LSHIFT]) and (dx != 0 or dy != 0)) or (keys[pg.K_LSHIFT] and float(self.stamina) <= 0 and (dx != 0 or dy != 0)):
            # Check if player was running
            if self.running:
                self.game.effects_sounds['running'].stop()
                self.game.effects_sounds['steps'].play()
                self.next_sound = now + 2500
                self.standing_still, self.walking, self.running = False, True, False
            # This plays the sounds every 2.5 seconds
            elif now > self.next_sound:
                self.next_sound = now + 2500
                self.game.effects_sounds['steps'].play()
        # Not moving
        elif dx == 0 and dy == 0:
            self.standing_still = True
            if self.walking:
                self.game.effects_sounds['steps'].stop()
                self.next_sound = now 
            elif self.running:
                self.game.effects_sounds['running'].stop()
                self.next_sound = now 
        
        self.player_rect.center = (self.x * 100, self.y * 100)

        self.check_wall_collision(dx, dy)

        self.angle %= math.tau

        self.game.map.add()

    def check_wall(self, x, y):
        return (x, y) not in self.game.map.world_map

    def check_wall_collision(self, dx, dy):
        scale = PLAYER_SIZE_SCALE / self.game.delta_time
        if self.check_wall(int(self.x + dx * scale), int(self.y)):
            self.x += dx
        if self.check_wall(int(self.x), int(self.y + dy * scale)):
            self.y += dy

    def mouse_control(self):
        mx, my = pg.mouse.get_pos()
        if mx < MOUSE_BORDER_LEFT or mx > MOUSE_BORDER_RIGHT:
            pg.mouse.set_pos([HALF_WIDTH, HALF_HEIGHT])
        self.rel = pg.mouse.get_rel()[0]
        self.rel = max(-MOUSE_MAX_REL, min(MOUSE_MAX_REL, self.rel))
        self.angle += self.rel * MOUSE_SENSITIVITY * self.game.delta_time

    def update(self):
        self.movement()
        self.mouse_control()

    @property
    def pos(self):
        return self.x, self.y

    @property
    def map_pos(self):
        return int(self.x), int(self.y)