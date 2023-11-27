"""
Concatalyst

Code by: Lucina Riley / Kontonkitsune
Last Updated: 19/7/2023

This is an action-puzzle game about making really long chains and then blowing them up.


To Do:

Pause Menu

Game over screen

High scores

Gamemode / Difficulty Presets

Tutorial

Color Schemes


"""

import random
import pygame, sys
import math
import time
from pygame.locals import *

pygame.init()
fps = pygame.time.Clock()

"""--------------Class Structures--------------"""

class Square:
	def __init__(self, color=0,special=0):
		self.color = color
		self.special = special
	def set(self,color = -1, special = -1):
		if special != -1:
			self.special = special
		if color != -1:
			self.color = color
	
	def copycell(self):
		return Square(self.color,self.special)
	
	def __add__(self,other):
		return Square(self.color + other,self.special)
		
	def __iadd__(self,other):
		self.color += other
		return self
	
	def __eq__(self,other):
		return (self.color == other)
		
	def __setitem__(self,index=0,value=0):
		match index:
			case 0: self.color = value
			case 1: self.special = value
	def __getitem__(self,index=0):
		match index:
			case 0: return self.color
			case 1: return self.special
	
	def __str__(self):
		return f"({str(self.color)}, {str(self.special)})"
	
class Config:
	"""A simple class to allow a variable to have a set minimum, maximum, and scale."""
	def __init__(self, value = 0, max = 0, min = 0, scale = 1, boolean = False):
		self.value = value
		self.max = max
		self.min = min
		self.scale = scale
		self.boolean = boolean
	def toggle(self):
		if self.value == 0:
			self.value = 1
		else:
			self.value = 0
	def increment(self):
		self.value += self.scale
		if self.value > self.max: self.value = self.max
	def decrement(self):
		self.value -= self.scale
		if self.value < self.min: self.value = self.min
	def set(self,value):
		self.value = value
		if self.value < self.min: self.value = self.min
		if self.value > self.max: self.value = self.max
	def __str__(self):
		if boolean:
			return "True" if self.value else "False"
		else:
			return f"{self.value}; Min: {self.min} Max: {self.max}"

class Block:
	"""
	A class containing four cells arranged in a square.
	
	The literal building block of the game.
	"""
	def __init__(self, tl, tr, bl, br):
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
	
	def setspecial(self,special):
		self.tl.set(special=special)
		self.tr.set(special=special)
		self.bl.set(special=special)
		self.br.set(special=special)
	
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
	
	def __str__(self):
		return f"{str(self.tl)},{str(self.tr)}\n{str(self.bl)},{str(self.br)}"
				
class Board: # 2-d array
	def __init__(self, width, height,filltype = 0):
		if filltype == 1:
			self.cells = [[Square() for y in range(height)] for x in range(width)]
		else:
			self.cells = [[0 for y in range(height)] for x in range(width)]
		self.width = width
		self.height = height
	def __getitem__(self,index):
		x,y = index
		return self.cells[x][y]
	def __setitem__(self,index,value):
		x,y = index
		self.cells[x][y] = value
	def __str__(self):
		string = ""
		for y in range(0,len(self.cells[0])):
			string += "("
			for x in range(0,len(self.cells)):
				string += str(self[x,len(self.cells[0])-y-1])
				if x != len(self.cells) - 1:
					string += ", "
			string += ")\n"
				
		return string

"""--------------Global Constants-------------"""

# Defaults
WIDTH = 1200
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

BLUE = (64, 96, 255)
BLUECAT = (63, 63, 192)

CYAN = (32, 225, 255)
CYANCAT = (63, 192, 255)

SILVER = (232, 245, 255)
GOLD = (220, 188, 12)

GOLDCAT = (212, 212, 255)
ROSEGOLD = (248,185,150)

ColorIndex = (
	BLACK,
	PINK,
	BLUE,
	GREEN,
	YELLOW,
	RED,
	CYAN,
	GOLD,
	PINKCAT,
	BLUECAT,
	GREENCAT,
	YELLOWCAT,
	REDCAT,
	CYANCAT,
	GOLDCAT
	
	)


# Fonts
DefaultFont = pygame.font.SysFont("Verdana", FONTSIZE)
SmallerFont = pygame.font.SysFont("Consolas", 20)

"""--------------Global Variables-------------"""

# General Game State Variables
game_state = "main_menu"
running = True # True while the game is supposed to be open.
keydown = 0 # Timer for how long a useful key has been pressed. Used to make sure single presses can happen.
selectedpreset = "normal"
tutorialsection = 0

# Visual and alignment
screen_width = WIDTH
screen_height = HEIGHT
centerx = screen_width // 2
centery = screen_height // 2

boardwidth = BLOCK_SIZE * BOARD_SIZE_X
boardheight = BLOCK_SIZE * BOARD_SIZE_Y

leftscreen = centerx - boardwidth // 2
rightscreen = centerx + boardwidth // 2
topscreen = centery - boardheight // 2
bottomscreen = centery + boardheight // 2


#Menu and Text Variables
buttonlist = []
menuitemoffset = 0
textoffset = 0
cursor_pos = 0

# Boards
GameBoard = Board(BOARD_SIZE_X,BOARD_SIZE_Y + 4,1) # The game board. It's a bit bigger than it looks.
ExplodeBoard = Board(BOARD_SIZE_X,BOARD_SIZE_Y + 4) # The board used for tracking which blocks are supposed to explode. Also acts as a handy graphics thing.
ConnectedBoard = Board(BOARD_SIZE_X,BOARD_SIZE_Y + 4)

ConcatalystTitleBoard = Board(43,5,1)
ConcatalystConnectedBoard = Board(43,5)

# Game Instance Variables
extrablocks = []

score = 0
squarescleared = 0
longestchain = 0
previousscores = []

# Game Progression / Difficulty Variables
level = 1
gravity = 10 # How fast the block falls
grace_period = 100 # How long before block starts falling?

# Physics
block_pos_x = GameBoard.width // 2 - 1
block_pos_y = GameBoard.height - 3
block_fall_progress = 0.0 #to deal with the slower fall speeds

# Timers and Counters
clock = 0 # General ingame timer, used for a lot of stuff.
grace = 100 
bombtimer = 400
timesinceexplode = 0
blockssincelastcatalyst = 0
bombssincelastexplosion = 0

# Weighted Lists
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

# Menu option toggles
optionsMenu = Config(0,boolean=True)
optionsMenuBoard = Config(0,boolean=True)
optionsMenuGameplay = Config(0,boolean=True)
optionsMenuVisuals = Config(0,boolean=True)
gamemodeMenu = Config(0,boolean=True)
presetsMenu = Config(0,boolean=True)
presetsMenuDifficulty = Config(0,boolean=True)
presetsMenuOther = Config(0,boolean=True)

# Visual
blockSize = Config(BLOCK_SIZE,100,10,5) # Block size 
titleBoardRefresh = Config(300,1500,50,50)
connectionType = Config(0,2,0,1)
pulseIntensity = Config(15,30,5,5)

# Board
boardHeight = Config(BOARD_SIZE_Y,24,8,1) # Height of the board
boardWidth = Config(BOARD_SIZE_X,24,4,1) # Width of the board
numberColors = Config(5,12,2,1)

# Gameplay
startLevel = Config(1,100,1,1) # Starting level
doLevelUp = Config(0,boolean=True)
squaresPerLevel = Config(20,100,1,1) # How many blocks before a catalyst should be guaranteed (REDUNDANT)

gracePeriod = Config(100,1000,0,10) # How long a block can idle at the starting position before beginning to fall.
rainbowChance = Config(10,100,1,1)
catalystChance = Config(-5,100,-50,5) # Base chance for any block to be a catalyst
catalystChanceIncrease = Config(5,10,0,1) # How 
catalystTimer = Config(400,10000,0,100) # How long it takes bombs to go off
maxBlocksPerCatalyst = Config(10,100,1,1) # How many blocks before a catalyst should be guaranteed (REDUNDANT)


# window declaration
window = pygame.display.set_mode((WIDTH, HEIGHT),RESIZABLE)
pygame.display.set_caption('Concatalyst')
backgroundImage = pygame.image.load("BackgroundImage.jpg").convert()
pygame.event.set_allowed([QUIT, KEYDOWN, KEYUP])



# Optimization Flags
updatescreennextframe = 2
needtocascade = False
screenupdaterects = []

# Custom Boards
literallythebestboard = (
	(12,12,1,-1,1,1,Square(1,1),12,12,-1),
	(-1,11,11,12,12,12,12,12,11,11),
	(10,10,11,11,11,12,11,11,11,10),
	(9,10,10,10,11,11,11,10,10,-1),
	(-1,9,9,10,10,10,10,10,9,9),
	(8,8,9,9,9,10,9,9,9,8),
	(7,8,8,8,9,9,9,8,8,-1),
	(-1,7,7,8,8,8,8,8,7,7),
	(6,6,7,7,7,8,7,7,7,6),
	(5,6,6,6,7,7,7,6,6,-1),
	(-1,5,5,6,6,6,6,6,5,5),
	(4,4,5,5,5,5,5,5,5,4),
	(3,4,4,4,4,4,4,4,4,-1),
	(-1,3,3,3,3,3,3,3,3,3),
	(2,2,2,2,2,2,2,2,2,2),
	(1,1,1,1,1,1,1,1,1,-1)
	)

concatalystboardlayout = (
	( 2, 2, 2, 0, 3, 3, 3,-1, 4, 4, 4, 0, 5, 5, 5, 0, 6, 6, 6,-1, 7, 7, 7, 0, 8, 8, 8, 0, 9, 0, 0, 0,10, 0,10, 0,11,11,11,-1,12,12,12),
	( 2, 0, 0, 0, 3, 0, 3, 0, 4, 0, 4, 0, 5, 0, 0, 0, 6, 0, 6, 0, 0, 7, 0, 0, 8, 0, 8, 0, 9, 0, 0, 0,10, 0,10, 0,11, 0, 0, 0, 0,12, 0),
	( 2, 0, 0, 0, 3, 0, 3, 0, 4, 0, 4, 0, 5, 0, 0, 0, 6, 6, 6, 0, 0, 7, 0, 0, 8, 8, 8, 0, 9, 0, 0, 0,10,10,10, 0,11,11,11, 0, 0,12, 0),
	( 2, 0, 0, 0, 3, 0, 3, 0, 4, 0, 4, 0, 5, 0, 0, 0, 6, 0, 6, 0, 0, 7, 0, 0, 8, 0, 8, 0, 9, 0, 0, 0, 0,10, 0, 0, 0, 0,11, 0, 0,12, 0),
	( 2, 2, 2,-1, 3, 3, 3, 0, 4, 0, 4,-1, 5, 5, 5,-1, 6, 0, 6, 0, 0, 7,-1,-1, 8, 0, 8,-1, 9, 9, 9,-1,-1,10,-1,-1,11,11,11, 0, 0,12, 0)
	)

tutorialboardpiececolors = (
	(),
	()
)

tutorialboards = (
	(
	((0) * 10) * 13,
	(2,3,3,0,0,3,0,0,2,2),
	(2,2,2,2,3,3,3,2,2,2),
	(2,2,3,3,3,3,2,2,2,3),
	),
	(
	((0) * 10) * 13,
	(2,3,3,0,0,3,0,0,2,2),
	(2,2,2,2,3,3,3,2,2,2),
	(2,2,3,3,3,3,2,2,2,3),
	),
	(
	((0) * 10) * 13,
	(2,3,3,0,0,3,0,0,2,2),
	(2,2,2,2,3,3,3,2,2,2),
	(2,2,3,3,3,3,2,2,2,3),
	),


)
"""--------------------Value Functions-------------------------"""


def normalize(value,max,min) -> int: # Ensures a value is between min and max
	"""Ensures a value is between min and max"""
	if value > max: value = max
	if value < min: value = min
	return value	

def hsv_to_rgb( h: int, s: int, v: int) -> tuple: # Converts hsv to rgb (Self-explanatory)
	"""
	Converts hsv to rgb
	
	:h: int, range 0 - 360 (loops)
	:s: int, range 0 - 100 
	:v: int, range 0 - 255
	"""
	if s:
		h %= 360
		h /= 360
		s = normalize(s,255,0)
		s /= 100
		v = normalize(v,255,0)
		
		
		if h == 1.0: h = 0.0
		i = int(h*6.0); f = h*6.0 - i
		
		w = round(v * (1.0 - s))
		q = round(v * (1.0 - s * f))
		t = round(v * (1.0 - s * (1.0 - f)))
		
		w = normalize(w,255,0)
		q = normalize(q,255,0)
		t = normalize(t,255,0)
		v = round(normalize(v,255,0))
		
		match i:
			case 0: output = (v, t, w)
			case 1: output = (q, v, w)
			case 2: output = (w, v, t)
			case 3: output = (w, q, v)
			case 4: output = (t, w, v)
			case 5: output = (v, w, q)
		return output
		
	else: 
		v = int(normalize(v,255,0))
		return (v, v, v)

def change_color_brightness(color:tuple, phase:int) -> tuple: # Takes a color and an int and adds that int to the color
	"""
	Changes the RGB values of a color by phase
	
	:color: tuple[3]. RGB
	:phase: int. Value to offset color by
	"""
	output = []
	for x in color:
		temp = normalize(x + phase,255,0)
		output.append(temp)
	tuple(output)
	return output


"""--------------------Squares / Blocks-------------------------"""


def generate_square(tiletype=0,catalystchance=False,catalyst=False) -> Square: # Generates a tile value
	"""
	Generates a tile value
	
	:tiletype: int. 0 if random, otherwise it will bypass assigning a random color.
	:catalystchance: bool. Whether this tile should have a chance of being a catalyst.
	:catalyst: bool. Whether this tile should be a catalyst.
	"""
	tile = Square(tiletype,1 if catalyst else 0)
	if tile.color == 0:
		if random.randint(0,100) < rainbowChance.value:
			tile.set(-1)
		else:
			tile.set(random.randint(1,numberColors.value))
	
	if catalystchance and random.randint(1,100) <= catalystChance.value + blockssincelastcatalyst * catalystChanceIncrease.value:
		catalyst = True
	if catalyst: tile.set(special=1)
	
	return tile

def compare_squares(localGameBoard, x: int, y: int, x2: int, y2: int) -> bool: # Checks if two squares are considered "connected" and can be cleared together
	if isinbounds(localGameBoard,x,y) and isinbounds(localGameBoard,x2,y2):
		if localGameBoard[x,y].color == 0 or localGameBoard[x2,y2].color == 0:
			return False
		elif localGameBoard[x,y].color == localGameBoard[x2,y2].color or localGameBoard[x,y].color == -1 or localGameBoard[x2,y2].color == -1:
			return True
		else:
			return False
	else:
		return False

def isinbounds(localGameBoard, x: int, y: int) -> bool: # Checks if the given coordinates are within bounds
	if x < 0 or x >= localGameBoard.width or y < 0 or y >= localGameBoard.height:
		return False
	else:
		return True

def create_block(type="random",color=0,catalyst=False) -> Block:
	global blockssincelastcatalyst
	
	colorsets = []
	for x in range(0,5):
		if random.randint(1,100) <= rainbowChance.value:
			colorsets.append(-1)
		else:
			colorsets.append(random.randint(1,numberColors.value))
	piecetype = list(PieceDict[random.choice(PieceWeights) if type == "random" else type])
	
	genblock = [colorsets[piecetype[0]],
					colorsets[piecetype[1]],
					colorsets[piecetype[2]],
					colorsets[piecetype[3]]]
	newblock = Block(Square(genblock[0]),Square(genblock[1]),Square(genblock[2]),Square(genblock[3]))
	
	if random.randint(1,100) <= catalystChance.value + blockssincelastcatalyst * catalystChanceIncrease.value:
		catalyst = True
	if catalyst:
		newblock.setspecial(1)
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

def reset_block() -> None:
	global block_pos_x, block_pos_y, block_fall_progress
	block_pos_x = GameBoard.width // 2 - 1
	block_pos_y = GameBoard.height - 3
	block_fall_progress = 0.0
	extrablocks.append(create_block())
	if len(extrablocks) > MAX_QUEUE_LENGTH:
		extrablocks.pop(0)

def place_block() -> None: 
	global grace, bombtimer, bombssincelastexplosion
	
	
	
	grace = grace_period
	if extrablocks[0][0,0].special == 1:
		if bombssincelastexplosion == 0:
			bombtimer = catalystTimer.value
		else:
			bombtimer += catalystTimer.value // (bombssincelastexplosion + 1)
			if bombtimer > catalystTimer.value:
				bombtimer = catalystTimer.value
		bombssincelastexplosion += 1
	
	for x in range(0,2):
		for y in range(0,2):
			GameBoard[block_pos_x + x,block_pos_y + y - 1] = extrablocks[0][x,y]
	cascade_board(GameBoard)
	if test_for_death(GameBoard):
		if bombtimer > 0:
			bombtimer = 1
		else:
			game_over()
	reset_block()

def rotate_block(block: Block, clockwise = True) -> Block: # 
	"""Takes a Block and rotates it clockwise or counterclockwise, then returns the Block."""
	if clockwise:
		return Block(block[1,0],block[0,0],block[1,1],block[0,1])
	else:
		return Block(block[0,1],block[1,1],block[0,0],block[1,0])


"""---------------------Board Functions-------------------------"""

def load_board(outputBoard,boardtoload):
	for x in range(0,outputBoard.width):
		for y in range(0,outputBoard.height):
			print(x,y,outputBoard.height - 4 - y)
			thing = boardtoload[outputBoard.height - 5  - y][x]
			if isinstance(thing,Square):
				outputBoard[x,y] = thing.copycell()
			else:
				outputBoard[x,y] = Square(thing,0)

def init_board() -> None: # Initializes the board
	"""This function initializes the game."""
	
	global GameBoard, ExplodeBoard, ConnectedBoard
	global block_pos_x, block_pos_y, block_fall_progress
	global bombtimer, blockssincelastcatalyst
	global previousscores
	
	apply_config()
	
	previousscores = []
	for x in range(0,MAX_QUEUE_LENGTH):
		extrablocks.append(create_block())
		if len(extrablocks) > MAX_QUEUE_LENGTH:
			extrablocks.pop(0)
			break
	
	blockssincelastcatalyst = 0 if game_state == "game" else 3
	
	GameBoard = Board(boardWidth.value,boardHeight.value + 4,1)
	ConnectedBoard = Board(boardWidth.value,boardHeight.value + 4)
	ExplodeBoard = Board(boardWidth.value,boardHeight.value + 4)
	
	block_pos_x = GameBoard.width // 2 - 1
	block_pos_y = GameBoard.height - 3
	block_fall_progress = 0.0 
	
	if game_state == "main_menu":
		bombtimer = catalystTimer.value
		if random.randint(1,20) == 1:
			load_board(GameBoard,literallythebestboard)
		else:
			for x in range(0,GameBoard.width):
				for y in range(0,GameBoard.height - random.randint(8,GameBoard.height - 2)):
					GameBoard[x,y] = generate_square(catalystchance=True)
				for y in range(GameBoard.height - 4,GameBoard.height):
					if (random.randint(1,2) == 2):
						GameBoard[x,y] = generate_square(catalystchance=True)
	else:
		bombtimer = -1

def init_concatalyst_board():
	global ConcatalystConnectedBoard
	for y in range(0,len(concatalystboardlayout)):
		for x in range(0,len(concatalystboardlayout[0])):
			ConcatalystTitleBoard[x,y] = Square(concatalystboardlayout[4-y][x])
	ConcatalystTitleBoard[2,4] = Square(2,1)
	ConcatalystConnectedBoard = find_connected_squares(ConcatalystTitleBoard)
	
def find_connected_squares(localInputBoard) -> Board: # Searches through the board and figures out which blocks are connected to catalysts.
	"""
	Searches through the board and returns a board of all cells connected to catalysts.
	
	
	"""
	
	OutputBoard = Board(localInputBoard.width,localInputBoard.height)
	stack = []
	
	for x in range(0,localInputBoard.width):
		for y in range(0,localInputBoard.height):
			if localInputBoard[x,y].special == 1:
				OutputBoard[x,y] += 1
				stack.append((x,y))
	
	while len(stack) > 0:
		x = stack[0][0]
		y = stack[0][1]
		stack.pop(0)
		for p in ((x+1,y),(x-1,y),(x,y+1),(x,y-1)):
			
			if isinbounds(localInputBoard,p[0],p[1]) and localInputBoard[p[0],p[1]].special == 0 and (OutputBoard[p[0],p[1]] == 0 or OutputBoard[p[0],p[1]] > OutputBoard[x,y] + 1) and compare_squares(localInputBoard,x,y,p[0],p[1]):
				stack.append((p[0],p[1]))
				OutputBoard[p[0],p[1]] = OutputBoard[x,y] + 1
	return OutputBoard

def clear_connected_squares(localGameBoard = GameBoard, localExplodeBoard = ExplodeBoard) -> tuple: # Deletes squares connected to catalysts and returns point values
	"""
	
	
	:localExplodeBoard: Board. Determines which blocks should be removed from play and how many points they are worth.
	"""
	global timesinceexplode
	timesinceexplode = 0
	score = 0
	squares = 0
	highestchain = 0
	pointspersquare = BASE_POINTS
	for x in range(0,localGameBoard.width):
		for y in range(0,localGameBoard.height):
			if localExplodeBoard[x,y] != 0:
				localGameBoard[x,y].set(0,0)
				squares += 1
				if localExplodeBoard[x,y] > highestchain:
					highestchain = localExplodeBoard[x,y]
				score += int(10 + localExplodeBoard[x,y]**2)
	return score, squares, highestchain

def cascade_board(localGameBoard, hard_cascade = False) -> None:
	gravityflag = False
	cascadeflag = False
	for x in range(0,localGameBoard.width):
		#First check if anything is wrong in the column
		gravityflag = False # Becomes true when the search finds an empty space
		cascadeflag = False # Becomes true when the search finds a non-empty space above an empty space
		for y in range(0,localGameBoard.height):
			
			if gravityflag and localGameBoard[x,y].color != 0:
				cascadeflag = True
			elif localGameBoard[x,y].color == 0:
				gravityflag = True
		
		#if something is wrong with the column, it will go through each block until it finds empty space, then if it finds blocks above that it will pull them to the first black space it will continue progressively.
		gravityflag = False
		if cascadeflag:
			lastsafe = 0
			for y in range(0,localGameBoard.height):
				if localGameBoard[x,y].color == 0:
					lastsafe = y
					break
			if hard_cascade:
				for y in range(lastsafe,localGameBoard.height):
					if localGameBoard[x,y].color != 0:
						localGameBoard[x,lastsafe] = localGameBoard[x,y].copycell()
						localGameBoard[x,y].set(0,0)
						lastsafe += 1
			else:
				for y in range(lastsafe,localGameBoard.height):
					if localGameBoard[x,y].color != 0:
						localGameBoard[x,y-1] = localGameBoard[x,y].copycell()
						localGameBoard[x,y].set(0,0)

def explode_board(localGameBoard) -> None: # This function is kind of unnecessary and should probably be moved to be part of find_connected_squares()
	global score, longestchain, squarescleared, bombssincelastexplosion, ExplodeBoard, updatescreennextframe
	cascade_board(localGameBoard,True)
	ExplodeBoard = find_connected_squares(localGameBoard)
	previousscores.insert(0,tuple(clear_connected_squares(localGameBoard,ExplodeBoard) + tuple([clock])))
	
	bombssincelastexplosion = 0
	
	score += previousscores[0][0]
	squarescleared += previousscores[0][1]
	if longestchain < previousscores[0][2]:
		longestchain = previousscores[0][2]
	if len(previousscores) > 5:
		previousscores.pop(-1)
	updatescreennextframe = 2


"""--------------------Gameplay Functions-------------------------"""


def level_up() -> None: # Slightly increases difficulty
	global gravity, level
	gravity += 1
	level += 1

def test_for_death(inputBoard = GameBoard) -> bool:
	for x in range(0,inputBoard.width):
		if GameBoard[x,inputBoard.height - 3].color != 0:
			return True
	return False

def game_over():
	global game_state, updatescreennextframe
	updatescreennextframe = 2
	game_state = "death_menu"


"""--------------------Graphics Functions-------------------------"""



def draw_concatalyst_board() -> None:
	for x in range(0,43):
		for y in range(0,5):
			if ConcatalystTitleBoard[x,y].color:
				blockID = ConcatalystTitleBoard[x,y]
				offsetx = 40 + (12 * x)
				offsety = 88 - (12 * y)
				
				blockcolor = ColorIndex[blockID.color]
				catalystcoloroffset = 4 * ( abs((-clock + 3 * ConcatalystConnectedBoard[x,y]) % 60 - 30) - 15 ) 
				
				if ConcatalystConnectedBoard[x,y] > 0:
					blockcolor = change_color_brightness(blockcolor,catalystcoloroffset)
						
				if blockID.color == -1:
					blockcolor = hsv_to_rgb(clock,100,255)
				elif blockID.color > 0 and blockID.color < len(ColorIndex):
					blockcolor = ColorIndex[blockID.color]
				pygame.draw.rect(window,blockcolor,pygame.Rect((	
						(offsetx, offsety	),
						(12,12))))
				
				if ConcatalystTitleBoard[x,y].color == 1:
					rainbowcolor = hsv_to_rgb(clock,100,255)
					pygame.draw.rect(window,rainbowcolor,pygame.Rect((	
								(offsetx + 2, offsety + 2	),
								(8,8))))
	screenupdaterects.append(Rect(38,38,525,64)) # Concatalyst Title Board

def draw_game(explosion=False,fakeboard=False) -> None:
	"""This function draws the game."""
	global textoffset
	
	#window.fill(BLACK)
	window.blit(backgroundImage,(0,0))
	
	#Draw the board
	for x in range(0,GameBoard.width):
		for y in range(0,(GameBoard.height - 4) ):
			if GameBoard[x,y] == 0:
				if ExplodeBoard[x,y] != 0:
					
					excolor = hsv_to_rgb(60 - 5 * ExplodeBoard[x,y],10 * ExplodeBoard[x,y],255)
					excolor = change_color_brightness(excolor, 40 * ExplodeBoard[x,y]  - 4 * timesinceexplode)
					
					if sum(excolor) > 40:
						draw_square(excolor,x,y)
			else:
				excolor = get_square_color(GameBoard[x,y])
				draw_square(excolor,x,y,special=GameBoard[x,y].special)
	
	if not fakeboard:
		#Draw Up Next
		if len(extrablocks) > 1:
			for z in range(1,len(extrablocks)):
				for x in range(0,2):
					for y in range(0,2):
						excolor = get_square_color(extrablocks[z][x,y])
						draw_square(excolor,x - 3, 18 + y - (3 * z),special=extrablocks[z][x,y].special )
		
		#Draw the active block
		for x in range(0,2):
			for y in range(0,2):
				excolor = get_square_color(extrablocks[0][x,y])
				draw_square(excolor,	(x + block_pos_x),	(y + block_pos_y),special=extrablocks[0][x,y].special)
		
	
	#Lines
	for x in range(0,GameBoard.width + 1 ):
		pygame.draw.line(window,WHITE,
			((leftscreen + (blockSize.value * x)),topscreen),
			((leftscreen + (blockSize.value * x)),bottomscreen))
	for y in range(0,GameBoard.height -3):
		pygame.draw.line(window,WHITE,
			(leftscreen,(bottomscreen - (blockSize.value * y))),
			(rightscreen,(bottomscreen - (blockSize.value * y))))
	
	if bombtimer > 0 and catalystTimer.value != 0:
		#operationlength2 = time.perf_counter_ns()
		bombline = (GameBoard.height - 4) * blockSize.value * bombtimer // catalystTimer.value
		for x in range(0,GameBoard.width + 1 ):
			pygame.draw.line(window,RED,((leftscreen + (blockSize.value * x)),bottomscreen),((leftscreen + (blockSize.value * x)),bottomscreen - bombline), 3)
		for y in range(0,GameBoard.height -3):
			if bottomscreen - bombline < bottomscreen - (blockSize.value * y):
				pygame.draw.line(window,RED,
					(leftscreen,(bottomscreen - (blockSize.value * y))),
					(rightscreen,(bottomscreen - (blockSize.value * y))),3)
	if game_state == "game":
		game_text()
	
	if fakeboard:
		screenupdaterects.append(Rect(leftscreen - blockSize.value,topscreen - blockSize.value,boardwidth + 2 * blockSize.value,boardheight + 2 *blockSize.value))
	else:
		screenupdaterects.append(Rect(leftscreen - 5 - (blockSize.value * 5),topscreen - 5 - (blockSize.value * 3),
								boardwidth + 10+ (blockSize.value * 5),boardheight + 10 + (blockSize.value * 3)))

def get_square_color(square: Square):
	if square.color == -1:
		blockcolor = hsv_to_rgb(clock,100,255)
	elif square.color > 0 and square.color < len(ColorIndex):
		blockcolor = ColorIndex[square.color]
	else:
		blockcolor = BLACK
		
	
	return blockcolor

def draw_square(blockcolor, x: int,y: int, special = 0, blocksize = 0, accentcolor = BLACK) -> None:
	if blocksize == 0:
		blocksize = blockSize.value
	offsetx = leftscreen + (blocksize * x)
	offsety = bottomscreen - (blocksize * (y+1))
	
	
	if connectionType.value == 0 and (special == 1 or bombtimer > 0 and ConnectedBoard[x,y] > 0):
		catalystcoloroffset = 8 * ( abs(	(-clock * pulseIntensity.value // 15 + 8 * ConnectedBoard[x,y]) % (4*pulseIntensity.value) - (2*pulseIntensity.value)) - pulseIntensity.value ) 
		blockcolor = change_color_brightness(blockcolor,catalystcoloroffset)
	
	pygame.draw.rect(window,blockcolor,pygame.Rect((
					(offsetx, offsety),
					(blocksize,blocksize))))	
	
	if (special == 1 or bombtimer > 0 and ConnectedBoard[x,y-1] > 0):
		if connectionType.value == 0:
			if special == 1:
					pygame.draw.circle(window,accentcolor, (offsetx + blocksize // 2, offsety + blocksize // 2 ), blocksize // 2 - 5)
		elif connectionType.value == 1:
			pygame.draw.line(window,BLACK,(offsetx + blocksize // 2,offsety),(offsetx + blocksize // 2,offsety + blocksize),3)
			pygame.draw.line(window,BLACK,(offsetx,	offsety + blocksize // 2),(offsetx + blocksize,offsety + blocksize // 2),3)
			if special == 1:
					pygame.draw.circle(window,BLACK, (offsetx + blocksize // 2, offsety + blocksize // 2 ), blocksize // 4)
		elif connectionType.value == 2:
			if special == 1:
					pygame.draw.circle(window,BLACK, (offsetx + blocksize // 2, offsety + blocksize // 2 ), blocksize // 4)
			for p in ((1,0),(-1,0),(0,1),(0,-1)):
				if isinbounds(GameBoard,x + p[0],y + p[1]) and ConnectedBoard[x + p[0],y + p[1]] != 0 and ConnectedBoard[x,y] != 0 and abs(ConnectedBoard[x + p[0],y + p[1]] - ConnectedBoard[x,y -1]) == 1:
					pygame.draw.line(window,BLACK,	(offsetx + blocksize // 2,	offsety + blocksize // 2),
															(offsetx + blocksize // 2 + p[0] * blocksize,	offsety + blocksize // 2 - p[1] * blocksize),3)
				

"""--------------------Game State Functions-------------------------"""

def apply_config() -> None: # Initializes variables to config values
	"""Basically just makes sure variables are set to what they need to be (for config settings and such)"""
	global boardwidth, boardheight, leftscreen, rightscreen, topscreen, bottomscreen, updatescreennextframe
	global grace_period, blockssincelastcatalyst, level, score, squarescleared, longestchain
	grace_period = gracePeriod.value
	level = startLevel.value
	score = 0
	squarescleared = 0
	longestchain = 0
	
	boardwidth = blockSize.value * boardWidth.value
	boardheight = blockSize.value * boardHeight.value

	leftscreen = centerx - boardwidth // 2 if game_state == "game" else centerx
	rightscreen = centerx + boardwidth // 2 if game_state == "game" else centerx + boardwidth
	topscreen = centery - boardheight // 2
	bottomscreen = centery + boardheight // 2
	
	updatescreennextframe = 2

def global_board_updates() -> None:
	"""This is a function. It does stuff"""
	
	global clock, bombtimer, timesinceexplode, ConnectedBoard
	
	clock += 1
	timesinceexplode += 1
	bombtimer -= 1
	
	if clock % 3 == 0:
		cascade_board(GameBoard)
	
	if bombtimer == 0:
		explode_board(GameBoard)
	
	if bombtimer > 0 and bombtimer % 10 == 0:
		ConnectedBoard = find_connected_squares(GameBoard)
	
	if game_state == "main_menu" and bombtimer <= -titleBoardRefresh.value:
		init_board()
		bombtimer = catalystTimer.value

def global_controls() -> None:
	global keydown, game_state
	keys = pygame.key.get_pressed()
	
	if keys[K_ESCAPE]:
		if game_state == "pause_menu":
			game_state = "game"
			updatescreennextframe = 2
		if game_state == "game":
			game_state = "pause_menu"
			updatescreennextframe = 2

def game_processing() -> None: # Ingame event handling
	"""This function does most of the game's event handling."""
	global keydown, game_state
	global block_pos_x, block_pos_y, grace, block_fall_progress
	global extrablocks, ExplodeBoard, ConnectedBoard
	
	keys = pygame.key.get_pressed()
	
	global_board_updates()
	global_controls()
	
	if squarescleared > 10 * level:
		level_up()
	
	if keys[K_LSHIFT]:
		cascade_board(GameBoard,hard_cascade=True)
	
	if grace <= 0:
		block_fall_progress += gravity
		if block_fall_progress > 1000:
			if block_pos_y < 1 or block_pos_y > 17 or block_pos_x < 0 or block_pos_x >= GameBoard.width - 1 or GameBoard[block_pos_x,block_pos_y - 2] == 0 and GameBoard[block_pos_x + 1,block_pos_y - 2] == 0 and block_pos_y >= 2:
				block_pos_y -= 1
			else:
				place_block()
			block_fall_progress = 0
	else:
		grace -= 1
	
	if not keydown:
		if keys[K_w]:
			reset_block()
		
		
		if keys[K_z]:
			extrablocks[0] = rotate_block(extrablocks[0])
		if keys[K_x]:
			extrablocks[0] = rotate_block(extrablocks[0],clockwise=False)
			
		outofbounds = False
		if block_pos_y < 1 or block_pos_y > 17 or block_pos_x < 0 or block_pos_x >= GameBoard.width - 1:
			outofbounds = True
		#Necessary to prevent out of bounds crashing
		if keys[K_RIGHT] and block_pos_x < GameBoard.width - 2:
			if outofbounds or GameBoard[block_pos_x + 2,block_pos_y] == 0 and GameBoard[block_pos_x + 2,block_pos_y - 1] == 0:
				block_pos_x += 1
		if keys[K_LEFT] and block_pos_x > 0:
			if outofbounds or GameBoard[block_pos_x - 1,block_pos_y] == 0 and GameBoard[block_pos_x - 1,block_pos_y - 1] == 0:
				block_pos_x -= 1
		if keys[K_UP]:
			place_block()
		if keys[K_DOWN]:
			if outofbounds or GameBoard[block_pos_x,block_pos_y - 2] == 0 and GameBoard[block_pos_x + 1,block_pos_y - 2] == 0 and block_pos_y >= 2:
				block_pos_y -= 1
				block_fall_progress = 0
			else:
				place_block()
	
	if keys[K_UP] or keys[K_DOWN] or keys[K_RIGHT] or keys[K_LEFT] or keys[K_z] or keys[K_x] or keys[K_c] or keys[K_p]:
		keydown += 1
		if keydown >= 10:
			keydown = 0
	else:
		keydown = 0
	
	
	
	# draw the game
	draw_game()

def menu_processing() -> None:
	"""This function controls the menu."""
	global keys, keydown, game_state, cursor_pos, updatescreennextframe, screenupdaterects, clock, selectedpreset
	
	if game_state == "main_menu":
		global_board_updates()
		draw_game(fakeboard=True)
		
	else:
		clock += 1
		draw_game()
	global_controls()
	
	if game_state == "main_menu":
		main_menu_text()
		draw_concatalyst_board()
	elif game_state == "pause_menu":
		pause_menu_text()
	elif game_state == "death_menu":
		death_menu_text()
	 # Display Board
	
	keys = pygame.key.get_pressed()
	# move cursor
	if (keys[K_UP]) and not keydown:
		cursor_pos -= 1
		if cursor_pos < 0:
			cursor_pos = 0
	if (keys[K_DOWN]) and not keydown:
		cursor_pos += 1
		if cursor_pos > len(buttonlist) - 2:
			cursor_pos = len(buttonlist) - 2

	# change settings
	if (keys[K_z]) and not keydown:
		updatescreennextframe = 2
		match buttonlist[cursor_pos]:
			case "startgamestandard":
				game_state = "game"
				init_board()
			case "startgameendless":
				game_state = "game"
				init_board()
			case "reinitialize":
				init_board()
			case "restartgame":
				game_state = "game"
				init_board()
			case "continuegame":
				game_state = "game"
			case "tomainmenu":
				game_state = "main_menu"
			case other:
				if type(buttonlist[cursor_pos]) == str and buttonlist[cursor_pos] != "null":
					apply_preset(buttonlist[cursor_pos])
					selectedpreset = buttonlist[cursor_pos]
		
	
	if isinstance(buttonlist[cursor_pos],Config) and not keydown:
		updatescreennextframe = 2
		if buttonlist[cursor_pos].boolean:
			if keys[K_z] or keys[K_RIGHT] or keys[K_LEFT]:
				buttonlist[cursor_pos].toggle()
		else:
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

def apply_preset(preset) -> None:
	match preset:
		case "normal":
			startLevel.set(1)
			doLevelUp.set(1)
			squaresPerLevel.set(20)
			
			boardHeight.set(16)
			boardWidth.set(10)
			numberColors.set(5)
			gracePeriod.set(100) 
			rainbowChance.set(10)
			catalystChance.set(-5) 
			catalystChanceIncrease.set(5) 
			catalystTimer.set(400)
			
		case "casual":
			startLevel.set(1)
			doLevelUp.set(1)
			squaresPerLevel.set(20)
			
			boardHeight.set(16)
			boardWidth.set(10)
			numberColors.set(4)
			gracePeriod.set(150)
			rainbowChance.set(15)
			catalystChance.set(-10) 
			catalystChanceIncrease.set(10) 
			catalystTimer.set(400)
			
		case "easy":
			startLevel.set(1)
			doLevelUp.set(1)
			squaresPerLevel.set(20)
			
			boardHeight.set(16)
			boardWidth.set(10)
			numberColors.set(5)
			gracePeriod.set(150)
			rainbowChance.set(15)
			catalystChance.set(-10) 
			catalystChanceIncrease.set(10) 
			catalystTimer.set(400)
			
		case "hard":
			startLevel.set(1)
			doLevelUp.set(1)
			squaresPerLevel.set(25)
			
			boardHeight.set(16)
			boardWidth.set(12)
			numberColors.set(6)
			gracePeriod.set(75) 
			rainbowChance.set(7)
			catalystChance.set(-4) 
			catalystChanceIncrease.set(4) 
			catalystTimer.set(500)
			
		case "extreme":
			startLevel.set(1)
			doLevelUp.set(1)
			squaresPerLevel.set(30)
			
			boardHeight.set(18)
			boardWidth.set(14)
			numberColors.set(7)
			gracePeriod.set(50) 
			rainbowChance.set(5)
			catalystChance.set(-8) 
			catalystChanceIncrease.set(4) 
			catalystTimer.set(600)
			
		case "absurd":
			startLevel.set(1)
			doLevelUp.set(1)
			squaresPerLevel.set(40)
			
			boardHeight.set(20)
			boardWidth.set(14)
			numberColors.set(8)
			gracePeriod.set(30) 
			rainbowChance.set(5)
			catalystChance.set(-6) 
			catalystChanceIncrease.set(3) 
			catalystTimer.set(800)
		
		case "morespacemoreproblems":
			startLevel.set(1)
			doLevelUp.set(1)
			squaresPerLevel.set(30)
			
			boardHeight.set(24)
			boardWidth.set(16)
			numberColors.set(8)
			gracePeriod.set(150) 
			rainbowChance.set(15)
			catalystChance.set(-10) 
			catalystChanceIncrease.set(10) 
			catalystTimer.set(400)
		


"""--------------------Text and GUI Functions-------------------------"""


def game_text() -> None:
	global textoffset, updatescreennextframe
	source = (rightscreen + 5, topscreen)
	
	textoffset = 0
	normaltext(f"Level: {level}",WHITE,source)
	normaltext(f"Score: {score}",WHITE,source)
	normaltext(f"Cleared: {squarescleared}",WHITE,source)
	normaltext(f"Longest Chain: {longestchain}",WHITE,source)
		
	for txt in previousscores:
		if txt[3] > clock - 600:
			normaltext(f"+{txt[0]}! {txt[1]} squares! {txt[2]} Chain!",YELLOW,source,SmallerFont)
		elif txt[3] == clock - 600:
			updatescreennextframe = 2

def main_menu_text() -> None: # Draws the menu
	global buttonlist, menuitemoffset, window, textoffset
	
	buttonlist = []
	menuitemoffset = 0
	textoffset = 0
	
	#normaltext("Action Puzzle Game Thing", WHITE, (0,0), False)
	#window.blit(DefaultFont.render("Action Puzzle Game Thing", True, WHITE),(0, 0))
	menutext("Play Game","startgamestandard")
	menutext("Game Modes",gamemodeMenu,txtcolornormal=PINK)
	if gamemodeMenu.value:
		menutext(f"Start Level: {startLevel.value}",startLevel)
		menutext("Standard","startgamestandard")
		menutext("Endless","startgameendless")
		menutext("Single Level","singlelevelendless")
		
	menutext("Game Presets",presetsMenu,txtcolornormal=PINK)
	if presetsMenu.value:
		menutext("Difficulty Presets",presetsMenuDifficulty,txtcolornormal=BLUE)
		if presetsMenuDifficulty.value:
			menutext("Casual","casual",txtcolornormal=ROSEGOLD if selectedpreset == "casual" else WHITE)
			menutext("Easy","easy",txtcolornormal=ROSEGOLD if selectedpreset == "easy" else WHITE)
			menutext("Normal","normal",txtcolornormal=ROSEGOLD if selectedpreset == "normal" else WHITE)
			menutext("Hard","hard",txtcolornormal=ROSEGOLD if selectedpreset == "hard" else WHITE)
			menutext("Extreme","extreme",txtcolornormal=ROSEGOLD if selectedpreset == "extreme" else WHITE)
			menutext("Absurd","absurd",txtcolornormal=ROSEGOLD if selectedpreset == "absurd" else WHITE)
		menutext("Other Presets",presetsMenuOther,txtcolornormal=BLUE)
		if presetsMenuOther.value:
			menutext("More Space More Problems","morespacemoreproblems",txtcolornormal=ROSEGOLD if selectedpreset == "morespacemoreproblems" else WHITE)
	menutext("Game Setup",optionsMenu,txtcolornormal=PINK)
	if optionsMenu.value:
		menutext("Refresh Title","reinitialize")
		menutext("Gameplay Options",optionsMenuGameplay,txtcolornormal=BLUE)
		if optionsMenuGameplay.value:
			menutext(f"Level Increase: {'On' if doLevelUp.value else 'Off'}",doLevelUp)
			if doLevelUp.value:
				menutext(f"Blocks per Level: {squaresPerLevel.value}",squaresPerLevel)
			
			menutext(f"Grace Period: {gracePeriod.value}",gracePeriod)
			menutext(f"Colors: {numberColors.value}",numberColors)
			menutext(f"Rainbow Chance: {rainbowChance.value}",rainbowChance)
			menutext(f"Catalyst Chance (%): {catalystChance.value}",catalystChance)
			menutext(f"+ Cat Chance (%): {catalystChanceIncrease.value}",catalystChanceIncrease)
			menutext(f"Catalyst Timer: {catalystTimer.value}",catalystTimer)
		menutext("Board Options",optionsMenuBoard,txtcolornormal=BLUE)
		if optionsMenuBoard.value:
			menutext(f"Board Width: {boardWidth.value}",boardWidth)
			menutext(f"Board Height: {boardHeight.value}",boardHeight)
			menutext(f"Block Size: {blockSize.value}",blockSize)
		menutext("Visual Options",optionsMenuVisuals,txtcolornormal=BLUE)
		if optionsMenuVisuals.value:
			menutext(f"Title Refresh: {titleBoardRefresh.value}",titleBoardRefresh)
			match connectionType.value:
				case 0: style = "Pulse"
				case 1: style = "Cross"
				case 2: style = "Lines"
			menutext(f"Connection Style: {style}",connectionType)
			if connectionType == 0:
				menutext(f"Pulse Intensity: {pulseIntensity.value}",pulseIntensity)
	menutext("Standard","starttutorial")
	menutext(f"Debug: {connectionType.value}")
		
		
	
	menutext("","5")

def pause_menu_text() -> None: # Draws the menu
	global buttonlist, menuitemoffset, window, textoffset
	
	game_text()
	buttonlist = []
	menuitemoffset = 0
	textoffset = 0
	
	normaltext("Game paused.", YELLOW, (50,50), False)
	menutext("Continue","continuegame")
	menutext("Restart","restartgame")
	menutext("Main Menu","tomainmenu")
		
		
	
	menutext("","5")

def death_menu_text() -> None: # Draws the menu
	global buttonlist, menuitemoffset, window, textoffset
	
	buttonlist = []
	menuitemoffset = 0
	textoffset = 0
	
	normaltext("Game over!", RED, (50,150), False)
	#window.blit(DefaultFont.render("Action Puzzle Game Thing", True, WHITE),(0, 0))
	normaltext(f"Score: {score}!", GREEN, (50,30), True)
	normaltext(f"Squares Cleared: {squarescleared}!", YELLOW, (50,30), True)
	normaltext(f"Longest Chain: {longestchain}!", PINK, (50,30), True)
	
	menutext("Restart","restartgame",source=(50,200))
	menutext("Main Menu","tomainmenu",source=(50,200))
	
	
	
		
		
	
	menutext("","5")

def menutext(itemtext, buttonmask = "null", txtcolorpressed = YELLOW, txtcolornormal = WHITE, source=(50,150), offset=True, font=DefaultFont) -> Rect: # Draws interactable text.
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
	color = txtcolorpressed if cursor_pos == menuitemoffset else txtcolornormal
	textbox = DefaultFont.render(itemtext, True, color)
	window.blit(textbox,(source[0], source[1] + menuitemoffset * FONTSIZE))
	if offset:
		menuitemoffset += 1
		
	textrect = textbox.get_rect(topleft = (source[0], source[1] + (menuitemoffset-1) * FONTSIZE))
	screenupdaterects.append(textrect)
	#print(source,textrect)
	return textrect

def normaltext(itemtext: str, txtcolor= WHITE, source = (0,0), offset = True, font = DefaultFont) -> Rect: # Draws non-interactable text consecutively.
	"""
	Draws non-interactable text. Used consecutevely, it can create multiple lines.
	
	:itemtext: string. Text (Required)
	:txtcolor: tuple[3]. RGB values for text color. (Default: (255,255,255))
	:source: tuple(2). Coordinates for top left corner of text. (Default: (0,0))
	:offset: bool. Whether or not to increment offset. (Default: True)
	:font: pygame.font. (Default: DefaultFont)
	"""
	
	global window, textoffset
	textbox = font.render(itemtext, True, txtcolor)
	
	window.blit(textbox,(source[0], source[1] + textoffset * FONTSIZE))
	if offset:
		textoffset += 1
	textrect = textbox.get_rect(topleft = (source[0], source[1] + (textoffset) * FONTSIZE))
	screenupdaterects.append(textrect)
	#print(source,textrect)
	return textrect



init_board()
init_concatalyst_board()
# game loop
while running:
	#operationlength = time.perf_counter_ns()
	if game_state == "game":
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

			boardwidth = (blockSize.value * GameBoard.width)
			boardheight = (blockSize.value * ( GameBoard.height - 4) )

			leftscreen = centerx - boardwidth // 2
			rightscreen = centerx + boardwidth // 2
			topscreen = centery - boardheight // 2
			bottomscreen = centery + boardheight // 2
			
			updatescreennextframe = 2
	
	
	if updatescreennextframe > 0:
		pygame.display.update()
		updatescreennextframe -= 1
	else:
		pygame.display.update(screenupdaterects)
	screenupdaterects = []
	fps.tick(60)
	

pygame.quit()
sys.exit()