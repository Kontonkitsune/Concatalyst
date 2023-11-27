"""
fuck this shit

Code by: Lucina Riley / Kontonkitsune
Last Updated: 15/7/2023

Action Puzzle thing





To Do:

Change the function that finds catalyst block connections and set it take an input board and output board.

Build third connected board to act as a "pre-explosion" explosion board (tracks the things connected to catalysts)

Make third connected board do some jank shit to give a shimmer effect to blocks that will be cleared. Maybe even make it progressive or something.



"""

import random
import pygame, sys
import math
from pygame.locals import *

pygame.init()
fps = pygame.time.Clock()

"""--------------Class Structures--------------"""

class Cell:
	def __init__(self, color=0,special=0):
		self.color = color
		self.special = special
	def set(self,color = -1, special = -1):
		if special != -1:
			self.special = special
		if color != -1:
			self.color = color
	
	def copycell(self):
		return Cell(self.color,self.special)
	
	def __add__(self,other):
		return Cell(self.color + other,self.special)
		
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
			self.cells = [[Cell() for y in range(height)] for x in range(width)]
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
		for y in range(1,len(self.cells[0])):
			for x in range(1,len(self.cells)):
				string += str(self[x,y]) + ", "
			string += "\n"
				
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

BLUE = (0, 0, 255)
BLUECAT = (63, 63, 192)

CYAN = (32, 225, 255)
CYANCAT = (63, 192, 255)

SILVER = (232, 245, 255)
GOLD = (220, 188, 12)

GOLDCAT = (212, 212, 255)
ROSEGOLD = (248,185,150)

ColorIndex = (
	(BLACK,BLACK),
	(GOLD,ROSEGOLD),
	(PINK,PINKCAT),
	(BLUE,BLUECAT),
	(GREEN,GREENCAT),
	(YELLOW,YELLOWCAT),
	(RED,REDCAT),
	(CYAN,CYANCAT)
	)


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

boardwidth = BLOCK_SIZE * BOARD_SIZE_X
boardheight = BLOCK_SIZE * BOARD_SIZE_Y

leftscreen = centerx - boardwidth // 2
rightscreen = centerx + boardwidth // 2
topscreen = centery - boardheight // 2
bottomscreen = centery + boardheight // 2

backgroundImage = pygame.image.load("BackgroundImage.jpg")

#Menu and Text Variables
buttonlist = []
menuitemoffset = 0
textoffset = 0
cursor_pos = 0

# Game Instance Variables
GameBoard = Board(BOARD_SIZE_X,BOARD_SIZE_Y + 4,1) # The game board. It's a bit bigger than it looks.
ExplodeBoard = Board(BOARD_SIZE_X,BOARD_SIZE_Y + 4) # The board used for tracking which blocks are supposed to explode. Also acts as a handy graphics thing.
ConnectedBoard = Board(BOARD_SIZE_X,BOARD_SIZE_Y + 4)

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
boardMenu = Config(0,boolean=True)
gameplayMenu = Config(0,boolean=True)
visualsMenu = Config(0,boolean=True)

# Visual
blockSize = Config(BLOCK_SIZE,100,10,5) # Block size 
titleBoardRefresh = Config(300,1500,50,50)
pulseIntensity = Config(15,30,0,5)

# Board
boardHeight = Config(BOARD_SIZE_Y,24,8,1) # Height of the board
boardWidth = Config(BOARD_SIZE_X,24,4,1) # Width of the board
numberColors = Config(5,6,2,1)

# Gameplay
startLevel = Config(1,100,1,1) # Starting level
gracePeriod = Config(100,1000,0,10) # How long a block can idle at the starting position before beginning to fall.
rainbowChance = Config(10,100,1,1)
catalystChance = Config(-5,100,-50,5) # Base chance for any block to be a catalyst
catalystGuarantee = Config(5,10,0,1) # How 
catalystTimer = Config(400,10000,0,100) # How long it takes bombs to go off
maxBlocksPerCatalyst = Config(10,100,1,1) # How many blocks before a catalyst should be guaranteed (REDUNDANT)




# window declaration
window = pygame.display.set_mode((WIDTH, HEIGHT),RESIZABLE)
pygame.display.set_caption('Action Puzzler Thing')


literallythebestboard = (
	(2,2,3,7,1,1,8,2,2,7),
	(7,1,1,2,2,2,2,2,1,1),
	(2,2,1,1,1,1,1,1,1,2),
	(1,2,2,2,1,1,1,2,2,7),
	(7,1,1,2,2,2,2,2,1,1),
	(2,2,1,1,1,1,1,1,1,2),
	(1,2,2,2,1,1,1,2,2,7),
	(7,1,1,2,2,2,2,2,1,1),
	(6,6,1,1,1,1,1,1,1,2),
	(1,6,6,6,1,1,1,6,6,7),
	(7,5,5,6,6,6,6,6,5,5),
	(4,4,5,5,5,5,5,5,5,4),
	(3,4,4,4,4,4,4,4,4,7),
	(7,3,3,3,3,3,3,3,3,3),
	(2,2,2,2,2,2,2,2,2,2),
	(1,1,1,1,1,1,1,1,1,7)
)


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

def generate_tile(tiletype=0,catalystchance=False,catalyst=False) -> Cell: # Generates a tile value
	"""
	Generates a tile value
	
	:tiletype: int. 0 if random, otherwise it will bypass assigning a random color.
	:catalystchance: bool. Whether this tile should have a chance of being a catalyst.
	:catalyst: bool. Whether this tile should be a catalyst.
	"""
	tile = Cell(tiletype,1 if catalyst else 0)
	if tile.color == 0:
		if random.randint(0,100) < rainbowChance.value:
			tile.set(1)
		else:
			tile.set(random.randint(2,numberColors.value+1))
	
	if catalystchance and random.randint(1,100) <= catalystChance.value + blockssincelastcatalyst * catalystGuarantee.value:
		catalyst = True
	if catalyst: tile.set(special=1)
	
	return tile

def apply_config() -> None: # Initializes variables to config values
	"""Basically just makes sure variables are set to what they need to be (for config settings and such)"""
	global boardwidth, boardheight, leftscreen, rightscreen, topscreen, bottomscreen
	global grace_period, blockssincelastcatalyst, level, score, squarescleared
	grace_period = gracePeriod.value
	level = startLevel.value
	score = 0
	squarescleared = 0
	blockssincelastcatalyst = 0 if game_state else 3
	
	boardwidth = blockSize.value * boardWidth.value
	boardheight = blockSize.value * boardHeight.value

	leftscreen = centerx - boardwidth // 2 if game_state else centerx
	rightscreen = centerx + boardwidth // 2 if game_state else centerx + boardwidth
	topscreen = centery - boardheight // 2
	bottomscreen = centery + boardheight // 2

def init_board() -> None: # Initializes the board
	"""This function initializes the game."""
	
	global GameBoard, ExplodeBoard, ConnectedBoard
	global block_pos_x, block_pos_y, block_fall_progress
	global bombtimer
	
	apply_config()
	
	for x in range(0,MAX_QUEUE_LENGTH):
		extrablocks.append(create_block())
		if len(extrablocks) > MAX_QUEUE_LENGTH:
			extrablocks.pop(0)
			break
	
	GameBoard = Board(boardWidth.value,boardHeight.value + 4,1)
	ConnectedBoard = Board(boardWidth.value,boardHeight.value + 4)
	ExplodeBoard = Board(boardWidth.value,boardHeight.value + 4)
	
	block_pos_x = GameBoard.width // 2 - 1
	block_pos_y = GameBoard.height - 3
	block_fall_progress = 0.0 
	
	if not game_state:
		bombtimer = catalystTimer.value
		
		for x in range(0,GameBoard.width):
			for y in range(0,GameBoard.height - random.randint(8,GameBoard.height - 2)):
				GameBoard[x,y] = generate_tile(catalystchance=True)
			for y in range(GameBoard.height - 4,GameBoard.height):
				if (random.randint(1,2) == 2):
					GameBoard[x,y] = generate_tile(catalystchance=True)
	else:
		bombtimer = -1
	
def isinbounds(x: int, y: int) -> bool: # Checks if the given coordinates are within bounds
	if x < 0 or x >= GameBoard.width or y < 0 or y >= GameBoard.height:
		return False
	else:
		return True

def compare_squares(x: int, y: int, x2: int, y2: int) -> bool: # Checks if two squares are considered "connected" and can be cleared together
	if isinbounds(x,y) and isinbounds(x2,y2):
		if GameBoard[x,y].color == 0 or GameBoard[x2,y2].color == 0:
			return False
		elif GameBoard[x,y].color == GameBoard[x2,y2].color or GameBoard[x,y].color == 1 or GameBoard[x2,y2].color == 1:
			return True
		else:
			return False
	else:
		return False

def find_connected_squares(localInputBoard = GameBoard) -> Board: # Searches through the board and figures out which blocks are connected to catalysts.
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
			if isinbounds(p[0],p[1]) and localInputBoard[p[0],p[1]].special == 0 and (OutputBoard[p[0],p[1]] == 0 or OutputBoard[p[0],p[1]] > OutputBoard[x,y] + 1) and compare_squares(x,y,p[0],p[1]):
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
				
def cascade_board(hard_cascade = False) -> None:
	gravityflag = False
	cascadeflag = False
	for x in range(0,GameBoard.width):
		#First check if anything is wrong in the column
		gravityflag = False # Becomes true when the search finds an empty space
		cascadeflag = False # Becomes true when the search finds a non-empty space above an empty space
		for y in range(0,GameBoard.height):
			
			if gravityflag and GameBoard[x,y].color != 0:
				cascadeflag = True
			elif GameBoard[x,y].color == 0:
				gravityflag = True
		
		#if something is wrong with the column, it will go through each block until it finds empty space, then if it finds blocks above that it will pull them to the first black space it will continue progressively.
		gravityflag = False
		if cascadeflag:
			lastsafe = 0
			for y in range(0,GameBoard.height):
				if GameBoard[x,y].color == 0:
					lastsafe = y
					break
			if hard_cascade:
				for y in range(lastsafe,GameBoard.height):
					if GameBoard[x,y].color != 0:
						GameBoard[x,lastsafe] = GameBoard[x,y].copycell()
						GameBoard[x,y].set(0,0)
						lastsafe += 1
			else:
				for y in range(lastsafe,GameBoard.height):
					if GameBoard[x,y].color != 0:
						GameBoard[x,y-1] = GameBoard[x,y].copycell()
						GameBoard[x,y].set(0,0)

def draw_square(blockID, x: int,y: int,usecolorinstead=False) -> None:
	
	offsetx = leftscreen + (blockSize.value * x)
	offsety = bottomscreen - (blockSize.value * y)
	
	if usecolorinstead or type(blockID) == tuple:
		pygame.draw.rect(window,blockID,
			pygame.Rect((	
				(offsetx, offsety),
				(blockSize.value,blockSize.value))))
	else:
		blockcolor = ColorIndex[blockID.color][0]
		catalystcoloroffset = 8 * ( abs(	(1 * bombtimer + 8 * ConnectedBoard[x,y-1]) % (4*pulseIntensity.value) - (2*pulseIntensity.value)) - pulseIntensity.value ) 
		
		if bombtimer > 0 and ConnectedBoard[x,y-1] > 0:
			blockcolor = change_color_brightness(blockcolor,catalystcoloroffset)
		
		pygame.draw.rect(window,blockcolor,pygame.Rect((	
				(offsetx, bottomscreen - (blockSize.value * y)	),
				(blockSize.value,blockSize.value))))
		
		if blockID.color == 1:
			rainbowcolor = hsv_to_rgb(clock,100,255)
			if blockID.special == 1: 
				rainbowcolor = change_color_brightness(rainbowcolor,catalystcoloroffset)
			
			pygame.draw.rect(window,rainbowcolor,pygame.Rect((	
						(offsetx + 5, bottomscreen - (blockSize.value * y) + 5	),
						(blockSize.value - 10,blockSize.value - 10))))
		
		if blockID.special == 1:
			pygame.draw.circle(window,ColorIndex[blockID.color][1], (offsetx + blockSize.value // 2, bottomscreen - (blockSize.value * y) + blockSize.value // 2 ), blockSize.value // 2 - 5)

def level_up() -> None: # Slightly increases difficulty
	global grace, gravity, level
	grace -= 1
	gravity += 1
	level += 1

def create_block(type="random",color=0,catalyst=False) -> Block:
	global blockssincelastcatalyst
	
	colorsets = []
	for x in range(0,5):
		if random.randint(1,100) <= rainbowChance.value:
			colorsets.append(1)
		else:
			colorsets.append(random.randint(2,numberColors.value + 1))
	piecetype = list(PieceDict[random.choice(PieceWeights) if type == "random" else type])
	
	genblock = [colorsets[piecetype[0]],
					colorsets[piecetype[1]],
					colorsets[piecetype[2]],
					colorsets[piecetype[3]]]
	newblock = Block(Cell(genblock[0]),Cell(genblock[1]),Cell(genblock[2]),Cell(genblock[3]))
	
	if random.randint(1,100) <= catalystChance.value + blockssincelastcatalyst * catalystGuarantee.value:
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
	cascade_board()
	if test_for_death(GameBoard):
		if bombtimer > 0:
			bombtimer = 1
		else:
			game_over()
	reset_block()

def test_for_death(inputBoard = GameBoard) -> bool:
	for x in range(0,inputBoard.width):
		print(GameBoard[x,inputBoard.height - 3])
		if GameBoard[x,inputBoard.height - 3].color != 0:
			return True
	return False

def game_over():
	global game_state
	game_state = False

def rotate_block(block: Block, clockwise = True) -> Block: # 
	"""Takes a Block and rotates it clockwise or counterclockwise, then returns the Block."""
	if clockwise:
		return Block(block[1,0],block[0,0],block[1,1],block[0,1])
	else:
		return Block(block[0,1],block[1,1],block[0,0],block[1,0])

def explode_board() -> None: # This function is kind of unnecessary and should probably be moved to be part of find_connected_squares()
	global score, longestchain, squarescleared, bombssincelastexplosion, ExplodeBoard
	cascade_board(True)
	ExplodeBoard = find_connected_squares(GameBoard)
	previousscores.insert(0,tuple(clear_connected_squares(GameBoard,ExplodeBoard) + tuple([clock])))
	
	bombssincelastexplosion = 0
	
	score += previousscores[0][0]
	squarescleared += previousscores[0][1]
	if longestchain < previousscores[0][2]:
		longestchain = previousscores[0][0]
	if len(previousscores) > 5:
		previousscores.pop(-1)

def global_board_updates() -> None:
	"""This function draws the game."""
	
	global clock, bombtimer, timesinceexplode, ConnectedBoard
	
	clock += 1
	timesinceexplode += 1
	bombtimer -= 1
	
	if clock % 3 == 0:
		cascade_board()
	
	if bombtimer == 0:
		explode_board()
	
	if bombtimer > 0 and bombtimer % 10 == 0:
		ConnectedBoard = find_connected_squares(GameBoard)
	
	if not game_state and bombtimer <= -titleBoardRefresh.value:
		init_board()
		bombtimer = catalystTimer.value

def game_processing() -> None: # Ingame event handling
	"""This function does most of the game's event handling."""
	global keydown, game_state
	global block_pos_x, block_pos_y, grace, block_fall_progress
	global extrablocks, ExplodeBoard, ConnectedBoard
	
	keys = pygame.key.get_pressed()
	
	global_board_updates()
	
	
	
	if keys[K_ESCAPE]:
		game_state = False
	
	if squarescleared > 10 * level:
		level_up()
	
	if keys[K_e]:
		cascade_board(hard_cascade=True)
	
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

def draw_game(explosion=False,fakeboard=False) -> None:
	"""This function draws the game."""
	global textoffset
	
	window.fill(BLACK)
	window.blit(backgroundImage,(0,0))
	
	#Draw the board
	for x in range(0,GameBoard.width):
		for y in range(0,(GameBoard.height - 4) ):
			if GameBoard[x,y] == 0:
				if ExplodeBoard[x,y] != 0:
					
					excolor = hsv_to_rgb(60 - 5 * ExplodeBoard[x,y],10 * ExplodeBoard[x,y],255)
					excolor = change_color_brightness(excolor, 40 * ExplodeBoard[x,y]  - 4 * timesinceexplode)
					
					if sum(excolor) > 40:
						draw_square(excolor,x,y+1,True)
			else:
				draw_square(GameBoard[x,y],x,y+1)
	
	if not fakeboard:
		#Draw Up Next
		if len(extrablocks) > 1:
			for z in range(1,len(extrablocks)):
				for x in range(0,2):
					for y in range(0,2):
						draw_square(extrablocks[z][x,y],x - 3, 18 + y - (3 * z) )
		
		#Draw the active block
		for x in range(0,2):
			for y in range(0,2):
				draw_square(extrablocks[0][x,y],	(x + block_pos_x),	(y + block_pos_y))
	
	#Lines
	for x in range(0,GameBoard.width + 1 ):
		pygame.draw.line(window,WHITE,
			((leftscreen + (blockSize.value * x)),topscreen),
			((leftscreen + (blockSize.value * x)),bottomscreen))
	for y in range(0,GameBoard.height -3):
		pygame.draw.line(window,WHITE,
			(leftscreen,(bottomscreen - (blockSize.value * y))),
			(rightscreen,(bottomscreen - (blockSize.value * y))))
			
	if bombtimer > 0:
		bombline = (GameBoard.height - 4) * blockSize.value * bombtimer // catalystTimer.value
		for x in range(0,GameBoard.width + 1 ):
			pygame.draw.line(window,RED,((leftscreen + (blockSize.value * x)),bottomscreen),((leftscreen + (blockSize.value * x)),bottomscreen - bombline), 3)
		for y in range(0,GameBoard.height -3):
			if bottomscreen - bombline < bottomscreen - (blockSize.value * y):
				pygame.draw.line(window,RED,
					(leftscreen,(bottomscreen - (blockSize.value * y))),
					(rightscreen,(bottomscreen - (blockSize.value * y))),3)
	
		
	if not fakeboard:
		source = (rightscreen, topscreen)
		
		textoffset = 0
		normaltext(f"Level: {level}",WHITE,source)
		normaltext(f"Score: {score}",WHITE,source)
		normaltext(f"Cleared: {squarescleared}",WHITE,source)
		normaltext(f"Longest Chain: {longestchain}",WHITE,source)
		
		for txt in previousscores:
			if txt[3] > clock - 600:
				normaltext(f"+{txt[0]}! {txt[1]} squares! {txt[2]} Chain!",YELLOW,source,SmallerFont)

def menu_processing() -> None:
	"""This function controls the menu."""
	global keys, keydown, game_state, cursor_pos
	
	global_board_updates()
	draw_game(fakeboard=True)
	draw_menu()
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
		match buttonlist[cursor_pos]:
			case "startgame":
				game_state = not game_state
				init_board()
			case "reinitialize":
				init_board()
	
	if isinstance(buttonlist[cursor_pos],Config) and not keydown:
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
	
	buttonlist = []
	menuitemoffset = 0
	textoffset = 0
	
	normaltext("Action Puzzle Game Thing", WHITE, (0,0), False)
	#window.blit(DefaultFont.render("Action Puzzle Game Thing", True, WHITE),(0, 0))
	menutext("Play game","startgame")
	menutext("Game Options",optionsMenu,txtcolornormal=PINK)
	if optionsMenu.value:
		menutext("Refresh Title","reinitialize")
		menutext("Gameplay Options",gameplayMenu,txtcolornormal=GREEN)
		if gameplayMenu.value:
			menutext(f"Starting Level: {startLevel.value}",startLevel)
			menutext(f"Catalyst Chance (%): {catalystChance.value}",catalystChance)
			menutext(f"Grace Period: {gracePeriod.value}",gracePeriod)
			menutext(f"Bomb Timer: {catalystTimer.value}",catalystTimer)
			menutext(f"Rainbow Chance: {rainbowChance.value}",rainbowChance)
		menutext("Board Options",boardMenu,txtcolornormal=GREEN)
		if boardMenu.value:
			menutext(f"Board Width: {boardWidth.value}",boardWidth)
			menutext(f"Board Height: {boardHeight.value}",boardHeight)
			menutext(f"Block Size: {blockSize.value}",blockSize)
			menutext(f"Colors: {numberColors.value}",numberColors)
		menutext("Visual Options",visualsMenu,txtcolornormal=GREEN)
		if visualsMenu.value:
			menutext(f"Title Refresh: {titleBoardRefresh.value}",titleBoardRefresh)
			menutext(f"Pulse Intensity: {pulseIntensity.value}",pulseIntensity)
		
		
	
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

			boardwidth = (blockSize.value * GameBoard.width)
			boardheight = (blockSize.value * ( GameBoard.height - 4) )

			leftscreen = centerx - boardwidth // 2
			rightscreen = centerx + boardwidth // 2
			topscreen = centery - boardheight // 2
			bottomscreen = centery + boardheight // 2

	pygame.display.update()
	fps.tick(60)

pygame.quit()
sys.exit()