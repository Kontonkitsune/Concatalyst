"""
fuck this shit

Code by: Lucina Riley / Kontonkitsune
Last Updated: 15/7/2023

Action Puzzle thing

Code still being repurposed.

"""

import random
import pygame, sys
import math
from pygame.locals import *

pygame.init()
fps = pygame.time.Clock()

# Global colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)

RED = (255, 63, 63)
YELLOW = (240, 240, 0)
GREEN = (63, 255, 63)
PINK = (255, 127, 255)
BLUE = (0, 0, 255)
CYAN = (0, 255, 255)

SILVER = (232, 245, 255)
GOLD = (220, 188, 12)

REDCAT = (127, 0, 0)
YELLOWCAT = (255, 192, 63)
GREENCAT = (0, 127, 32)
PINKCAT = (192, 64, 192)
BLUECAT = (63, 63, 192)
GOLDCAT = (212, 212, 255)
CYANCAT = (63, 192, 255)

ROSEGOLD = (248,185,150)

	


ColorIndex = (BLACK, 
	PINK,	BLUE,	GREEN,	YELLOW,	RED,	CYAN,		SILVER, 
	PINKCAT,BLUECAT,GREENCAT,YELLOWCAT,REDCAT,CYANCAT,	ROSEGOLD)

# Global constants

# Global defaults
WIDTH = 800
HEIGHT = 800
BOARD_SIZE_X = 10
BOARD_SIZE_Y = 16
FONTSIZE = 30

BASE_POINTS = 100
POINTS_INCREASE = 10

BLOCK_SIZE = 40

MAX_QUEUE_LENGTH = 3

DefaultFont = pygame.font.SysFont("Comic Sans MS", FONTSIZE)



# Global variables
screen_width = WIDTH
screen_height = HEIGHT
centerx = screen_width // 2
centery = screen_height // 2

board_size_x = BOARD_SIZE_X
board_size_y = BOARD_SIZE_Y + 4


boardwidth = (BLOCK_SIZE * board_size_x)
boardheight = (BLOCK_SIZE * ( board_size_y - 4) )

leftscreen = centerx - boardwidth // 2
rightscreen = centerx + boardwidth // 2
topscreen = centery - boardheight // 2
bottomscreen = centery + boardheight // 2


blockPositionX = BOARD_SIZE_X // 2 - 1
blockPositionY = BOARD_SIZE_Y + 1
blockPositionYExact = 0.0 #to deal with the slower fall speeds

Board = []
explodeboard = []

buttonlist = []
colorphase = 0
extrablocks = [[[0,0],[0,0]],[[0,0],[0,0]],[[0,0],[0,0]]]
colorsets = [1,2,3,4,5,6] * 2 + [7]

clock = 0
running = True
optionsmenu = False
menuitemoffset = 0
textoffset = 0
cursor_pos = 0
game_state = False # true if a game is active.
keydown = 0 # this just prevents key stuttering and allows the menu to be navigable.

PieceDict = {
	"full": (1,1,1,1),
	"quarter": (1,1,1,2),
	"half": (1,1,2,2),
	"checker": (1,2,2,1),
	"triple": (1,1,2,3),
	"triplechecker": (1,2,3,1),
	"quad": (1,2,3,4),
	"catalyst": (1,1,1,1)
}
'''PieceDict = {
	"full": [[1,1],[1,1]],
	"quarter": [[1,2],[1,1]],
	"half": [[1,1],[2,2]],
	"checker": [[1,2],[2,1]],
	"triple": [[1,1],[2,3]],
	"triplechecker": [[1,2],[3,1]],
	"quad": [[1,2],[3,4]],
	"catalyst": [[0,0],[0,0]]
}'''
PieceWeights = (["full","quarter","half"] * 4 + ["checker","triple","catalyst"] * 2 + ["triplechecker","quad"] + ["catalyst"] * 12)



# config options
class Config:
	def __init__(self, value = 0, max = 10, min = 0, scale = 1):
		self.value = value
		self.max = max
		self.min = min
		self.scale = scale
		
class Block:
	def __init__(self, tl=0, tr = 0, bl = 0, br = 0):
		self.tl = tl
		self.tr = tr
		self.bl = bl
		self.br = br
		
	def __add__(self, other):
		tl = self.tl + other
		tr = self.tr + other
		bl = self.bl + other
		br = self.br + other
		return Block(tl,tr,bl,br)
		
	def __iadd__(self, other):
		self.tl += other
		self.tr += other
		self.bl += other
		self.br += other
		return self
		
	def __getitem__(self,index):
		match index:
			case 0:
				return tl
			case 1:
				return tr
			case 2:
				return bl
			case 3:
				return br
			case (0,0):
				return tl
			case (0,1):
				return tr
			case (1,0):
				return bl
			case (1,1):
				return br
	
		
	


# window declaration
window = pygame.display.set_mode((WIDTH, HEIGHT),RESIZABLE)
pygame.display.set_caption('Action Puzzler Thing')

def colorchange(color,phase):
	return tuple([((x + phase if x + phase >= 0 else 0) if x + phase < 255 else 255) for x in color])

def init_board() -> None:
	"""This function initializes the game."""
	global Board, explodeboard
	Board = [[0 for x in range(board_size_y)] for y in range(board_size_x)]
	explodeboard = [[0 for x in range(board_size_y)] for y in range(board_size_x)]
	
	'''for x in range(0,len(Board)):
		for y in range(0,random.randint(9,14)):
			Board[x][y] = random.randint(0,3)'''

def isinbounds(x,y):
	if x < 0 or x >= len(Board) or y < 0 or y >= len(Board[0]):
		return False
	else:
		return True
		

def comparesquares(x,y,x2,y2):
	print(x,y,x2,y2)
	if isinbounds(x,y) and isinbounds(x2,y2):
		#print(Board[x][y] % 7,Board[x2][y2],Board[x][y] % 7)
		if Board[x][y] == 0 or Board[x2][y2] == 0:
			return False
		elif Board[x][y] % 7 == Board[x2][y2] or Board[x][y] % 7 == 0 or Board[x2][y2] % 7 == 0:
			return True
		else:
			return False
	else:
		return False

def findclears():
	global explodeboard
	explodeboard = [[0 for x in range(board_size_y)] for y in range(board_size_x)]
	stack = []
	
	for x in range(0,len(Board)):
		for y in range(0,len(Board[x])):
			if Board[x][y] > 7 and Board[x][y] < 15 and explodeboard[x][y] == 0:
				explodeboard[x][y] += 1
				stack.append((x,y))
	while len(stack) > 0:
		print(stack)
		x = stack[0][0]
		y = stack[0][1]
		stack.pop(0)
		if isinbounds(x+1,y) and explodeboard[x+1][y] == 0 and comparesquares(x,y,x+1,y):
			print(comparesquares(x,y,x+1,y))
			stack.append((x+1,y))
			explodeboard[x+1][y] = explodeboard[x][y] + 1
						
		if isinbounds(x-1,y) and explodeboard[x-1][y] == 0 and comparesquares(x,y,x-1,y):
			print(comparesquares(x,y,x-1,y))
			stack.append((x-1,y))
			explodeboard[x-1][y] = explodeboard[x][y] + 1
						
		if isinbounds(x,y+1) and explodeboard[x][y+1] == 0 and comparesquares(x,y,x,y+1):
			stack.append((x,y+1))
			explodeboard[x][y+1] = explodeboard[x][y] + 1
						
		if isinbounds(x,y-1) and explodeboard[x][y-1] == 0 and comparesquares(x,y,x,y-1):
			stack.append((x,y-1))
			explodeboard[x][y-1] = explodeboard[x][y] + 1
		draw_game()
	return explodeboard

def catalystclearblocks(explodelist):
	score = 0
	pointspersquare = BASE_POINTS
	for x in range(0,len(Board)):
		for y in range(0,len(Board[x])):
			if explodelist[x][y] != 0:
				Board[x][y] = 0
				score += pointspersquare
				pointspersquare += POINTS_INCREASE
	return score
				


def cascade_board(hard_cascade = False):
	gravityflag = False
	cascadeflag = False
	for x in range(0,len(Board)):
		#First check if anything is wrong in the column
		gravityflag = False
		cascadeflag = False
		for y in range(0,len(Board[x])):
			if gravityflag and Board[x][y] != 0:
				cascadeflag = True
			elif Board[x][y] == 0:
				gravityflag = True
		
		#if something is wrong with the column, it will go through each block until it finds empty space, then if it finds blocks above that it will pull them to the first black space it will continue progressively.
		gravityflag = False
		if cascadeflag:
			lastsafe = 0
			for y in range(0,len(Board[x])):
				if Board[x][y] == 0:
					lastsafe = y
					break
			if hard_cascade:
				for y in range(lastsafe,len(Board[x])):
					if Board[x][y] != 0:
						Board[x][lastsafe] = Board[x][y]
						Board[x][y] = 0
						lastsafe += 1
			else:
				for y in range(lastsafe,len(Board[x])):
					if Board[x][y] != 0:
						Board[x][y-1] = Board[x][y]
						Board[x][y] = 0




def drawblock(blockID,x,y):
	
	if blockID >= 7:
		pygame.draw.rect(window,colorchange(ColorIndex[blockID],abs(clock%60-30)-15),
				pygame.Rect((	
					(leftscreen + (BLOCK_SIZE * x), bottomscreen - (BLOCK_SIZE * y)	),
					(BLOCK_SIZE,BLOCK_SIZE))))
	else:
		pygame.draw.rect(window,ColorIndex[blockID],
				pygame.Rect((	
					(leftscreen + (BLOCK_SIZE * x), bottomscreen - (BLOCK_SIZE * y)	),
					(BLOCK_SIZE,BLOCK_SIZE))))
	if blockID == 7 or blockID == 14:
		pygame.draw.rect(window,GOLD,
				pygame.Rect((	
					(leftscreen + (BLOCK_SIZE * x) + 5, bottomscreen - (BLOCK_SIZE * y) + 5	),
					(BLOCK_SIZE - 10,BLOCK_SIZE - 10))))
	if blockID > 7:
		pygame.draw.circle(window,ColorIndex[blockID-7], (leftscreen + (BLOCK_SIZE * x) + BLOCK_SIZE // 2, bottomscreen - (BLOCK_SIZE * y) + BLOCK_SIZE // 2 ), BLOCK_SIZE // 2 - 5)
	

"""def level_up() -> None:
	#This function should increase the difficulty to the next
"""

def create_block(type="random",colors="random"):
		random.shuffle(colorsets)
		piecechoice = random.choice(PieceWeights)
		if piecechoice == "catalyst":
			piecechoice = random.choice(PieceWeights)
			newblock = Block(PieceDict[piecechoice]) + 7
		else:
			newblock = Block(PieceDict[piecechoice])
			
		
		
		match random.randint(1,4):
			case 1:
				return newblock
			case 2:
				return rotate_block(newblock)
			case 3:
				return rotate_block(rotate_block(newblock))
			case 4:
				return rotate_block(newblock,clockwise=True)
				
'''
def create_block(type="random",colors="random"):
	colorsets = [1,2,3,4,5,6] * 2 + [7]
	random.shuffle(colorsets)
	piecechoice = random.choice(PieceWeights)
	if piecechoice == "catalyst":
		piecechoice = random.choice(PieceWeights)
		randomblock = PieceDict[piecechoice]
		newblock = [[colorsets[randomblock[0][0]]+7,colorsets[randomblock[0][1]]+7],
				[colorsets[randomblock[1][0]]+7,colorsets[randomblock[1][1]]+7]]
	else:
		randomblock = PieceDict[piecechoice]
		newblock = [[colorsets[randomblock[0][0]],colorsets[randomblock[0][1]]],
				[colorsets[randomblock[1][0]],colorsets[randomblock[1][1]]]]
	#print(newblock)
	match random.randint(1,4):
		case 1:
			return newblock
		case 2:
			return rotate_block(newblock)
		case 3:
			return rotate_block(rotate_block(newblock))
		case 4:
			return rotate_block(newblock,clockwise=True)
'''
#def queue_block(type="random",colors="random"):
	

def init_block_place():
	global blockPositionX, blockPositionY, blockPositionYExact
	blockPositionX = BOARD_SIZE_X // 2 - 1
	blockPositionY = BOARD_SIZE_Y + 2 - 1
	blockPositionYExact = 0.0
	extrablocks.append(create_block())
	if len(extrablocks) > 3:
		extrablocks.pop(0)

def place_block():
	for x in range(0,2):
		for y in range(0,2):
			Board[blockPositionX + x][blockPositionY + y - 1] = extrablocks[0][x][y]
	init_block_place()
	

def rotate_block(block, clockwise = True):
	if clockwise:
		newblock = [[block[1][0],block[0][0]],[block[1][1],block[0][1]]]
	else:
		newblock = [[block[0][1],block[1][1]],[block[0][0],block[1][0]]]
	return newblock
	
'''
def rotate_block(block, clockwise = True):
	if clockwise:
		newblock = [[block[1][0],block[0][0]],[block[1][1],block[0][1]]]
	else:
		newblock = [[block[0][1],block[1][1]],[block[0][0],block[1][0]]]
	return newblock
'''

def game_processing() -> None:
	"""
	This function does most of the game's calculations.
	These have to do with the ball's movement, momentum, and collision.
	"""
	global extrablocks, keydown, blockPositionX, blockPositionY, clock, explodeboard
	keys = pygame.key.get_pressed()
	if keys[K_ESCAPE]:
		game_state = False
	
	if clock % 3 == 0:
		cascade_board()
	
	if keys[K_e]:
		cascade_board(hard_cascade=True)
		
		
	if not keydown:
		if keys[K_q]:
			init_board()
		if keys[K_p]:
			explodeboard = findclears()
			catalystclearblocks(explodeboard)
		if keys[K_w]:
			extrablocks.insert(0,create_block())
			if len(extrablocks) > 3:
				extrablocks.pop(-1)
		
		
		if keys[K_z]:
			extrablocks[0] = rotate_block(extrablocks[0])
		if keys[K_x]:
			extrablocks[0] = rotate_block(extrablocks[0],clockwise=False)
			
		outofbounds = False
		if blockPositionY < 1 or blockPositionY > 17 or blockPositionX < 0 or blockPositionX >= board_size_x - 1:
			outofbounds = True
		#Necessary to prevent out of bounds crashing
		if keys[K_RIGHT] and blockPositionX < BOARD_SIZE_X - 2:
			if outofbounds or Board[blockPositionX + 2][blockPositionY] == 0 and Board[blockPositionX + 2][blockPositionY - 1] == 0:
				blockPositionX += 1
		if keys[K_LEFT] and blockPositionX > 0:
			if outofbounds or Board[blockPositionX - 1][blockPositionY] == 0 and Board[blockPositionX - 1][blockPositionY - 1] == 0:
				blockPositionX -= 1
		if keys[K_UP]:
			place_block()
		if keys[K_DOWN]:
			if outofbounds or Board[blockPositionX][blockPositionY - 2] == 0 and Board[blockPositionX + 1][blockPositionY - 2] == 0:
				blockPositionY -= 1
			else:
				place_block()
	
	clock += 1
	
	
	if keys[K_UP] or keys[K_DOWN] or keys[K_RIGHT] or keys[K_LEFT] or keys[K_z] or keys[K_x] or keys[K_c]:
		keydown += 1
		if keydown >= 10:
			keydown = 0
	else:
		keydown = 0
	
	
	
	# draw the game
	draw_game()

def draw_game() -> None:
	"""This function draws the game."""
	global centerx, centery, screen_height, screen_width, explodeboard
	
	
	window.fill(BLACK)
	
	
	
	#Draw the board
	for x in range(0,board_size_x):
		for y in range(0,(board_size_y - 4) ):
			drawblock(Board[x][y],x,y+1)
	
		#explodeboard
	for x in range(0,board_size_x):
		for y in range(0,(board_size_y - 4) ):
			if explodeboard[x][y] != 0:
				drawblock((explodeboard[x][y] if explodeboard[x][y] < 10 else 10),x,y)
	
	#Draw Up Next
	for z in range(1,len(extrablocks)):
		for x in range(0,2):
			for y in range(0,2):
				drawblock(extrablocks[z][x][y],x - 3, 18 + y - (3 * z) )
	
	#Draw the active block
	for x in range(0,2):
		for y in range(0,2):
			drawblock(extrablocks[0][x][y],	(x + blockPositionX),	(y + blockPositionY))
	
	#Lines
	for x in range(0,board_size_x + 1 ):
		pygame.draw.line(window,WHITE,
			((leftscreen + (BLOCK_SIZE * x)),topscreen),
			((leftscreen + (BLOCK_SIZE * x)),bottomscreen))
	for y in range(0,board_size_y -3):
		pygame.draw.line(window,WHITE,
			(leftscreen,(bottomscreen - (BLOCK_SIZE * y))),
			(rightscreen,(bottomscreen - (BLOCK_SIZE * y))))
			
	



def menu_processing() -> None:
	"""This function controls the menu."""
	global keys, keydown, game_state, cursor_pos
	global optionsmenu, startlevel
	
	draw_menu()
	keys = pygame.key.get_pressed()

	# move cursor
	if (keys[K_UP]) and not keydown:
		cursor_pos -= 1
		if cursor_pos < 0:
			cursor_pos = 0
	if (keys[K_DOWN]) and not keydown:
		cursor_pos += 1
		if cursor_pos > len(buttonlist) - 1:
			cursor_pos = len(buttonlist) - 1

	# change settings
	if (keys[K_z]) and not keydown:
		match buttonlist[cursor_pos]:
			case "startgame":
				game_state = not game_state
			case "optionsmenu":
				optionsmenu = not optionsmenu
	
	

	if keys[K_UP] or keys[K_DOWN] or keys[K_RIGHT] or keys[K_LEFT] or keys[K_z] or keys[K_x] or keys[K_c]:
		keydown += 1
		if keydown > 10:
			keydown = 0
	else:
		keydown = 0


def menutext(itemtext, buttonmask = "null", txtcolorpressed = YELLOW, txtcolornormal = WHITE, source=(0,50), font=DefaultFont):
	global window, buttonlist, menuitemoffset
	buttonlist.append(buttonmask)
	window.blit(DefaultFont.render(itemtext, True, txtcolorpressed if cursor_pos == menuitemoffset else txtcolornormal),(source[0], source[1] + menuitemoffset * FONTSIZE))
	menuitemoffset += 1
	
def normaltext(itemtext, txtcolor= WHITE, source = (0,0), font = DefaultFont):
	global window, buttonlist, textoffset
	window.blit(DefaultFont.render(itemtext, True, txtcolor),(source[0], source[1] + menuitemoffset * FONTSIZE))
	textoffset += 1

def draw_menu():
	global buttonlist, menuitemoffset, window
	
	window.fill(BLACK)
	
	buttonlist = []
	menuitemoffset = 0
	textoffset = 0
	
	normaltext("Action Puzzle Game Thing", WHITE, (0,0))
	#window.blit(DefaultFont.render("Action Puzzle Game Thing", True, WHITE),(0, 0))
	menutext("Play game","startgame")
	menutext("Game Options","optionsmenu")
	if optionsmenu:
		menutext(f"Starting Level: {startlevel}","startlevel")
		
	
	menutext("","5")
	
	


init_board()

# game loop
while running:

	if game_state:
		game_processing()
	else:
		menu_processing()
		
		
	for event in pygame.event.get():
		if event.type == QUIT:
			running = False
			
		if event.type == VIDEORESIZE:
			window = pygame.display.set_mode((event.w,event.h),RESIZABLE)
			screen_height = event.h
			screen_width = event.w
			centerx = screen_width // 2
			centery = screen_height // 2
			
			board_size_x = BOARD_SIZE_X
			board_size_y = BOARD_SIZE_Y + 4


			boardwidth = (BLOCK_SIZE * board_size_x)
			boardheight = (BLOCK_SIZE * ( board_size_y - 4) )

			leftscreen = centerx - boardwidth // 2
			rightscreen = centerx + boardwidth // 2
			topscreen = centery - boardheight // 2
			bottomscreen = centery + boardheight // 2

	pygame.display.update()
	fps.tick(60)

pygame.quit()
sys.exit()