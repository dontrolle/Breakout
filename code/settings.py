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

UPGRADE_CHANCE = 0.8
UPGRADES = ['speed','laser','heart','size']

TIMED_UPGRADES = ['speed','laser','size']
TIMED_UPGRADES_LAST_IN_TICKS = 10000
