WINDOW_WIDTH = 1280
WINDOW_HEIGHT = 960

WITH_CRT = False

BLOCK_MAP = [
	'            ',
 	'            ',
	'            ',  
 	'            ',
  '            ',
  '            ',  
	'bbbbbbbbbbbb',
	'rrrrrzzrrrrr',
	'bbbbbbbbbbbb',
	'rrrrrrrrrrrr',
 	'            ',
	'            ',
	'            ',
	'            ',
	'            ',
  '            ']

BLOCK_DEFS = {
	'r': (1, 'red'),
	'b': (1, 'blue'),
	'g': (2, 'green'),
	'o': (3, 'orange'),
	'p': (4, 'purple'),
	'e': (5, 'grey'),
	'z': (6, 'bronze'),
}

# note: for now, we accept that there can only be one block-type
# with a particular in this dict, and that it will be an arbitrary one
BLOCK_TYPE_BY_HEALTH = {
	h : n for (h,n) in BLOCK_DEFS.values()
}

GAP_SIZE = 2
BLOCK_HEIGHT = WINDOW_HEIGHT / len(BLOCK_MAP) - GAP_SIZE
BLOCK_WIDTH = WINDOW_WIDTH / len(BLOCK_MAP[0]) - GAP_SIZE
TOP_OFFSET = WINDOW_HEIGHT // 30

PLAYER_SPEED = 800
BALL_INIT_SPEED = 400
BALL_MAX_SPEED = 700
BALL_SPEED_INC = 25
BALL_SPEED_INTERVAL = 30000

UPGRADE_CHANCE = 0.8
UPGRADES = ['speed','laser','heart','size']

TIMED_UPGRADES = ['speed','laser','size']
TIMED_UPGRADES_LAST_IN_TICKS = 10000

SQUARE_ROOT_2_DIV_2 = 0.707
SQUARE_ROOT_3_DIV_2 = 0.866

# must be ordered from largest to -1 
# (-1 to catch any rounding errors, which end up with an x below 0)
COLLISION_DIRECTION_VECTORS = {
	0.9:  (SQUARE_ROOT_3_DIV_2,-0.5),
	0.8:  (SQUARE_ROOT_2_DIV_2,-SQUARE_ROOT_2_DIV_2),
	0.65: (0.5,-SQUARE_ROOT_3_DIV_2),
	0.35: (1,-1),
	0.2:  (-0.5,-SQUARE_ROOT_3_DIV_2),
	0.1:  (-SQUARE_ROOT_2_DIV_2,-SQUARE_ROOT_2_DIV_2),
	-1:   (-SQUARE_ROOT_3_DIV_2,-0.5), 
}