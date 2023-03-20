import pygame as pg
import random
from os import path
from decimal import Decimal
from src.sprite_object import *
from src.settings import *

class NPC(AnimatedSprite):
    def __init__(self, game, path, pos, scale, shift, animation_time):
        super().__init__(game, path, pos, scale, shift, animation_time)
        self.game = game
        self.grid_x, self.grid_y = Decimal(pos[0]) - Decimal('0.5'), Decimal(pos[1]) - Decimal('0.5')
        self.direction = random.choice( [ 'N', 'S', 'E', 'W' ] ) 
        self.next_mob_movement = pg.time.get_ticks()
        self.searching, self.roaming, self.chasing = False, True, False
        self.npc_rect = pg.Rect(self.x * 100, self.y * 100, 50, 50)
        self.npc_rect.center = (self.grid_x, self.grid_y)
        self.screen_effect = False
        self.chaise_audio = True
        self.screen_effect_time = 350
        self.chasing_time = 3500
        self.ambient_noise_chance_time = 15000

    def update(self):
        self.check_animation_time()
        self.get_sprite()
        self.run_logic()

    def movement(self):
        if self.direction == 'N':
            self.y -= float(MOB_SPEED)
            self.grid_y -= MOB_SPEED
        elif self.direction == 'E':
            self.x += float(MOB_SPEED)
            self.grid_x += MOB_SPEED
        elif self.direction == 'S':
            self.y += float(MOB_SPEED)
            self.grid_y += MOB_SPEED
        else:  # W
            self.x -= float(MOB_SPEED)
            self.grid_x -= MOB_SPEED
                
    def run_logic(self):
        now = pg.time.get_ticks()
        if now > self.next_mob_movement:
            # Determines npc speed, as well as ambient noise chance and screen effect
            if self.screen_effect:
                if now > self.screen_effect_time:
                    self.screen_effect_time = now + 350
                    self.game.screen.fill('red')

            if self.roaming:
                self.next_mob_movement = now + 15
            elif self.searching:
                self.next_mob_movement = now + 10
            else:
                self.next_mob_movement = now + 5
                self.ambient_noise_chance = now + 15000

            self.check_collision()
            self.check_state()

            # Checks between three states: roaming, searching and chasing
            if self.roaming:
                # Every 15 seconds, there is a 5% chance of playing an ambient sound and npc gettting players position
                if now > self.ambient_noise_chance_time:
                    if random.randrange(0,100) <= 5:
                        sound = random.randrange(1, 3)
                        self.game.effects_sounds['ambient' + str(sound)].play()

                        self.game.player.noise_pos = self.game.player.map_pos
                        self.searching, self.roaming, self.chasing = True, False, False
                    else:
                        self.ambient_noise_chance_time = now + 10000   

                # Checks if the grid position is an integer to calculate a direction
                if float(self.grid_x).is_integer() and float(self.grid_y).is_integer():
                    exits = self.availableMoves()
                    # Generally: Keep moving in current direction, never u-turn 
                    opposite = self.getOppositeDirection()
                    # 50% change of continuing forward at an intersection
                    if self.direction in exits and (len(exits) == 1 or random.randrange(0,100) <= 50):
                        pass
                    elif self.direction not in exits and len(exits) == 1:
                        self.direction = exits[0]   # maybe u-turn
                    else:  # more than 1 exit
                        if opposite in exits:
                            exits.remove(opposite)
                        if len(exits) > 0:
                            self.direction = random.choice(exits)
                self.movement()

            elif self.searching:
                # Checks if the monster is still chasing the player, else stop the chase music and screen effect
                chase = pg.time.get_ticks()
                if chase < self.chasing_time:
                    self.game.player.noise_pos = self.game.player.map_pos
                elif not(self.chaise_audio):
                    self.game.effects_sounds['chase_music'].fadeout(1000)
                    self.game.effects_sounds['ambient_music'].play(loops=-1)
                    self.chaise_audio = True
                    self.screen_effect = False
                # Calculates the next position
                next_pos = self.game.pathfinding.get_path(self.map_pos, self.game.player.noise_pos)
                next_x, next_y = next_pos  
                # Only moves if the position is an integer
                if float(self.grid_x).is_integer() and float(self.grid_y).is_integer():
                    self.searching_moves(next_x, next_y)
                # Only moves if the npc is in a different tile from the goal tile
                if (float(self.grid_x), float(self.grid_y)) != (next_x, next_y):
                    self.movement()
                else:
                    self.searching, self.roaming, self.chasing =  False, True, False

            elif self.chasing:
                # Starts chase music, npc scream and screen effect.
                self.screen_effect = True
                if self.chaise_audio:
                    self.game.effects_sounds['ambient_music'].stop()
                    self.game.effects_sounds['chase_music'].play(loops=-1)
                    self.game.effects_sounds['npc_scream'].play()
                    self.chaise_audio = False
                self.chasing_time = pg.time.get_ticks() + 3500
                # Calculates the next position
                next_pos = self.game.pathfinding.get_path(self.map_pos, self.game.player.map_pos)
                next_x, next_y = next_pos  
                # Only moves if the position is an integer
                if float(self.grid_x).is_integer() and float(self.grid_y).is_integer():
                    self.searching_moves(next_x,next_y)
                # Only moves if the npc is in a different tile from the goal tile
                if (float(self.grid_x), float(self.grid_y)) != (next_x, next_y):
                    self.movement()

        # Positions the npc rect in the grid
        self.npc_rect.center = (self.x * 100, self.y * 100)
            
    def check_collision(self):
        if self.npc_rect.colliderect(self.game.player.player_rect):
            self.game.object_handler.game_over()
        elif self.npc_rect.colliderect(self.game.player.player_rect):
            self.game.object_handler.win()

    def check_state(self):
        self.ray_cast_value = self.ray_cast_player_npc()
        if self.ray_cast_value:
            self.searching, self.roaming, self.chasing = False, False, True
        elif self.roaming:
            self.searching, self.roaming, self.chasing = False, True, False
        else:
            self.searching, self.roaming, self.chasing = True, False, False

    def searching_moves(self, x, y):
        map_x, map_y = (int(self.grid_x), int(self.grid_y))
        # Checks the next direction in a lineal pattern
        if y == map_y and x != map_x:
            if x > map_x:
                self.direction = 'E'
            else:
                self.direction = 'W'
        elif y != map_y and x == map_x:
            if y > map_y:
                self.direction = 'S'
            else:
                self.direction = 'N'
        # If the next direction is after a curve, the pathfinding ignores the corner a makes a diagonal. This helps to fix that.
        else:
            if y > map_y:
                if x > map_x:
                    if MINI_MAP[map_y][map_x + 1] not in [1, 2, 3, 4, 5, 6, 7, 8]:
                        self.direction = 'E'
                    else:
                        self.direction = 'S'
                else:
                    if MINI_MAP[map_y][map_x - 1] not in [1, 2, 3, 4, 5, 6, 7, 8]:
                        self.direction = 'W'
                    else:
                        self.direction = 'S'
            else:
                if x > map_x:
                    if MINI_MAP[map_y][map_x + 1] not in [1, 2, 3, 4, 5, 6, 7, 8]:
                        self.direction = 'E'
                    else:
                        self.direction = 'N'
                else:
                    if MINI_MAP[map_y][map_x - 1] not in [1, 2, 3, 4, 5, 6, 7, 8]:
                        self.direction = 'W'
                    else:
                        self.direction = 'N'

    def availableMoves(self):
        #Consult the map to see where is good to go from here
        map_x, map_y = (int(self.grid_x), int(self.grid_y))
        exits = []
        if MINI_MAP[map_y - 1][map_x] not in [1, 2, 3]:
            exits.append('N')
        if MINI_MAP[map_y][map_x + 1] not in [1, 2, 3]:
            exits.append('E')
        if MINI_MAP[map_y + 1][map_x] not in [1, 2, 3]:
            exits.append('S')
        if MINI_MAP[map_y][map_x - 1] not in [1, 2, 3]:
            exits.append('W')
        return exits

    def getOppositeDirection(self):
        opposites = { 'N':'S', 'S':'N', 'E':'W', 'W':'E' }
        return opposites[self.direction]
    
    def ray_cast_player_npc(self):
        if self.game.player.map_pos == self.map_pos:
            return True

        wall_dist_v, wall_dist_h = 0, 0
        player_dist_v, player_dist_h = 0, 0

        ox, oy = self.game.player.pos
        x_map, y_map = self.game.player.map_pos

        ray_angle = self.theta

        sin_a = math.sin(ray_angle)
        cos_a = math.cos(ray_angle)

        # horizontals
        y_hor, dy = (y_map + 1, 1) if (sin_a + 1e-6) > 0 else (y_map - 1e-6, -1)

        depth_hor = (y_hor - oy) / (sin_a + 1e-6)
        x_hor = ox + depth_hor * cos_a

        delta_depth = dy / (sin_a + 1e-6)
        dx = delta_depth * cos_a

        for i in range(MAX_DEPTH):
            tile_hor = int(x_hor), int(y_hor)
            if tile_hor == self.map_pos:
                player_dist_h = depth_hor
                break
            if tile_hor in self.game.map.world_map:
                wall_dist_h = depth_hor
                break
            x_hor += dx
            y_hor += dy
            depth_hor += delta_depth

        # verticals
        x_vert, dx = (x_map + 1, 1) if cos_a > 0 else (x_map - 1e-6, -1)

        depth_vert = (x_vert - ox) / cos_a
        y_vert = oy + depth_vert * (sin_a + 1e-6)

        delta_depth = dx / cos_a
        dy = delta_depth * (sin_a + 1e-6)

        for i in range(MAX_DEPTH):
            tile_vert = int(x_vert), int(y_vert)
            if tile_vert == self.map_pos:
                player_dist_v = depth_vert
                break
            if tile_vert in self.game.map.world_map:
                wall_dist_v = depth_vert
                break
            x_vert += dx
            y_vert += dy
            depth_vert += delta_depth

        player_dist = max(player_dist_v, player_dist_h)
        wall_dist = max(wall_dist_v, wall_dist_h)

        if 0 < player_dist < wall_dist or not wall_dist:
            return True
        return False

    @property
    def map_pos(self):
        return int(self.grid_x), int(self.grid_y)