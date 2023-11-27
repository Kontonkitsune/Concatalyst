"""
fuck this shit

Code by: Lucina Riley / Kontonkitsune
Last Updated: 15/7/2023

Action Puzzle thing


"""

import random
import pygame, sys
import math
from pygame.locals import *

pygame.init()
fps = pygame.time.Clock()

"""--------------Class Structures--------------"""

class Config:
	"""A simple class to allow a variable to have a set minimum, maximum, and scale."""
	def __init__(self, value = 0, max = 10, min = 0, scale = 1):
		self.value = value
		self.max = max
		self.min = min
		self.scale = scale
	def increment(self):
		self.value += self.scale
		if self.value > self.max:
			self.value = self.max
	def decrement(self):
		self.value -= self.scale
		if self.value < self.min:
			self.value = self.min

class Block:
	"""
	A class containing four cells arranged in a square.
	
	The literal building block of the game.
	"""
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
				return self.tl
			case 1:
				return self.tr
			case 2:
				return self.bl
			case 3:
				return self.br
			case (0,0):
				return self.tl
			case (0,1):
				return self.tr
			case (1,0):
				return self.bl
			case (1,1):
				return self.br

class Boardt: # 2-d array
	def __init__(self, width, height):
		self.cells = [[0 for x in range(board_size_y)] for y in range(board_size_x)]
		self.width = width
		self.height = height
	def __getitem__(self,index):
		x,y = index
		return self.cells[x,y]

"""--------------Global Constants-------------"""

# Defaults
WIDTH = 800
HEIGHT = 800
BOARD_SIZE_X = 10
BOARD_SIZE_Y = 16
BLOCK_SIZE = 30
FONTSIZE = 30

# Game Defaults
BASE_POINTS = 100
POINTS_INCREASE = 2

MAX_QUEUE_LENGTH = 5 # How many blocks "next up" shows.

# Global Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 63, 63)
REDCAT = (127, 0, 0)
YELLOW = (240, 240, 0)
YELLOWCAT = (255, 192, 63)
GREEN = (63, 255, 63)
GREENCAT = (0, 127, 32)
PINK = (255, 127, 255)
PINKCAT = (192, 64, 192)
BLUE = (0, 0, 255)
BLUECAT = (63, 63, 192)
CYAN = (0, 255, 255)
CYANCAT = (63, 192, 255)

SILVER = (232, 245, 255)
GOLD = (220, 188, 12)
GOLDCAT = (212, 212, 255)
ROSEGOLD = (248,185,150)

ColorIndex = (BLACK, 
	PINK,	BLUE,	GREEN,	YELLOW,	RED,	CYAN,		SILVER, 
	PINKCAT,BLUECAT,GREENCAT,YELLOWCAT,REDCAT,CYANCAT,	ROSEGOLD)

# Fonts
DefaultFont = pygame.font.SysFont("Comic Sans MS", FONTSIZE)
SmallerFont = pygame.font.SysFont("Comic Sans MS", 20)

"""--------------Global Variables-------------"""

# General Game State Variables
game_state = False # True while a game is active.
running = True # True while the game is supposed to be open.
keydown = 0 # Timer for how long a useful key has been pressed. Used to make sure single presses can happen.

# Visual and alignment
screen_width = WIDTH
screen_height = HEIGHT
centerx = screen_width // 2
centery = screen_height // 2

board_size_x = BOARD_SIZE_X
board_size_y = BOARD_SIZE_Y + 4
block_size = BLOCK_SIZE

boardwidth = (block_size * board_size_x)
boardheight = (block_size * ( board_size_y - 4) )

leftscreen = centerx - boardwidth // 2
rightscreen = centerx + boardwidth // 2
topscreen = centery - boardheight // 2
bottomscreen = centery + boardheight // 2

backgroundImage = pygame.image.load("BackgroundImage.jpg")

#Menu and Text Variables
optionsmenu = False
buttonlist = []
menuitemoffset = 0
textoffset = 0
cursor_pos = 0

# Game Instance Variables
Board = [] # The game board. It's a bit bigger than it looks.
ExplodeBoard = [] # The board used for tracking which blocks are supposed to explode. Also acts as a handy graphics thing.

score = 0
squarescleared = 0
longestchain = 0
previousscores = []

# Game Progression / Difficulty Variables
level = 1
gravity = 10 # How fast the block falls
grace_period = 100 # How long before block starts falling?

# Physics
block_pos_x = board_size_x // 2 - 1
block_pos_y = board_size_y - 3
block_fall_progress = 0.0 #to deal with the slower fall speeds

# Timers and Counters
clock = 0 # General ingame timer, used for a lot of stuff.
grace = 100 
bombtimer = -2
timesinceexplode = 0
blockssincelastcatalyst = 0
bombssincelastexplosion = 0

# Weighted Lists
ColorSets = [1,2,3,4,5] * 3 + [7] * 2
PieceWeights = (["full","quarter","half"] * 4 + ["checker","triple"] * 2 + ["triplechecker","quad"])
PieceDict = {
	"full": (1,1,1,1),
	"quarter": (1,1,1,2),
	"half": (1,1,2,2),
	"checker": (1,2,2,1),
	"triple": (1,1,2,3),
	"triplechecker": (1,2,3,1),
	"quad": (1,2,3,4)}

"""--------------Configuration / Settings----------------"""

# Visual
boardHeight = Config(BOARD_SIZE_Y,24,8,1) # Height of the board
boardWidth = Config(BOARD_SIZE_X,24,4,1) # Width of the board
blockSize = Config(BLOCK_SIZE,100,10,5) # Block size 

# Gameplay
startLevel = Config(1,100,1,1) # Starting level
catalystChance = Config(-5,100,-50,5) # Base chance for any block to be a catalyst
gracePeriod = Config(100,1000,0,10) # How long a block can idle at the starting position before beginning to fall.
bombTimer = Config(400,10000,0,100) # How long it takes bombs to go off
catalystGuarantee = Config(5,10,0,1) # How 
maxBlocksPerCatalyst = Config(10,100,1,1) # How many blocks before a catalyst should be guaranteed (REDUNDANT)

extrablocks = [Block(0,0,0,0),Block(0,0,0,0),Block(0,0,0,0)]


# window declaration
window = pygame.display.set_mode((WIDTH, HEIGHT),RESIZABLE)
pygame.display.set_caption('Action Puzzler Thing')

def colorchange(color:tuple, phase:int) -> tuple: # Takes a color and an int and adds that int to the color
	return tuple([((x + phase if x + phase >= 0 else 0) if x + phase < 255 else 255) for x in color])

def reinitialize() -> None: # Initializes variables to config values
	"""Basically just makes sure variables are set to what they need to be (for config settings and such)"""
	global board_size_x, board_size_y, block_size, boardwidth, boardheight, leftscreen, rightscreen, topscreen, bottomscreen, grace_period
	board_size_x = boardWidth.value
	board_size_y = boardHeight.value + 4
	grace_period = gracePeriod.value
	block_size = blockSize.value
	level = startLevel.value
	
	boardwidth = (block_size * board_size_x)
	boardheight = (block_size * ( board_size_y - 4) )

	leftscreen = centerx - boardwidth // 2 if game_state else centerx
	rightscreen = centerx + boardwidth // 2 if game_state else centerx + boardwidth
	topscreen = centery - boardheight // 2
	bottomscreen = centery + boardheight // 2

def init_board() -> None: # Initializes the board
	"""This function initializes the game."""
	reinitialize()
	global Board, ExplodeBoard
	for x in range(0,MAX_QUEUE_LENGTH):
		create_block()
	
	
	if game_state:
		Board = [[0 for x in range(board_size_y)] for y in range(board_size_x)]
	else:
		Board = [[(random.choice(ColorSets) + 7 if random.randint(1,100) <= catalystChance.value + catalystGuarantee.value * 5 else random.choice(ColorSets)) for x in range(board_size_y)] for y in range(board_size_x)]
	ExplodeBoard = [[0 for x in range(board_size_y)] for y in range(board_size_x)]
	

def isinbounds(x: int, y: int) -> bool: # Checks if the given coordinates are within bounds
	if x < 0 or x >= len(Board) or y < 0 or y >= len(Board[0]):
		return False
	else:
		return True
		
def comparesquares(x: int, y: int, x2: int, y2: int): # Checks if two squares are considered "connected" and can be cleared together
	if isinbounds(x,y) and isinbounds(x2,y2):
		if Board[x][y] == 0 or Board[x2][y2] == 0:
			return False
		elif Board[x][y] % 7 == Board[x2][y2] or Board[x][y] % 7 == 0 or Board[x2][y2] % 7 == 0:
			return True
		else:
			return False
	else:
		return False

def findclears() -> list: # Searches through the board and figures out which blocks are connected to catalysts.
	"""
	Searches through the board and returns a board of all cells connected to catalysts.
	
	
	"""
	global ExplodeBoard
	ExplodeBoard = [[0 for x in range(board_size_y)] for y in range(board_size_x)]
	stack = []
	
	for x in range(0,len(Board)):
		for y in range(0,len(Board[x])):
			if Board[x][y] > 7 and Board[x][y] < 15 and ExplodeBoard[x][y] == 0:
				ExplodeBoard[x][y] += 1
				stack.append((x,y))
	while len(stack) > 0:
		x = stack[0][0]
		y = stack[0][1]
		stack.pop(0)
		for p in ((x+1,y),(x-1,y),(x,y+1),(x,y-1)):
			if isinbounds(p[0],p[1]) and Board[p[0]][p[1]] < 8 and (ExplodeBoard[p[0]][p[1]] == 0 or ExplodeBoard[p[0]][p[1]] > ExplodeBoard[x][y] + 1) and comparesquares(x,y,p[0],p[1]):
				stack.append((p[0],p[1]))
				ExplodeBoard[p[0]][p[1]] = ExplodeBoard[x][y] + 1
	return ExplodeBoard

def catalystclearblocks(explodelist: list) -> tuple:
	global timesinceexplode
	timesinceexplode = 0
	score = 0
	squares = 0
	highestchain = 0
	pointspersquare = BASE_POINTS
	for x in range(0,len(Board)):
		for y in range(0,len(Board[x])):
			if explodelist[x][y] != 0:
				Board[x][y] = 0
				squares += 1
				if explodelist[x][y] > highestchain:
					highestchain = explodelist[x][y]
				score += pointspersquare
				pointspersquare += POINTS_INCREASE
				pointspersquare += explodelist[x][y]
	return score, squares, highestchain
				
def cascade_board(hard_cascade = False) -> None:
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

def drawblock(blockID: int,x: int,y: int,usecolorinstead=False) -> None:
	
	if usecolorinstead:
		pygame.draw.rect(window,blockID,
			pygame.Rect((	
				(leftscreen + (block_size * x), bottomscreen - (block_size * y)	),
				(block_size,block_size))))
	else:
		if blockID >= 7:
			pygame.draw.rect(window,colorchange(ColorIndex[blockID],abs(clock%60-30)-15),
					pygame.Rect((	
						(leftscreen + (block_size * x), bottomscreen - (block_size * y)	),
						(block_size,block_size))))
		else:
			pygame.draw.rect(window,ColorIndex[blockID],
					pygame.Rect((	
						(leftscreen + (block_size * x), bottomscreen - (block_size * y)	),
						(block_size,block_size))))
		if blockID == 7 or blockID == 14:
			pygame.draw.rect(window,GOLD,
					pygame.Rect((	
						(leftscreen + (block_size * x) + 5, bottomscreen - (block_size * y) + 5	),
						(block_size - 10,block_size - 10))))
		if blockID > 7:
			pygame.draw.circle(window,ColorIndex[blockID-7], (leftscreen + (block_size * x) + block_size // 2, bottomscreen - (block_size * y) + block_size // 2 ), block_size // 2 - 5)
	
def level_up() -> None:
	global grace, gravity, level
	grace -= 1
	gravity += 1
	level += 1

def create_block(type="random",colors=0,catalyst=False) -> Block:
		global blockssincelastcatalyst
		if colors == 0:
			random.shuffle(ColorSets)
		piecechoice = random.choice(PieceWeights) if type == "random" else type
		
		newblock = Block(ColorSets[PieceDict[piecechoice][0]],ColorSets[PieceDict[piecechoice][1]],ColorSets[PieceDict[piecechoice][2]],ColorSets[PieceDict[piecechoice][3]])
		randomnumber = random.randint(1,100)
		
		
		if randomnumber <= catalystChance.value + blockssincelastcatalyst * catalystGuarantee.value:
			catalyst = True
		if catalyst:
			newblock += 7
			blockssincelastcatalyst = 0
		else:
			blockssincelastcatalyst += 1
			
		
		match random.randint(1,4):
			case 1:
				return newblock
			case 2:
				return rotate_block(newblock)
			case 3:
				return rotate_block(rotate_block(newblock))
			case 4:
				return rotate_block(newblock,clockwise=True)
				
#def queue_block(type="random",colors="random"):
	
def reset_block() -> None:
	global block_pos_x, block_pos_y, block_fall_progress
	block_pos_x = board_size_x // 2 - 1
	block_pos_y = board_size_y - 3
	block_fall_progress = 0.0
	extrablocks.append(create_block())
	if len(extrablocks) > MAX_QUEUE_LENGTH:
		extrablocks.pop(0)

def place_block() -> None: 
	global grace, bombtimer, bombssincelastexplosion
	
	grace = grace_period
	if extrablocks[0][0,0] > 7:
		if bombssincelastexplosion == 0:
			bombtimer = bombTimer.value
		else:
			bombtimer += bombTimer.value // (bombssincelastexplosion + 1)
			if bombtimer > bombTimer.value:
				bombtimer = bombTimer.value
		bombssincelastexplosion += 1
		
	for x in range(0,2):
		for y in range(0,2):
			Board[block_pos_x + x][block_pos_y + y - 1] = extrablocks[0][x,y]
	reset_block()
	
def rotate_block(block: Block, clockwise = True) -> Block: # 
	"""Takes a Block and rotates it clockwise or counterclockwise, then returns the Block."""
	if clockwise:
		return Block(block[1,0],block[0,0],block[1,1],block[0,1])
	else:
		return Block(block[0,1],block[1,1],block[0,0],block[1,0])

def explodethings() -> None: # This function is kind of unnecessary and should probably be moved to be part of findclears()
	global score, longestchain, squarescleared, bombssincelastexplosion
	ExplodeBoard = findclears()
	previousscores.insert(0,catalystclearblocks(ExplodeBoard))
	
	bombssincelastexplosion = 0
	
	score += previousscores[0][0]
	squarescleared += previousscores[0][1]
	if longestchain < previousscores[0][2]:
		longestchain = previousscores[0][0]
	if len(previousscores) > 5:
		previousscores.pop(-1)

def game_processing() -> None: # Ingame event handling
	"""This function does most of the game's event handling."""
	global extrablocks, keydown, block_pos_x, block_pos_y, block_fall_progress, clock, ExplodeBoard, score, prevscore, timesinceexplode, game_state, grace, bombtimer
	keys = pygame.key.get_pressed()
	if keys[K_ESCAPE]:
		game_state = False
	
	if squarescleared > 10 * level:
		level_up()
	
	if clock % 3 == 0:
		cascade_board()
	
	if keys[K_e]:
		cascade_board(hard_cascade=True)
		
	if bombtimer == 0:
		explodethings()
	bombtimer -= 1
	
	if grace <= 0:
		block_fall_progress += gravity
		if block_fall_progress > 1000:
			if block_pos_y < 1 or block_pos_y > 17 or block_pos_x < 0 or block_pos_x >= board_size_x - 1 or Board[block_pos_x][block_pos_y - 2] == 0 and Board[block_pos_x + 1][block_pos_y - 2] == 0 and block_pos_y >= 2:
				block_pos_y -= 1
			else:
				place_block()
			block_fall_progress = 0
	else:
		grace -= 1
	
	if not keydown:
		if keys[K_p]:
			bombtimer=0
		if keys[K_w]:
			reset_block()
		
		
		if keys[K_z]:
			extrablocks[0] = rotate_block(extrablocks[0])
		if keys[K_x]:
			extrablocks[0] = rotate_block(extrablocks[0],clockwise=False)
			
		outofbounds = False
		if block_pos_y < 1 or block_pos_y > 17 or block_pos_x < 0 or block_pos_x >= board_size_x - 1:
			outofbounds = True
		#Necessary to prevent out of bounds crashing
		if keys[K_RIGHT] and block_pos_x < board_size_x - 2:
			if outofbounds or Board[block_pos_x + 2][block_pos_y] == 0 and Board[block_pos_x + 2][block_pos_y - 1] == 0:
				block_pos_x += 1
		if keys[K_LEFT] and block_pos_x > 0:
			if outofbounds or Board[block_pos_x - 1][block_pos_y] == 0 and Board[block_pos_x - 1][block_pos_y - 1] == 0:
				block_pos_x -= 1
		if keys[K_UP]:
			place_block()
		if keys[K_DOWN]:
			if outofbounds or Board[block_pos_x][block_pos_y - 2] == 0 and Board[block_pos_x + 1][block_pos_y - 2] == 0 and block_pos_y >= 2:
				block_pos_y -= 1
				block_fall_progress = 0
			else:
				place_block()
	
	clock += 1
	timesinceexplode += 1
	
	
	if keys[K_UP] or keys[K_DOWN] or keys[K_RIGHT] or keys[K_LEFT] or keys[K_z] or keys[K_x] or keys[K_c] or keys[K_p]:
		keydown += 1
		if keydown >= 10:
			keydown = 0
	else:
		keydown = 0
	
	
	
	# draw the game
	draw_game()

def draw_game(explosion=False,fakeboard=False) -> None:
	"""This function draws the game."""
	global centerx, centery, screen_height, screen_width, ExplodeBoard, textoffset
	
	window.fill(BLACK)
	window.blit(backgroundImage,(0,0))
	
	#Draw the board
	for x in range(0,board_size_x):
		for y in range(0,(board_size_y - 4) ):
			if Board[x][y] == 0:
				if ExplodeBoard[x][y] != 0:
					
					extcolor = 0 if 255-(8 * ExplodeBoard[x][y]) < 0 else 255-(8 * ExplodeBoard[x][y])
					
					excolor = colorchange((255,extcolor,extcolor),8 * ExplodeBoard[x][y] - (0 if explosion else 8 * timesinceexplode))
					
					if excolor != (0,0,0):
						drawblock(excolor,x,y+1,True)
			else:
				drawblock(Board[x][y],x,y+1)
	
	if not fakeboard:
		#Draw Up Next
		if len(extrablocks) > 1:
			for z in range(1,len(extrablocks)):
				for x in range(0,2):
					for y in range(0,2):
						drawblock(extrablocks[z][x,y],x - 3, 18 + y - (3 * z) )
		
		#Draw the active block
		for x in range(0,2):
			for y in range(0,2):
				drawblock(extrablocks[0][x,y],	(x + block_pos_x),	(y + block_pos_y))
	
	#Lines
	for x in range(0,board_size_x + 1 ):
		pygame.draw.line(window,WHITE,
			((leftscreen + (block_size * x)),topscreen),
			((leftscreen + (block_size * x)),bottomscreen))
	for y in range(0,board_size_y -3):
		pygame.draw.line(window,WHITE,
			(leftscreen,(bottomscreen - (block_size * y))),
			(rightscreen,(bottomscreen - (block_size * y))))
			
	if bombtimer > 0:
		bombline = (board_size_y - 4) * block_size * bombtimer // bombTimer.value
		for x in range(0,board_size_x + 1 ):
			pygame.draw.line(window,RED,((leftscreen + (block_size * x)),bottomscreen),((leftscreen + (block_size * x)),bottomscreen - bombline), 3)
		for y in range(0,board_size_y -3):
			if bottomscreen - bombline < bottomscreen - (block_size * y):
				pygame.draw.line(window,RED,
					(leftscreen,(bottomscreen - (block_size * y))),
					(rightscreen,(bottomscreen - (block_size * y))),3)
	
		
	if not fakeboard:
		source = (rightscreen, topscreen)
		textoffset = 0
		if bombtimer > 0:
			normaltext(f"{bombtimer}",YELLOW,(leftscreen,bottomscreen))
		textoffset = 0
		normaltext(f"Level: {level}",WHITE,source)
		normaltext(f"Score: {score}",WHITE,source)
		normaltext(f"Cleared: {squarescleared}",WHITE,source)
		
		for txt in previousscores:
			normaltext(f"+{txt[0]}! {txt[1]} squares",YELLOW,source,SmallerFont)
		
def menu_fake_game_board() -> None:
	"""This function draws the game."""
	
	global clock, bombtimer, timesinceexplode
	clock += 1
	if clock % 3 == 0:
		cascade_board()
	if bombtimer == 0:
		explodethings()
	bombtimer -= 1
	if bombtimer == -300:
		init_board()
		bombtimer = bombTimer.value
	timesinceexplode += 1
	
	draw_game(fakeboard=True)
			
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
				init_board()
			case "optionsmenu":
				optionsmenu = not optionsmenu
	
	if isinstance(buttonlist[cursor_pos],Config) and not keydown:
		if keys[K_RIGHT]: 
			buttonlist[cursor_pos].increment()
		if keys[K_LEFT]:
			buttonlist[cursor_pos].decrement()
		
	if keys[K_UP] or keys[K_DOWN] or keys[K_RIGHT] or keys[K_LEFT] or keys[K_z] or keys[K_x] or keys[K_c]:
		keydown += 1
		if keydown > 10:
			keydown = 0
	else:
		keydown = 0

def menutext(itemtext, buttonmask = "null", txtcolorpressed = YELLOW, txtcolornormal = WHITE, source=(0,50), offset=True, font=DefaultFont) -> None: # Draws interactable text.
	"""
	Draws interactable text. Used consecutevely, it can create multiple lines.
	
	:itemtext: string. Text (Required)
	:buttonmask: string or Config. Used to easily change config. (Default: "null")
	:txtcolorpressed: tuple[3]. RGB values for text color when highlighted. (Default: (255,255,0))
	:txtcolornormal: tuple[3]. RGB values for text color when not highlighted. (Default: (255,255,255))
	:source: tuple(2). Coordinates for top left corner of text. (Default: (0,50))
	:offset: bool. Whether or not to increment offset. (Default: True)
	:font: pygame.font. (Default: DefaultFont)
	"""
	global window, buttonlist, menuitemoffset
	buttonlist.append(buttonmask)
	window.blit(DefaultFont.render(itemtext, True, txtcolorpressed if cursor_pos == menuitemoffset else txtcolornormal),(source[0], source[1] + menuitemoffset * FONTSIZE))
	if offset:
		menuitemoffset += 1
	
def normaltext(itemtext: str, txtcolor= WHITE, source = (0,0), offset = True, font = DefaultFont) -> None: # Draws non-interactable text consecutively.
	"""
	Draws non-interactable text. Used consecutevely, it can create multiple lines.
	
	:itemtext: string. Text (Required)
	:txtcolor: tuple[3]. RGB values for text color. (Default: (255,255,255))
	:source: tuple(2). Coordinates for top left corner of text. (Default: (0,0))
	:offset: bool. Whether or not to increment offset. (Default: True)
	:font: pygame.font. (Default: DefaultFont)
	"""
	
	global window, buttonlist, textoffset
	window.blit(font.render(itemtext, True, txtcolor),(source[0], source[1] + textoffset * FONTSIZE))
	if offset:
		textoffset += 1

def draw_menu() -> None: # Draws the menu
	global buttonlist, menuitemoffset, window, textoffset
	
	window.fill(BLACK)
	
	menu_fake_game_board()
	
	buttonlist = []
	menuitemoffset = 0
	textoffset = 0
	
	normaltext("Action Puzzle Game Thing", WHITE, (0,0), False)
	#window.blit(DefaultFont.render("Action Puzzle Game Thing", True, WHITE),(0, 0))
	menutext("Play game","startgame")
	menutext("Game Options","optionsmenu")
	if optionsmenu:
		menutext(f"Starting Level: {startLevel.value}",startLevel)
		menutext(f"Board Width: {boardWidth.value}",boardWidth)
		menutext(f"Board Height: {boardHeight.value}",boardHeight)
		menutext(f"Catalyst Chance (%): {catalystChance.value}",catalystChance)
		menutext(f"Block Size: {blockSize.value}",blockSize)
		menutext(f"Grace Period: {gracePeriod.value}",gracePeriod)
		menutext(f"Bomb Timer: {bombTimer.value}",bombTimer)
		
	
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

			boardwidth = (block_size * board_size_x)
			boardheight = (block_size * ( board_size_y - 4) )

			leftscreen = centerx - boardwidth // 2
			rightscreen = centerx + boardwidth // 2
			topscreen = centery - boardheight // 2
			bottomscreen = centery + boardheight // 2

	pygame.display.update()
	fps.tick(60)

pygame.quit()
sys.exit()