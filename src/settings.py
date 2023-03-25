import math
from screeninfo import get_monitors
from decimal import Decimal

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (124, 252, 0)
DARKGREY = (78, 78, 78)

# Game settings
MONITOR_W, MONITOR_H = get_monitors()[0].width, get_monitors()[0].height
HALF_WIDTH, WIDTH = MONITOR_W // 2, MONITOR_W // 4
HALF_HEIGHT, HEIGHT = MONITOR_H // 2, MONITOR_W // 4
FPS = 90
FONT = 'resources/font/PixeloidMono-VGj6x.ttf'
ICON = 'resources/textures/game_icon.ico'

# Music and sound effects
MENU_MUSIC = 'resources/music/menu_music.mp3'
NPC1_CHASE = 'resources/music/npc1_chase_music.mp3'
NPC2_CHASE = 'resources/music/npc2_chase_music.mp3'
NPC3_CHASE = 'resources/music/npc3_chase_music.mp3'
NPC4_CHASE = 'resources/music/npc4_chase_music.mp3'

EFFECT_SOUNDS = {
                'chase_music':     'resources/music/npc1_chase_music.mp3',
                'ambient_music':   'resources/music/ambient_music.mp3',
                'ambient1':        'resources/sounds/ambient_noise1.wav',
                'ambient2':        'resources/sounds/ambient_noise2.wav',
                'ambient3':        'resources/sounds/ambient_noise3.wav',
                'ambient4':        'resources/sounds/ambient_noise4.wav',
                'key_grab':        'resources/sounds/key_grab.wav',
                'npc_scream':      'resources/sounds/npc_scream.wav',
                'running':         'resources/sounds/running.wav',
                'steps':           'resources/sounds/steps.wav'
                }

# Player settings
PLAYER_ANGLE = 0
PLAYER_WALKING_SPEED = 0.001
PLAYER_RUNNING_SPEED = 0.005
PLAYER_ROT_SPEED = 0.002
PLAYER_SIZE_SCALE = 100
STAMINA_ICON = 'resources/textures/stamina_icon.png'

# Mouse settings
MOUSE_MAX_REL = 40
MOUSE_BORDER_LEFT = 100
MOUSE_BORDER_RIGHT = MONITOR_W - MOUSE_BORDER_LEFT

# Raycasting settings
FOV = math.pi / 3
HALF_FOV = FOV / 2
NUM_RAYS = WIDTH // 2 
HALF_NUM_RAYS = NUM_RAYS // 2
DELTA_ANGLE = FOV / NUM_RAYS
MAX_DEPTH = 50

SCREEN_DIST = HALF_WIDTH / math.tan(HALF_FOV)
SCALE = MONITOR_W // NUM_RAYS

# Textures settings
TEXTURE_SIZE = 512
HALF_TEXTURE_SIZE = TEXTURE_SIZE // 2

# NPC settings
NPC1 = 'resources/sprites/animated/npc1/walking1.png'
NPC2 = 'resources/sprites/animated/npc2/enemy2.png'
NPC3 = 'resources/sprites/animated/npc3/enemy3.png'
NPC4 = 'resources/sprites/animated/npc4/enemy4.png'
MOB_SPEED = Decimal('0.025')