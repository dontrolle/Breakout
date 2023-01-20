WINDOW_WIDTH = 1280
WINDOW_HEIGHT = 744

WITH_CRT = False

BLOCK_MAP = [
	'            ',
	'444557755444',
	'333333333333',
	'222222222222',
	'111111111111',
	'            ',
	'            ',
	'            ',
	'            ',
  '            ']

COLOR_LEGEND = {
	'1': 'blue',
	'2': 'green',
	'3': 'red',
	'4': 'orange',
	'5': 'purple',
	'6': 'bronce',
	'7': 'grey',
}

GAP_SIZE = 2
BLOCK_HEIGHT = WINDOW_HEIGHT / len(BLOCK_MAP) - GAP_SIZE
BLOCK_WIDTH = WINDOW_WIDTH / len(BLOCK_MAP[0]) - GAP_SIZE
TOP_OFFSET = WINDOW_HEIGHT // 30

PLAYER_SPEED = 500
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
	0.9: (SQUARE_ROOT_3_DIV_2,-0.5),
	0.7: (SQUARE_ROOT_2_DIV_2,-SQUARE_ROOT_2_DIV_2),
	0.3: (1,-1),
	0.1: (-SQUARE_ROOT_2_DIV_2,-SQUARE_ROOT_2_DIV_2),
	-1: (-SQUARE_ROOT_3_DIV_2,-0.5), 
}