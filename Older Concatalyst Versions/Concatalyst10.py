"""
Concatalyst

Code by: Lucina Riley / Kontonkitsune
Last Updated: 22/7/2023

This is an action-puzzle game about making really long chains and then blowing them up.


Bugs:

Bombtimer goes off screen when doing shit



To Do:

High scores

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
	def set(self,color = None, special = None):
		if special != None:
			self.special = special
		if color != None:
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
	"""
	A simple class to allow a variable to have a set minimum, maximum, and scale.
	
	If boolean is set to true, min and max are used instead for cursor memory:
	max: where cursor should go when menu is opened
	min: where cursor should go when menu is closed
	"""
	def __init__(self, value = 0, max = 0, min = 0, scale = 1, boolean = False, needupdate = False):
		self.value = value
		self.max = max
		self.min = min
		self.scale = scale
		self.boolean = boolean
		self.needupdate = needupdate
		
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
		if self.boolean:
			self.value = 1 if value else 0
		else:
			self.value = value
			if self.value < self.min: self.value = self.min
			if self.value > self.max: self.value = self.max
	def override(self,value):
		if self.boolean:
			self.value = 1 if value else 0
		else:
			self.value = value
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
SmallerFont = pygame.font.SysFont("Verdana", 20)

"""--------------Global Variables-------------"""

# General Game State Variables
game_state = "main_menu"
running = True # True while the game is supposed to be open.
keydown = 0 # Timer for how long a useful key has been pressed. Used to make sure single presses can happen.
selectedpreset = "normal"
tutorialsection = 0
supersecretthings = True

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

extraslist = []


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
tutoriallevel = -1


# Physics
block_pos_x = GameBoard.width // 2 - 1
block_pos_y = GameBoard.height - 3
block_fall_progress = 0.0 #to deal with the slower fall speeds

# Timers and Counters
clock = 0 # General ingame timer, used for a lot of stuff.
grace = 100 
catalysttimer = 400
timesinceexplode = 0
blockssincelastcatalyst = 0
catalystssincelastclear = 0
blockssincelastbomb = 0

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
gamemodeMenu = Config(0,1,1,boolean=True)
presetsMenu = Config(0,1,2,boolean=True)
presetsMenuDifficulty = Config(0,3,3,boolean=True)
presetsMenuOther = Config(0,3,4,boolean=True)
configMenu = Config(0,1,3,boolean=True)
configMenuGameplay = Config(0,3,3,boolean=True)
configMenuSpecials = Config(0,3,4,boolean=True)
configMenuSpecialsBombs = Config(0,4,10,boolean=True)
configMenuBoard = Config(0,3,5,boolean=True)
optionsMenu = Config(0,1,4,boolean=True)
tutorialsMenu = Config(0,1,5,boolean=True)

# Visual
blockSize = Config(BLOCK_SIZE,100,10,5) # Block size 
titleBoardRefresh = Config(300,1500,50,50)
drawExtras = Config(1,-1,-1,boolean=True)
connectionType = Config(2,2,0,1)
connectionThickness = Config(5,10,1,1)
pulseIntensity = Config(50,100,5,5)
pulseSpeed = Config(10,30,1,1)
pulseFrequency = Config(50,100,5,5)

# Board
boardHeight = Config(BOARD_SIZE_Y,24,8,1,needupdate=True) # Height of the board
boardWidth = Config(BOARD_SIZE_X,24,4,1,needupdate=True) # Width of the board

testBoardSelection = Config(0,1,0,1) # How 

# Gameplay
startLevel = Config(1,1000,1,1) # Starting level
doLevelUp = Config(1,-1,-1,boolean=True)
squaresPerLevel = Config(20,100,1,1) # How many blocks before a catalyst should be guaranteed (REDUNDANT)
endLevel = Config(100,1000,0,10) # How many blocks before a catalyst should be guaranteed (REDUNDANT)
gracePeriod = Config(100,1000,0,10) # How long a block can idle at the starting position before beginning to fall.

numberColors = Config(5,12,2,1)
rainbowEnable = Config(1,-1,-1,boolean=True)
rainbowChance = Config(10,100,0,1)
bombEnable = Config(0,-1,-1,boolean=True)
trashEnable = Config(0,-1,-1,boolean=True)
trashChance = Config(0,100,1,1)

catalystChance = Config(-5,100,-50,1) # Base chance for any block to be a catalyst
catalystChanceIncrease = Config(5,10,0,1) # How much catalystChance should increase by for every non-catalyst piece
catalystTimer = Config(400,1200,50,50,needupdate=True) # How long between the first catalyst being placed and all catalysts exploding

bombEnable = Config(0,-1,-1,boolean=True)
bombChance = Config(-2,100,-50,1) # Base chance for any block to be a catalyst
bombChanceIncrease = Config(1,10,0,1) # How 
bombRange = Config(4,5,0,1) # How long it takes bombs to go off
bombChain = Config(1,-1,-1,boolean=True) # How long it takes bombs to go off

eraserEnable = Config(1,-1,-1,boolean=True)
eraserChance = Config(5,100,-50,5) # Base chance for any block to be a catalyst
eraserChanceIncrease = Config(0,10,0,1) # How 

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

tutorialboards = (
	((0,0,0,0,0,0,0,0,0,0),
	(0,0,0,0,0,0,0,0,0,0),
	(0,0,0,0,0,0,0,0,0,0),
	(0,0,0,0,0,0,0,0,0,0),
	(0,0,0,0,0,0,0,0,0,0),
	(0,0,0,0,0,0,0,0,0,0),
	(0,0,0,0,0,0,0,0,0,0),
	(0,0,0,0,0,0,0,0,0,0),
	(0,0,0,0,0,0,0,0,0,0),
	(0,0,0,0,0,0,0,0,0,0),
	(0,0,0,0,0,0,0,0,0,0),
	(0,0,0,0,0,0,0,0,0,0),
	(0,0,0,0,0,0,0,0,0,0),
	(2,3,3,0,0,3,0,0,2,2),
	(2,2,2,2,3,3,3,2,2,2),
	(2,2,3,3,3,3,2,2,2,3)),
	
	
	(
	( 0, 0, 0, 0, 0, 0, 0, 0, 0, 0),
	( 0, 0, 0, 0, 0, 0, 0, 0, 0, 0),
	( 0, 0, 0, 0, 0, 0, 0, 0, 0, 0),
	( 0, 0, 0, 0, 0, 0, 0, 0, 0, 0),
	( 0, 0, 0, 0, 0, 0, 0, 0, 0, 0),
	( 0, 0, 0, 0, 0, 0, 0, 0, 0, 0),
	( 0, 0, 0, 0, 0, 0, 0, 0, 0, 3),
	( 3,-1, 0, 3, 3, 3, 3, 0, 3, 3),
	( 1, 3, 3, 3, 3,-1, 3, 3, 3, 3),
	( 1, 1, 3, 4, 4, 2, 3,-1,-1, 4),
	( 1, 1, 4, 4, 4, 4, 4, 4, 4, 4),
	( 1, 4, 4, 1, 1, 2, 4, 4, 2, 2),
	(-1, 4, 4, 1,-1,-1, 2, 3, 3, 2),
	(-1, 3, 3, 3, 3, 2, 2, 2, 2, 2),
	( 3, 3, 3, 3, 1, 1, 2, 2, 1,-1),
	( 1, 3, 3, 1, 1, 1, 1, 1, 1,-1)),
	
	(
	( 0, 0, 0, 0, 0, 0, 0, 0, 0, 0),
	( 0, 0, 0, 0, 0, 0, 0, 0, 0, 0),
	( 0, 0, 0, 0, 0, 0, 0, 0, 0, 0),
	( 0, 0, 0, 0, 0, 0, 0, 0, 0, 0),
	( 0, 0, 0, 0, 0, 0, 0, 0, 0, 0),
	( 0, 0, 0, 0, 0, 0, 0, 0, 0, 0),
	( 0, 0, 0, 0, 0, 0, 0, 0, 0, 0),
	( 0, 0, 0, 0, 0, 0, 0, 0, 0, 0),
	( 0, 0, 0, 0, 0, 0, 0, 0, 0, 0),
	( 0, 0, 0, Square(2,2), Square(3,2), 1, 0, 0, 0, 0),
	( 0, 0, 0, 1, 1, 1, 1, 1, Square(4,2), 0),
	( 2, Square(1,2), 1, 1, 3, 3, 3, 1, 1, 1),
	( 2, 2, 2, 3, 3, 3, 4, 4, 4, 1),
	( 2, 1, 2, 2, 3, 3, 3, 4, 4, 4),
	( 2, 1, 1, 2, 2, 2, 3, 3, 4, 4),
	( 1, 1, 1, 1, 1, 1, 2, 3, 4, 4)),
	
	(
	( 0, 0, 1, Square(4,1), 0, 0, 0, 0, 0, 0),
	( 2, 1, 1,Square(2,1), 0, 0, 1, 1,-1, 4),
	( 2, 2, 1, 1, Square(1,1), 1, 1, 1, 4, 4),
	( 1, 2, 2, 1, Square(1,1), 1, 1, 4, 4, 4),
	( 1, 2, 2, 2, 2, 2, 4, 4, 4, 4),
	( 1, 1, 2, 1,-1, 2, 2, 4, 4, 4),
	(-1, 1, 1, 1, 1, 2, 2,-1, 4, 3),
	( 3,-1, 1, 3, 3, 3, 3, 4, 3, 3),
	( 1, 3, 3, 3, 3,-1, 3, 3, 3, 3),
	( 1, 1, 3, 4, 4, 2, 3,-1,-1, 4),
	( 1, 1, 4, 4, 4, 4, 4, 4, 4, 4),
	( 1, 4, 4, 1, 1, 2, 4, 4, 2, 2),
	(-1, 4, 4, 1,-1,-1, 2, 3, 3, 2),
	(-1, 3, 3, 3, 3, 2, 2, 2, 2, 2),
	( 3, 3, 3, 3, 1, 1, 2, 2, 1,-1),
	( 1, 3, 3, 1, 1, 1, 1, 1, 1,-1)),
	
	(
	( 0, 0, 0, 0, 0, 0, 0, 0, 0, 0),
	( 0, 0, 0, 0, 0, 0, 0, 0, 0, 0),
	( 0, 0, 0, 0, 0, 0, 0, 0, 0, 0),
	( 0, 0, 0, 0, 0, 0, 0, 0, 0, 0),
	( 0, 0, 0, 0, 0, 0, 0, 0, 0, 0),
	( 0, 0, 0, 0, 0, 0, 0, 0, 0, 0),
	( 0, 0, 0, 0, 0, 0, 0, Square(1,1), 0, 0),
	( 0, 0, 0, 0, 0, 0, Square(2,1), Square(1,1), 0, 0),
	( 0, 0, 0, 0, 0, 0, Square(1,1),-2, 3, 0),
	( Square(1,1), Square(3,1), 0, 0, 0, 0,-2,-2, 3, 3),
	( Square(3,1), Square(2,1), 0, 2,-1,-1, 1,-2, 2, 2),
	(-2, 2, 2, 2,-2,-2, 1, 1,-2, 2),
	(-2, 2, 2,-2,-2,-2,-2, 1,-2,-2),
	( 2,-2,-2,-2,-2,-2, 1, 1,-2,-2),
	( 2, 1,-2,-2, 1, 1,-1,-2,-1,-2),
	( 3, 3, 2,-2,-2,-2,-2,-2,-2,-2))
	
	)

testboards = (
	((0,0,0,0,0,0,0,0,0,0),
	(0,0,0,0,0,0,0,0,0,0),
	(0,0,0,0,0,0,0,0,0,0),
	(0,0,0,0,0,0,0,0,0,0),
	(0,0,0,0,0,0,0,0,0,0),
	(0,0,0,0,0,0,0,0,0,0),
	(0,0,0,0,0,0,0,0,0,0),
	(0,0,0,0,0,0,0,0,0,0),
	(0,0,0,0,0,0,0,0,0,0),
	(0,0,0,0,0,0,0,0,0,0),
	(0,0,0,0,0,0,0,0,0,0),
	(0,0,0,0,0,0,0,0,0,0),
	(Square(1,1),0,1,0,1,0,0,0,0,0),
	(Square(1,2),2,2,1,2,0,0,0,0,0),
	(5,6,7,8,9,10,1,2,3,4),
	(1,2,3,4,5,6,7,8,9,10)),
	
	((0,0,0,0,0,0,0,0,0,0),
	(0,0,0,0,0,0,0,0,0,0),
	(0,0,0,0,0,0,0,0,0,0),
	(0,0,0,0,0,0,0,0,0,0),
	(1,2,1,2,1,2,1,2,1,2),
	(2,1,2,1,2,1,2,1,2,1),
	(1,2,1,2,1,2,1,2,1,2),
	(2,1,2,1,2,1,2,1,2,1),
	(1,2,1,2,1,2,1,2,1,2),
	(2,1,2,1,Square(1,1),1,2,1,2,1),
	(1,2,1,2,Square(1,2),2,1,2,1,2),
	(2,1,2,1,2,1,2,1,2,1),
	(1,2,1,2,1,2,1,2,1,2),
	(2,1,2,1,2,1,2,1,2,1),
	(1,2,1,2,1,2,1,2,1,2),
	(2,1,2,1,2,1,2,1,2,1))

	)

"""--------------------Value Functions-------------------------"""


def normalize(value,max,min) -> int: # Ensures a value is between min and max
	"""Ensures a value is between min and max"""
	if min > max:
		temp = min
		min = max
		max = temp
	
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


def generate_square(tiletype=0,special=-1) -> Square: # Generates a tile value
	"""
	Generates a tile value
	
	:tiletype: int. 0 if random, otherwise it will bypass assigning a random color.
	:catalystchance: bool. Whether this tile should have a chance of being a catalyst.
	:catalyst: bool. Whether this tile should be a catalyst.
	"""
	if tiletype == 0:
		if random.randint(0,100) < rainbowChance.value:
			tiletype = -1
		elif trashEnable.value and random.randint(0,100) < trashChance.value:
			tiletype = -2
		else:
			tiletype = (random.randint(1,numberColors.value))
	
	if special == -1:
		if random.randint(1,100) <= catalystChance.value + blockssincelastcatalyst * catalystChanceIncrease.value:
			special = 1
		elif bombEnable.value and random.randint(1,100) <= bombChance.value + blockssincelastbomb * bombChanceIncrease.value:
			special = 2
		else:
			special = 0
	
	tile = Square(tiletype,special)
	return tile

def compare_squares(localGameBoard, x: int, y: int, x2: int, y2: int) -> bool: # Checks if two squares are considered "connected" and can be cleared together. NOT COMMUTATIVE
	if isinbounds(localGameBoard,x,y) and isinbounds(localGameBoard,x2,y2):
		if localGameBoard[x,y].color == 0 or localGameBoard[x2,y2].color == 0 or localGameBoard[x,y].color == -2:
			return False
		elif localGameBoard[x,y].color == localGameBoard[x2,y2].color or localGameBoard[x,y].color == -1 or localGameBoard[x2,y2].color == -1 or localGameBoard[x2,y2].color == -2:
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

def create_block(type="random",color=0,special=-1) -> Block:
	global blockssincelastcatalyst, blockssincelastbomb
	
	colorsets = []
	for x in range(0,5):
		if random.randint(1,100) <= rainbowChance.value:
			colorsets.append(-1)
		if trashEnable.value and random.randint(1,100) <= trashChance.value:
			colorsets.append(-2)
		else:
			colorsets.append(random.randint(1,numberColors.value))
	piecetype = list(PieceDict[random.choice(PieceWeights) if type == "random" else type])
	
	genblock = [colorsets[piecetype[0]],
					colorsets[piecetype[1]],
					colorsets[piecetype[2]],
					colorsets[piecetype[3]]]
	newblock = Block(Square(genblock[0]),Square(genblock[1]),Square(genblock[2]),Square(genblock[3]))
	
	if special == -1:
		if random.randint(1,100) <= catalystChance.value + blockssincelastcatalyst * catalystChanceIncrease.value:
			special = 1
		elif bombEnable.value and random.randint(1,100) <= bombChance.value + blockssincelastbomb * bombChanceIncrease.value:
			special = 2
	
	if special == 1:
		newblock.setspecial(1)
		blockssincelastcatalyst = 0
	else:
		blockssincelastcatalyst += 1
	
	if special == 2:
		newblock.setspecial(2)
		blockssincelastbomb = 0
	else:
		blockssincelastbomb += 1
	
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
	global grace, catalysttimer, catalystssincelastclear
	
	
	
	grace = grace_period
	if extrablocks[0][0,0].special == 1:
		if catalystssincelastclear == 0:
			catalysttimer = catalystTimer.value
		else:
			catalysttimer += catalystTimer.value // (catalystssincelastclear + 1)
			if catalysttimer > catalystTimer.value:
				catalysttimer = catalystTimer.value
		catalystssincelastclear += 1
	
	for x in range(0,2):
		for y in range(0,2):
			GameBoard[block_pos_x + x,block_pos_y + y - 1] = extrablocks[0][x,y]
	cascade_board(GameBoard)
	if test_for_death(GameBoard):
		if catalysttimer > 0:
			catalysttimer = 1
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
		for y in range(0,outputBoard.height - 4):
			if x < len(boardtoload[0]) and y < len(boardtoload):
				thing = boardtoload[outputBoard.height - 5  - y][x]
				if isinstance(thing,Square):
					outputBoard[x,y] = thing.copycell()
				else:
					outputBoard[x,y].set(thing,0)

def init_board() -> None: # Initializes the board
	"""This function initializes the game."""
	
	global GameBoard, ExplodeBoard, ConnectedBoard
	global block_pos_x, block_pos_y, block_fall_progress
	global catalysttimer, blockssincelastcatalyst
	global previousscores
	global grace_period, level, score, squarescleared, longestchain, gravity
	
	resize_board()
	
	grace_period = gracePeriod.value
	level = 1
	score = 0
	gravity = 10
	itvar = 1
	while itvar < startLevel.value:
		level_up()
		itvar += 1
	squarescleared = 0
	longestchain = 0
	previousscores = []
	for x in range(0,MAX_QUEUE_LENGTH):
		extrablocks.append(create_block())
		if len(extrablocks) > MAX_QUEUE_LENGTH:
			extrablocks.pop(0)
	
	blockssincelastcatalyst = 0 if game_state == "game" else 3
	blockssincelastbomb = 0 if game_state == "game" else 3
	
	GameBoard = Board(boardWidth.value,boardHeight.value + 4,1)
	ConnectedBoard = Board(boardWidth.value,boardHeight.value + 4)
	ExplodeBoard = Board(boardWidth.value,boardHeight.value + 4)
	
	block_pos_x = GameBoard.width // 2 - 1
	block_pos_y = GameBoard.height - 3
	block_fall_progress = 0.0 
	
	if game_state == "main_menu":
		catalysttimer = catalystTimer.value
		if GameBoard.width == 10 and GameBoard.height == 20 and random.randint(1,20) == 1:
			load_board(GameBoard,literallythebestboard)
		else:
			for x in range(0,GameBoard.width):
				for y in range(0,GameBoard.height - random.randint(8,GameBoard.height - 2)):
					GameBoard[x,y] = generate_square()
				for y in range(GameBoard.height - 4,GameBoard.height):
					if (random.randint(1,2) == 2):
						GameBoard[x,y] = generate_square()
	else:
		catalysttimer = -1
	ConnectedBoard = find_connected_squares(GameBoard)

def init_concatalyst_board():
	global ConcatalystConnectedBoard
	for y in range(0,len(concatalystboardlayout)):
		for x in range(0,len(concatalystboardlayout[0])):
			ConcatalystTitleBoard[x,y] = Square(concatalystboardlayout[4-y][x])
	ConcatalystTitleBoard[2,4] = Square(2,1)
	ConcatalystConnectedBoard = find_connected_squares(ConcatalystTitleBoard)

def clear_board(board: Board,squares=True) -> None:
	for x in range(0,board.width):
		for y in range(0,board.height):
			if squares:
				board[x,y].set(0,0)
			else:
				board[x,y] = 0

def find_connected_squares(localInputBoard) -> Board: # Searches through the board and figures out which blocks are connected to catalysts.
	"""
	Searches through the board and returns a board of all cells connected to catalysts.
	
	
	"""
	global catalysttimer
	
	OutputBoard = Board(localInputBoard.width,localInputBoard.height)
	stack = []
	
	for x in range(0,localInputBoard.width):
		for y in range(0,localInputBoard.height):
			if localInputBoard[x,y].special == 1:
				if catalysttimer < 0:
					catalysttimer = catalystTimer.value
				OutputBoard[x,y] += 1
				stack.append((x,y))
	
	while len(stack) > 0:
		x = stack[0][0]
		y = stack[0][1]
		stack.pop(0)
		# Catalyst / normal logic
		if isinbounds(localInputBoard,x,y) and localInputBoard[x,y].special == 2:
			connectablelocations = []
			for x2 in range(x - bombRange.value, x + bombRange.value + 1):
				for y2 in range(y - bombRange.value, y + bombRange.value + 1):
					connectablelocations.append((x2,y2))
		else:
			connectablelocations = ((x+1,y),(x-1,y),(x,y+1),(x,y-1))
		
		for p in connectablelocations:
			if isinbounds(localInputBoard,p[0],p[1]) and localInputBoard[p[0],p[1]].special != 1: 
				if (OutputBoard[p[0],p[1]] == 0 or OutputBoard[p[0],p[1]] > OutputBoard[x,y] + 1) and compare_squares(localInputBoard,x,y,p[0],p[1]):
					if bombChain.value or localInputBoard[x,y].special != 2:
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
	global score, longestchain, squarescleared, catalystssincelastclear, ExplodeBoard, updatescreennextframe
	cascade_board(localGameBoard,True)
	ExplodeBoard = find_connected_squares(localGameBoard)
	previousscores.insert(0,tuple(clear_connected_squares(localGameBoard,ExplodeBoard) + tuple([clock])))
	clear_board(ConnectedBoard,False)
	catalystssincelastclear = 0
	
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
	if endLevel.value != 0 and level > endLevel.value:
		game_over(True)

def test_for_death(inputBoard = GameBoard) -> bool:
	for x in range(0,inputBoard.width):
		if GameBoard[x,inputBoard.height - 3].color != 0:
			return True
	return False

def game_over(win=False):
	global game_state, updatescreennextframe
	updatescreennextframe = 2
	if win:
		game_state = "win_menu"
	else:
		game_state = "death_menu"


"""--------------------Graphics Functions-------------------------"""


def draw_concatalyst_board() -> None:
	"""Draws the title screen board"""
	for x in range(0,43):
		for y in range(0,5):
			if ConcatalystTitleBoard[x,y].color:
				draw_square(ConcatalystTitleBoard[x,y],x,y,blocksize=12,source=(40,100),connectedboard=ConcatalystConnectedBoard,gameboard=ConcatalystTitleBoard)
				
	screenupdaterects.append(Rect(38,38,525,64)) # Concatalyst Title Board

def draw_game(explosion=False,fakeboard=False) -> None:
	"""This function draws the game."""
	global textoffset, extraslist
	
	extraslist = []
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
				draw_square(GameBoard[x,y],x,y)
	
	if not fakeboard:
		#Draw Up Next
		if len(extrablocks) > 1:
			for z in range(1,len(extrablocks)):
				for x in range(0,2):
					for y in range(0,2):
						excolor = get_square_color(extrablocks[z][x,y])
						draw_square(extrablocks[z][x,y],x - 3, GameBoard.height - 3 + y - (3 * z),connected=False)
		
		#Draw the active block
		for x in range(0,2):
			for y in range(0,2):
				excolor = get_square_color(extrablocks[0][x,y])
				draw_square(extrablocks[0][x,y],	(x + block_pos_x),	(y + block_pos_y - 1),connected=False)
		
	
	#Lines
	for x in range(0,GameBoard.width + 1 ):
		pygame.draw.line(window,WHITE,
			((leftscreen + (blockSize.value * x)),topscreen),
			((leftscreen + (blockSize.value * x)),bottomscreen))
	for y in range(0,GameBoard.height -3):
		pygame.draw.line(window,WHITE,
			(leftscreen,(bottomscreen - (blockSize.value * y))),
			(rightscreen,(bottomscreen - (blockSize.value * y))))
	
	draw_extras()
	
	if catalysttimer > 0 and catalystTimer.value != 0:
		#operationlength2 = time.perf_counter_ns()
		clearline = (GameBoard.height - 4) * blockSize.value * catalysttimer // catalystTimer.value
		for x in range(0,GameBoard.width + 1 ):
			pygame.draw.line(window,RED,((leftscreen + (blockSize.value * x)),bottomscreen),((leftscreen + (blockSize.value * x)),bottomscreen - clearline), 3)
		for y in range(0,GameBoard.height -3):
			if bottomscreen - clearline < bottomscreen - (blockSize.value * y):
				pygame.draw.line(window,RED,
					(leftscreen,(bottomscreen - (blockSize.value * y))),
					(rightscreen,(bottomscreen - (blockSize.value * y))),3)
	if game_state == "game":
		game_text()
		if tutoriallevel != -1:
			tutorial_text()
	
	
		
	if fakeboard:
		screenupdaterects.append(Rect(leftscreen - blockSize.value,topscreen - blockSize.value,boardwidth + 2 * blockSize.value,boardheight + 2 *blockSize.value))
	else:
		screenupdaterects.append(Rect(leftscreen - 5 - (blockSize.value * 5),topscreen - 5 - (blockSize.value * 3),
								boardwidth + 10+ (blockSize.value * 5),boardheight + 10 + (blockSize.value * 3)))

def get_square_color(square: Square) -> tuple:
	"""Gets the RGB color for a square"""
	if square.color == -1:
		blockcolor = hsv_to_rgb(clock,100,255)
	elif square.color == -2:
		blockcolor = (128,128,128)
	elif square.color > 0 and square.color < len(ColorIndex):
		blockcolor = ColorIndex[square.color]
	else:
		blockcolor = BLACK
		
	
	return blockcolor

def draw_square(square, x: int,y: int, blocksize = 0, connected = True, source=0,connectedboard=0,gameboard=0) -> None:
	"""
	This function draws squares.
	
	:square: Square or tuple[3] (RGB).
	:x: int
	:y: int
	:blocksize: int. what size all blocks should be treated as. Default: blockSize.value.
	:connected: boolean. Whether the block should be considered part of a board. Default: True
	:source: 0 or tuple[2] (position). Origin point for position calculations. Default: (leftscreen,bottomscreen)
	:connectedboard: Board. Default: ConnectedBoard
	:gameboard: Board. Default: GameBoard
	
	"""
	if blocksize == 0:
		blocksize = blockSize.value
	if source:
		squaretopleftx = source[0] + (blocksize * x)
		squaretoplefty = source[1] - (blocksize * (y+1))
		
	else:
		squaretopleftx = leftscreen + (blocksize * x)
		squaretoplefty = bottomscreen - (blocksize * (y+1))
		
	if connectedboard == 0:
		connectedboard = ConnectedBoard
	if gameboard == 0:
		gameboard = GameBoard
		
	if isinstance(square,Square):
		squarecolor = get_square_color(square)
		special = square.special
		rainbow = (square.color == -1)
			
	else:
		squarecolor = square
		special = 0
		connected = False
		rainbow = False
	
	
	
	
	if connectionType.value == 0 and (special == 1 or connected and connectedboard[x,y] > 0):
		
		catalystcoloroffset = pulseIntensity.value * (abs( (( - clock * pulseSpeed.value ) + ( pulseFrequency.value * connectedboard[x,y] )) % 600 - 300) - 150 ) // 150
		squarecolor2 = change_color_brightness(squarecolor,catalystcoloroffset)
	else:
		squarecolor2 = squarecolor
	pygame.draw.rect(window,squarecolor2,pygame.Rect((
					(squaretopleftx, squaretoplefty),
					(blocksize,blocksize))))	
	
	#pygame.draw.circle(window,SILVER, (squaretopleftx, squaretoplefty), blocksize // 4)
	#pygame.draw.line(window,SILVER,(squaretopleftx,squaretoplefty),(squaretopleftx + blocksize,	squaretoplefty + blocksize),	3)
	
	if rainbow:
		rainbowoutlinecolor = SILVER
		match special:
			case 0: rainbowoutlinecolor = SILVER
			case 1: rainbowoutlinecolor = GOLD
		pygame.draw.rect(window,rainbowoutlinecolor,pygame.Rect((
					(squaretopleftx, squaretoplefty),
					(blocksize,blocksize))),blocksize // 6)	
	if special or (connected and connectedboard[x,y] > 0):
		if connectionType.value == 0:
			if special == 1:
					pygame.draw.circle(window,squarecolor, (squaretopleftx + blocksize // 2, squaretoplefty + blocksize // 2 ), blocksize // 2 - 5)
		elif connectionType.value == 1:
			if True:
				excolor = hsv_to_rgb(clock - 5 * connectedboard[x,y],10 * connectedboard[x,y],min(30 * connectedboard[x,y],255))
			else:
				excolor = BLACK
			pygame.draw.line(window,excolor,
				(squaretopleftx + blocksize // 2,	squaretoplefty),
				(squaretopleftx + blocksize // 2,	squaretoplefty + blocksize),		connectionThickness.value)
			pygame.draw.line(window,excolor,
				(squaretopleftx,					squaretoplefty + blocksize // 2),
				(squaretopleftx + blocksize,		squaretoplefty + blocksize // 2),	connectionThickness.value)
			if special == 1:
					pygame.draw.circle(window,BLACK, (squaretopleftx + blocksize // 2, squaretoplefty + blocksize // 2 ), blocksize // 4)
			if special == 2:
				pygame.draw.circle(window,BLACK, (squaretopleftx + blocksize // 2, squaretoplefty + blocksize // 2 ), blocksize // 2 - 5,3)
				if connected and connectedboard[x,y] > 0:
					extraslist.append((gameboard[x,y],x,y,connectedboard[x,y]))
		
		elif connectionType.value == 2:
			if special == 1:
					pygame.draw.circle(window,BLACK, (squaretopleftx + blocksize // 2, squaretoplefty + blocksize // 2 ), blocksize // 4)
			if special == 2:
				excolor = hsv_to_rgb(clock - 5 * connectedboard[x,y],10 * connectedboard[x,y],min(30 * connectedboard[x,y],255))
				pygame.draw.circle(window,excolor, (squaretopleftx + blocksize // 2, squaretoplefty + blocksize // 2 ), blocksize // 2 - 5,3)
				if drawExtras.value and connected and connectedboard[x,y] > 0:
					extraslist.append((gameboard[x,y],x,y,connectedboard[x,y]))
			isolatedsquare = True
			for p in ((-1,0),(0,-1)):
				if (connected and connectedboard[x,y] > 0) and isinbounds(gameboard,x + p[0],y + p[1]) and compare_squares(gameboard,x,y,x+p[0],y+p[1]):
					isolatedsquare = False					
					if True:
						excolor = hsv_to_rgb(clock - 5 * connectedboard[x,y],10 * connectedboard[x,y],min(30 * connectedboard[x,y],255))
					else:
						excolor = BLACK
					pygame.draw.line(window,excolor,	(squaretopleftx + blocksize // 2,	squaretoplefty + blocksize // 2),(squaretopleftx + blocksize // 2 + p[0] * blocksize,	squaretoplefty + blocksize // 2 - p[1] * blocksize),connectionThickness.value)
			for p in ((1,0),(0,1)):
				if (connected and connectedboard[x,y] > 0) and isinbounds(gameboard,x + p[0],y + p[1]) and compare_squares(gameboard,x,y,x+p[0],y+p[1]):
					isolatedsquare = False
			if isolatedsquare and special == 0:
				if True:
					excolor = hsv_to_rgb(clock - 5 * connectedboard[x,y],10 * connectedboard[x,y],min(30 * connectedboard[x,y],255))
				else:
					excolor = BLACK
				pygame.draw.circle(window,excolor, (squaretopleftx + blocksize // 2, squaretoplefty + blocksize // 2 ), connectionThickness.value // 2 + 1)

def draw_extras():
	blocksize = blockSize.value
	
	
	
	if drawExtras.value:
		for z in extraslist:
			x = z[1]
			y = z[2]
			if z[0].special == 2:
				squaresize = blocksize * (1 + 2 * bombRange.value)
				
				squaretopleftx = leftscreen + (blocksize * x) - (bombRange.value * blocksize)
				squarebottomrightx = squaretopleftx + squaresize
				squaretopleftx = normalize(squaretopleftx, leftscreen, rightscreen)
				squarebottomrightx = normalize(squarebottomrightx, leftscreen, rightscreen)
				
				squaretoplefty = bottomscreen - (blocksize * (y+1)) - (bombRange.value * blocksize)
				squarebottomrighty = squaretoplefty + squaresize
				squaretoplefty = normalize(squaretoplefty, topscreen, bottomscreen)
				squarebottomrighty = normalize(squarebottomrighty, topscreen, bottomscreen)
				
				squaresizex = squarebottomrightx - squaretopleftx
				squaresizey = squarebottomrighty - squaretoplefty
				
				excolor = hsv_to_rgb(clock - 5 * z[3],10 * z[3],min(30 * z[3],255))
				pygame.draw.rect(window,excolor,pygame.Rect((
							(squaretopleftx, squaretoplefty),
							(squaresizex,squaresizey))),connectionThickness.value)	
			


"""--------------------Game State Functions-------------------------"""

def resize_board() -> None: # Initializes variables to config values
	"""Basically just makes sure variables are set to what they need to be (for config settings and such)"""
	global boardwidth, boardheight, leftscreen, rightscreen, topscreen, bottomscreen, updatescreennextframe
	
	
	boardwidth = blockSize.value * boardWidth.value
	boardheight = blockSize.value * boardHeight.value

	leftscreen = centerx - boardwidth // 2 if game_state == "game" else centerx
	rightscreen = centerx + boardwidth // 2 if game_state == "game" else centerx + boardwidth
	topscreen = centery - boardheight // 2
	bottomscreen = centery + boardheight // 2
	
	updatescreennextframe = 2

def global_board_updates() -> None:
	"""This is a function. It does stuff"""
	
	global clock, catalysttimer, timesinceexplode, ConnectedBoard
	
	clock += 1
	timesinceexplode += 1
	catalysttimer -= 1
	
	if clock % 3 == 0:
		cascade_board(GameBoard)
	
	if catalysttimer == 0:
		explode_board(GameBoard)
	
	if catalysttimer > 0 and catalysttimer % 10 == 0:
		ConnectedBoard = find_connected_squares(GameBoard)
	
	if game_state == "main_menu" and catalysttimer <= -titleBoardRefresh.value:
		init_board()
		catalysttimer = catalystTimer.value

def global_controls() -> None:
	global keydown, game_state, updatescreennextframe
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
	
	
	if doLevelUp.value and squarescleared > squaresPerLevel.value * level:
		level_up()
	
	if keys[K_LSHIFT]:
		cascade_board(GameBoard,hard_cascade=True)
	
	outofbounds = (block_pos_y < 1 or block_pos_y > GameBoard.height - 3 or block_pos_x < 0 or block_pos_x >= GameBoard.width - 1) 
	if grace <= 0:
		block_fall_progress += gravity
		if block_fall_progress > 1000:
			if outofbounds or GameBoard[block_pos_x,block_pos_y - 2] == 0 and GameBoard[block_pos_x + 1,block_pos_y - 2] == 0 and block_pos_y >= 2:
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
	global keys, keydown, game_state, cursor_pos, updatescreennextframe, screenupdaterects, clock, selectedpreset, tutoriallevel
	global catalysttimer
	
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
		game_over_menu_text()
	elif game_state == "win_menu":
		game_over_menu_text(True)
	 # Display Board
	
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
	if (keys[K_z]) and not keydown: # This should really be its own function
		updatescreennextframe = 2
		match buttonlist[cursor_pos]:
			case "startgamestandard":
				game_state = "game"
				tutoriallevel = -1
				init_board()
				doLevelUp.set(1)
				if endLevel.value == 0:
					endLevel.set(100)
				
			case "startgameendless":
				game_state = "game"
				init_board()
				tutoriallevel = -1
				endLevel.set(0)
			case "singlelevelendless":
				game_state = "game"
				init_board()
				tutoriallevel = -1
				doLevelUp.set(0)
			case "usethatoneboard":
				game_state = "game"
				tutoriallevel = -1
				init_board()
				load_board(GameBoard,literallythebestboard)
				catalysttimer = catalystTimer.value
			case "usetestboard":
				game_state = "game"
				tutoriallevel = -1
				init_board()
				load_board(GameBoard,testboards[testBoardSelection.value])
				catalysttimer = catalystTimer.value
			case "reinitialize":
				init_board()
			case "restartgame":
				game_state = "game"
				init_board()
			case "continuegame":
				game_state = "game"
			case "continueendless":
				game_state = "game"
				endLevel.set(0)
			case "tomainmenu":
				game_state = "main_menu"
			case "tutorialbasic":
				game_state = "game"
				selectedpreset = "tutorialbasic"
				apply_preset("tutorialbasic")
				tutoriallevel = 0
				init_board()
				#load_board(GameBoard,tutorialboards[0])
			case "tutorialcatalysts":
				game_state = "game"
				selectedpreset = "tutorialcatalysts"
				apply_preset("tutorialcatalysts")
				tutoriallevel = 1
				init_board()
			case "tutorialrainbow":
				game_state = "game"
				selectedpreset = "tutorialrainbow"
				apply_preset("tutorialrainbow")
				tutoriallevel = 2
				init_board()
				load_board(GameBoard,tutorialboards[0])
			case "tutorialcombo":
				game_state = "game"
				selectedpreset = "tutorialcombo"
				apply_preset("tutorialcombo")
				tutoriallevel = 3
				init_board()
				load_board(GameBoard,tutorialboards[1])
			case "tutorialbombs":
				game_state = "game"
				selectedpreset = "tutorialbombs"
				apply_preset("tutorialbombs")
				tutoriallevel = 4
				init_board()
				load_board(GameBoard,tutorialboards[2])
			case "tutorialhardcascadeandmercy":
				game_state = "game"
				selectedpreset = "tutorialhardcascadeandmercy"
				apply_preset("tutorialhardcascadeandmercy")
				tutoriallevel = 5
				init_board()
				load_board(GameBoard,tutorialboards[3])
				catalysttimer = catalystTimer.value
			case "tutorialtrash":
				game_state = "game"
				selectedpreset = "tutorialtrash"
				apply_preset("tutorialtrash")
				tutoriallevel = 6
				init_board()
				load_board(GameBoard,tutorialboards[4])
				catalysttimer = catalystTimer.value
			case other:
				if type(buttonlist[cursor_pos]) == str and buttonlist[cursor_pos] != "null":
					apply_preset(buttonlist[cursor_pos])
					selectedpreset = buttonlist[cursor_pos]
		
	if cursor_pos > len(buttonlist) - 1:
		cursor_pos = len(buttonlist) - 1
	if isinstance(buttonlist[cursor_pos],Config) and not keydown:
		updatescreennextframe = 2
		if buttonlist[cursor_pos].boolean:
			if keys[K_z] or keys[K_RIGHT] or keys[K_LEFT]:
				buttonlist[cursor_pos].toggle()
				if buttonlist[cursor_pos].needupdate:
					init_board()
				if buttonlist[cursor_pos].value:
					if buttonlist[cursor_pos].max != -1: cursor_pos = buttonlist[cursor_pos].max
				else:
					if buttonlist[cursor_pos].min != -1: cursor_pos = buttonlist[cursor_pos].min
		else:
			if keys[K_RIGHT]: 
				buttonlist[cursor_pos].increment()
				selectedpreset = "custom"
				if buttonlist[cursor_pos].needupdate:
					init_board()
			if keys[K_LEFT]:
				buttonlist[cursor_pos].decrement()
				selectedpreset = "custom"
				if buttonlist[cursor_pos].needupdate:
					init_board()
		
	if keys[K_UP] or keys[K_DOWN] or keys[K_RIGHT] or keys[K_LEFT] or keys[K_z] or keys[K_x] or keys[K_c]:
		keydown += 1
		if keydown > 10:
			keydown = 0
	else:
		keydown = 0

def apply_preset(preset) -> None:
	"""Sets config options to certain values"""
	match preset:
	
		# ------------------ Difficulty Presets----------------
		
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
		
		# ------------------ Fun Presets ----------------
		
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
			
		# ------------------ Tutorials ----------------
		
		case "tutorialbasic":
			startLevel.set(1)
			doLevelUp.set(0)
			boardHeight.set(16)
			boardWidth.set(10)
			numberColors.set(2)
			gracePeriod.set(150) 
			rainbowChance.set(-100)
			catalystChance.set(-25) 
			catalystChanceIncrease.set(25) 
			catalystTimer.set(100)
			trashEnable.set(0)
			bombEnable.set(0)
		case "tutorialcatalysts":
			startLevel.set(1)
			doLevelUp.set(0)
			boardHeight.set(16)
			boardWidth.set(10)
			numberColors.set(2)
			gracePeriod.set(150) 
			rainbowChance.set(-100)
			catalystChance.set(25) 
			catalystChanceIncrease.set(50) 
			catalystTimer.set(200)
			trashEnable.set(0)
			bombEnable.set(0)
		case "tutorialrainbow":
			startLevel.set(1)
			doLevelUp.set(0)
			boardHeight.set(16)
			boardWidth.set(10)
			numberColors.set(3)
			gracePeriod.set(150) 
			rainbowChance.set(25)
			catalystChance.set(10)
			catalystChanceIncrease.set(10) 
			catalystTimer.set(400)
			trashEnable.set(0)
			bombEnable.set(0)
		case "tutorialcombo":
			startLevel.set(1)
			doLevelUp.set(0)
			boardHeight.set(16)
			boardWidth.set(10)
			numberColors.set(4)
			gracePeriod.set(150)
			rainbowChance.set(15)
			catalystChance.set(0)
			catalystChanceIncrease.set(10) 
			catalystTimer.set(400)
			trashEnable.set(0)
			bombEnable.set(0)
		case "tutorialbombs":
			startLevel.set(1)
			doLevelUp.set(0)
			boardHeight.set(16)
			boardWidth.set(10)
			numberColors.set(4)
			gracePeriod.set(150)
			rainbowChance.set(5)
			catalystChance.set(0)
			catalystChanceIncrease.set(10) 
			catalystTimer.set(200)
			trashEnable.set(0)
			bombEnable.set(1)
			bombChance.set(0)
			bombChanceIncrease.set(5)
			bombRange.set(4)
			bombChain.set(1)
		case "tutorialhardcascadeandmercy":
			startLevel.set(1)
			doLevelUp.set(0)
			boardHeight.set(16)
			boardWidth.set(10)
			numberColors.set(4)
			gracePeriod.set(150)
			rainbowChance.set(15)
			catalystChance.set(0)
			catalystChanceIncrease.set(10) 
			catalystTimer.set(1200)
			bombEnable.set(0)
		case "tutorialtrash":
			startLevel.set(1)
			doLevelUp.set(0)
			boardHeight.set(16)
			boardWidth.set(10)
			numberColors.set(4)
			gracePeriod.set(150)
			rainbowChance.set(15)
			catalystChance.set(0)
			catalystChanceIncrease.set(10) 
			catalystTimer.set(400)
			trashEnable.set(1)
			trashChance.set(5)
			bombEnable.set(1)
			bombChance.set(0)
			bombChanceIncrease.set(2)
			bombRange.set(4)
			bombChain.set(1)

"""--------------------Text and GUI Functions-------------------------"""


def game_text() -> None:
	global textoffset, updatescreennextframe
	source = (rightscreen + 5, topscreen)
	
	textoffset = 0
	normaltext(f"Level: {level}",WHITE,source)
	normaltext(f"Score: {score:,}",WHITE,source)
	normaltext(f"Cleared: {squarescleared:,}",WHITE,source)
	normaltext(f"Longest Chain: {longestchain}",WHITE,source)
	source = (rightscreen + 5, topscreen + 150)
	for txt in previousscores:
		diff = clock - txt[3]
		if diff < 600:
			normaltext(f"+{txt[0]:,} points!",hsv_to_rgb(60-(diff*txt[0]//60000),(diff*txt[0]//60000),255),source,font=SmallerFont,fontsize=20)
			normaltext(f"+{txt[1]} squares!",hsv_to_rgb(60-(diff*txt[1]//120),(diff*txt[1]//300),255),source,font=SmallerFont,fontsize=20)
			normaltext(f"{txt[2]} chain!",hsv_to_rgb(60-(diff*txt[2]//120),(diff*txt[2]//120),255),source,font=SmallerFont,fontsize=20)
		elif diff == 600:
			updatescreennextframe = 2

def main_menu_text() -> None: # Draws the menu
	global buttonlist, menuitemoffset, window, textoffset
	
	buttonlist = []
	menuitemoffset = 0
	textoffset = 0
	nestlevel = 0
	menutext("Play Game","startgamestandard",txtcolornormal=GREEN)
	if gamemodeMenu.value:
		menutext("Game Modes",gamemodeMenu,txtcolornormal=PINK)
		nestlevel += 1
		menutext(f"Start Level: {startLevel.value}",startLevel,depth=nestlevel)
		menutext("Standard","startgamestandard",txtcolornormal=GREEN,depth=nestlevel)
		menutext("Endless","startgameendless",txtcolornormal=GREEN,depth=nestlevel)
		menutext("Single Level","singlelevelendless",txtcolornormal=GREEN,depth=nestlevel)
	elif presetsMenu.value:
		menutext("Game Presets",presetsMenu,txtcolornormal=PINK)
		nestlevel += 1
		menutext(f"Preset: {selectedpreset}",depth=nestlevel)
		if presetsMenuDifficulty.value:
			menutext("Difficulty Presets",presetsMenuDifficulty,txtcolornormal=BLUE,depth=nestlevel)
			nestlevel += 1
			menutext("Casual","casual",txtcolornormal=ROSEGOLD if selectedpreset == "casual" else WHITE,depth=nestlevel)
			menutext("Easy","easy",txtcolornormal=ROSEGOLD if selectedpreset == "easy" else WHITE,depth=nestlevel)
			menutext("Normal","normal",txtcolornormal=ROSEGOLD if selectedpreset == "normal" else WHITE,depth=nestlevel)
			menutext("Hard","hard",txtcolornormal=ROSEGOLD if selectedpreset == "hard" else WHITE,depth=nestlevel)
			menutext("Extreme","extreme",txtcolornormal=ROSEGOLD if selectedpreset == "extreme" else WHITE,depth=nestlevel)
			menutext("Absurd","absurd",txtcolornormal=ROSEGOLD if selectedpreset == "absurd" else WHITE,depth=nestlevel)
		elif presetsMenuOther.value:
			menutext("Other Presets",presetsMenuOther,txtcolornormal=BLUE,depth=nestlevel)
			nestlevel += 1
			menutext("More Space More Problems","morespacemoreproblems",txtcolornormal=ROSEGOLD if selectedpreset == "morespacemoreproblems" else WHITE,depth=nestlevel)
		else:
			
			menutext("Difficulty Presets",presetsMenuDifficulty,txtcolornormal=BLUE,depth=nestlevel)
			menutext("Other Presets",presetsMenuOther,txtcolornormal=BLUE,depth=nestlevel)
		
	elif configMenu.value:
		menutext("Game Configuration",configMenu,txtcolornormal=PINK,depth=nestlevel)
		nestlevel += 1
		menutext("Refresh Title","reinitialize",depth=nestlevel)
		if configMenuGameplay.value:
			menutext("Gameplay Options",configMenuGameplay,txtcolornormal=BLUE,depth=nestlevel)
			nestlevel += 1
			menutext(f"Level Increase: {'On' if doLevelUp.value else 'Off'}",doLevelUp,depth=nestlevel,txtcolornormal=CYAN)
			if doLevelUp.value:
				menutext(f"Blocks per Level: {squaresPerLevel.value}",squaresPerLevel,depth=nestlevel+1)
				menutext(f"Ending level: {endLevel.value}",endLevel,depth=nestlevel+1)
			menutext(f"Grace Period: {gracePeriod.value}",gracePeriod,depth=nestlevel)
			menutext(f"Colors: {numberColors.value}",numberColors,depth=nestlevel)
		elif configMenuSpecials.value:
			menutext("Specials Config",configMenuSpecials,txtcolornormal=BLUE,depth=nestlevel)
			nestlevel += 1
			if configMenuSpecialsBombs.value:
				menutext("Bombs",configMenuSpecialsBombs,txtcolornormal=RED,depth=nestlevel)
				nestlevel += 1
				menutext(f"Bombs: {'On' if bombEnable.value else 'Off'}",bombEnable,depth=nestlevel)
				menutext(f"Bomb Chance (%): {bombChance.value}",bombChance,depth=nestlevel)
				menutext(f"+ Bomb Chance (%): {bombChanceIncrease.value}",bombChanceIncrease,depth=nestlevel)
				menutext(f"Bomb Range: {bombRange.value}",bombRange,depth=nestlevel)
				menutext(f"Bomb Chain: {'On' if bombChain.value else 'Off'}",bombChain,depth=nestlevel)
			else:
				menutext(f"Rainbow Chance: {rainbowChance.value}",rainbowChance,depth=nestlevel)
				menutext(f"Trash: {'On' if trashEnable.value else 'Off'}",trashEnable,depth=nestlevel)
				menutext(f"Trash Chance: {trashChance.value}",trashChance,depth=nestlevel)
				menutext(f"Catalyst Chance (%): {catalystChance.value}",catalystChance,depth=nestlevel)
				menutext(f"+ Cat Chance (%): {catalystChanceIncrease.value}",catalystChanceIncrease,depth=nestlevel)
				menutext(f"Catalyst Timer: {catalystTimer.value}",catalystTimer,depth=nestlevel)
				menutext("Bombs",configMenuSpecialsBombs,txtcolornormal=RED,depth=nestlevel)
			
			
			
		elif configMenuBoard.value:
			menutext("Board Config",configMenuBoard,txtcolornormal=BLUE,depth=nestlevel)
			nestlevel += 1
			menutext(f"Board Width: {boardWidth.value}",boardWidth,depth=nestlevel)
			menutext(f"Board Height: {boardHeight.value}",boardHeight,depth=nestlevel)
		else:
			menutext("Basic Config",configMenuGameplay,txtcolornormal=BLUE,depth=nestlevel)
			menutext("Specials Config",configMenuSpecials,txtcolornormal=BLUE,depth=nestlevel)
			menutext("Board Config",configMenuBoard,txtcolornormal=BLUE,depth=nestlevel)
	elif optionsMenu.value:
		menutext("Options",optionsMenu,txtcolornormal=PINK,depth=nestlevel)
		nestlevel += 1
		menutext(f"Block Size: {blockSize.value}",blockSize,depth=nestlevel)
		menutext(f"Title Refresh: {titleBoardRefresh.value}",titleBoardRefresh,depth=nestlevel)
		menutext(f"Draw Extra things: {'On' if drawExtras.value else 'Off'}",drawExtras,depth=nestlevel)
		match connectionType.value:
			case 0: style = "Pulse"
			case 1: style = "Cross"
			case 2: style = "Lines"
		menutext(f"Connection Style: {style}",connectionType,depth=nestlevel,txtcolornormal=CYAN)
		if connectionType.value == 0:
			menutext(f"Pulse Intensity: {pulseIntensity.value}",pulseIntensity,depth=nestlevel+1)
			menutext(f"Pulse Frequency: {pulseFrequency.value}",pulseFrequency,depth=nestlevel+1)
			menutext(f"Pulse Speed: {pulseSpeed.value}",pulseSpeed,depth=nestlevel+1)
		else:
			menutext(f"Line Thickness: {connectionThickness.value}",connectionThickness,depth=nestlevel+1)
	elif tutorialsMenu.value:
		menutext("Tutorials",tutorialsMenu,txtcolornormal=PINK)
		nestlevel += 1
		menutext("Basic","tutorialbasic",txtcolornormal=GREEN,depth=nestlevel)
		menutext("Catalysts","tutorialcatalysts",txtcolornormal=GREEN,depth=nestlevel)
		menutext("Rainbow Squares","tutorialrainbow",txtcolornormal=GREEN,depth=nestlevel)
		menutext("Combos","tutorialcombo",txtcolornormal=GREEN,depth=nestlevel)
		menutext("Bombs","tutorialbombs",txtcolornormal=GREEN,depth=nestlevel)
		menutext("Hard Cascade/Mercy","tutorialhardcascadeandmercy",txtcolornormal=GREEN,depth=nestlevel)
		menutext("Trash Squares","tutorialtrash",txtcolornormal=GREEN,depth=nestlevel)
	else:
		menutext("Game Modes",gamemodeMenu,txtcolornormal=PINK)
		menutext("Game Presets",presetsMenu,txtcolornormal=PINK)
		menutext("Game Configuration",configMenu,txtcolornormal=PINK)
		menutext("Options",optionsMenu,txtcolornormal=PINK)
		menutext("Tutorials",tutorialsMenu,txtcolornormal=PINK)
	
	if supersecretthings:
		menutext("Load max board (DEBUG)","usethatoneboard",txtcolornormal=GREEN)
		menutext(f"Test board #: {testBoardSelection.value}",testBoardSelection)
		menutext("Load test board (DEBUG)","usetestboard",txtcolornormal=GREEN)
		
	#-------------Tooltips
	
	if len(buttonlist) > cursor_pos and buttonlist[cursor_pos] is connectionType:
		normaltext("How connected squares", YELLOW, (50,700), True,font=SmallerFont,fontsize=20)
		normaltext("should be drawn.", YELLOW, (50,700), True,font=SmallerFont,fontsize=20)
	if len(buttonlist) > cursor_pos and buttonlist[cursor_pos] is bombChain:
		normaltext("Whether bombs are allowed to", YELLOW, (50,700), True,font=SmallerFont,fontsize=20)
		normaltext("continue chains or if they can", YELLOW, (50,700), True,font=SmallerFont,fontsize=20)
		normaltext("only remove nearby blocks.", YELLOW, (50,700), True,font=SmallerFont,fontsize=20)
	if len(buttonlist) > cursor_pos and buttonlist[cursor_pos] is catalystTimer:
		normaltext("The time between the first", YELLOW, (50,700), True,font=SmallerFont,fontsize=20)
		normaltext("catalyst being placed and", YELLOW, (50,700), True,font=SmallerFont,fontsize=20)
		normaltext("all catalysts exploding.", YELLOW, (50,700), True,font=SmallerFont,fontsize=20)
	if len(buttonlist) > cursor_pos and buttonlist[cursor_pos] is gracePeriod:
		normaltext("How long before the block", YELLOW, (50,700), True,font=SmallerFont,fontsize=20)
		normaltext("is affected by gravity", YELLOW, (50,700), True,font=SmallerFont,fontsize=20)
	if len(buttonlist) > cursor_pos and buttonlist[cursor_pos] is catalystChanceIncrease:
		normaltext("How much the catalyst chance", YELLOW, (50,700), True,font=SmallerFont,fontsize=20)
		normaltext("should increase by for every", YELLOW, (50,700), True,font=SmallerFont,fontsize=20)
		normaltext("non-catalyst block recieved.", YELLOW, (50,700), True,font=SmallerFont,fontsize=20)
	if len(buttonlist) > cursor_pos and buttonlist[cursor_pos] is bombChanceIncrease:
		normaltext("How much the bomb chance", YELLOW, (50,700), True,font=SmallerFont,fontsize=20)
		normaltext("should increase by for every", YELLOW, (50,700), True,font=SmallerFont,fontsize=20)
		normaltext("non-bomb block recieved.", YELLOW, (50,700), True,font=SmallerFont,fontsize=20)
	if len(buttonlist) > cursor_pos and buttonlist[cursor_pos] is titleBoardRefresh:
		normaltext("How long to wait after an", YELLOW, (50,700), True,font=SmallerFont,fontsize=20)
		normaltext("explosion before resetting", YELLOW, (50,700), True,font=SmallerFont,fontsize=20)
		normaltext("the board (Main Menu).", YELLOW, (50,700), True,font=SmallerFont,fontsize=20)

def pause_menu_text() -> None: # Draws the menu
	global buttonlist, menuitemoffset, window, textoffset
	
	game_text()
	buttonlist = []
	menuitemoffset = 0
	textoffset = 0
	
	normaltext("Game paused.", YELLOW, (50,50), False)
	menutext("Continue","continuegame")
	if tutoriallevel == -1:
		menutext("Restart","restartgame")
	else:
		match tutoriallevel:
			case 0:
				menutext("Restart","tutorialbasic")
				menutext("Next tutorial","tutorialcatalysts")
			case 1:
				menutext("Restart","tutorialcatalysts")
				menutext("Next tutorial","tutorialrainbow")
				menutext("Previous tutorial","tutorialbasic")
			case 2:
				menutext("Restart","tutorialrainbow")
				menutext("Next tutorial","tutorialcombo")
				menutext("Previous tutorial","tutorialcatalysts")
			case 3:
				menutext("Restart","tutorialcombo")
				menutext("Next tutorial","tutorialbombs")
				menutext("Previous tutorial","tutorialrainbow")
			case 4:
				menutext("Restart","tutorialbombs")
				menutext("Next tutorial","tutorialhardcascadeandmercy")
				menutext("Previous tutorial","tutorialcombo")
			case 5:
				menutext("Restart","tutorialhardcascadeandmercy")
				menutext("Next tutorial","tutorialtrash")
				menutext("Previous tutorial","tutorialbombs")
			case 6:
				menutext("Restart","tutorialtrash")
				#menutext("Next tutorial","tutorialhardcascadeandmercy")
				menutext("Previous tutorial","tutorialhardcascadeandmercy")
				
	menutext("Main Menu","tomainmenu")

def game_over_menu_text(win=False) -> None: # Draws the menu
	global buttonlist, menuitemoffset, window, textoffset
	
	buttonlist = []
	menuitemoffset = 0
	textoffset = 0
	
	if win: normaltext("Game clear!", GREEN, (50,150), False)
	else: normaltext("Game over!", RED, (50,150), False)
	normaltext(f"Score: {score:,}!", YELLOW, (50,30), True)
	normaltext(f"Squares Cleared: {squarescleared:,}!", YELLOW, (50,30), True)
	normaltext(f"Longest Chain: {longestchain}!", YELLOW, (50,30), True)
	if win: menutext("Continue in Endless","continueendless",source=(50,200))
	if tutoriallevel != -1:
		menutext("Restart",selectedpreset,source=(50,200))
	else:
		menutext("Restart","restartgame",source=(50,200))
	menutext("Main Menu","tomainmenu",source=(50,200))

def tutorial_text() -> None: # Draws the menu
	global buttonlist, menuitemoffset, window, textoffset
	
	buttonlist = []
	textoffset = 0
	match tutoriallevel:
		case 0:
			normaltext("Basic Tutorial", YELLOW, (50,30), False)
			normaltext("Controls", PINK, (50,150), True,font=SmallerFont,fontsize=20)
			normaltext("Arrow Keys to move", WHITE, (50,150), True,font=SmallerFont,fontsize=20)
			normaltext("Z/X to rotate the block", WHITE, (50,150), True,font=SmallerFont,fontsize=20)
			normaltext("UP to drop a piece", WHITE, (50,150), True,font=SmallerFont,fontsize=20)
			normaltext("ESCAPE to pause", WHITE, (50,150), True,font=SmallerFont,fontsize=20)
			normaltext("", WHITE, (50,150), True,font=SmallerFont,fontsize=20)
			normaltext("Game Over:", PINK, (50,150), True,font=SmallerFont,fontsize=20)
			normaltext("Don't let your stack", WHITE, (50,150), True,font=SmallerFont,fontsize=20)
			normaltext("reach the top or it's", WHITE, (50,150), True,font=SmallerFont,fontsize=20)
			normaltext("game over.", WHITE, (50,150), True,font=SmallerFont,fontsize=20)
			normaltext("", WHITE, (50,150), True,font=SmallerFont,fontsize=20)
			normaltext("Catalysts:", PINK, (50,150), True,font=SmallerFont,fontsize=20)
			normaltext("Catalysts will clear all", WHITE, (50,150), True,font=SmallerFont,fontsize=20)
			normaltext("connected blocks of the", WHITE, (50,150), True,font=SmallerFont,fontsize=20)
			normaltext("same color.", WHITE, (50,150), True,font=SmallerFont,fontsize=20)
			normaltext("", WHITE, (50,150), True,font=SmallerFont,fontsize=20)
			normaltext("Chains:", PINK, (50,150), True,font=SmallerFont,fontsize=20)
			normaltext("Connect many squares", WHITE, (50,150), True,font=SmallerFont,fontsize=20)
			normaltext("of the same color", WHITE, (50,150), True,font=SmallerFont,fontsize=20)
			normaltext("and use catalysts", WHITE, (50,150), True,font=SmallerFont,fontsize=20)
			normaltext("to clear them!", WHITE, (50,150), True,font=SmallerFont,fontsize=20)
		case 1:
			normaltext("Catalyst Tutorial", YELLOW, (50,30), False)
			normaltext("Catalyst Explosion:", PINK, (50,150), True,font=SmallerFont,fontsize=20)
			normaltext("When the red lines leave", WHITE, (50,150), True,font=SmallerFont,fontsize=20)
			normaltext("the bottom of the screen,", WHITE, (50,150), True,font=SmallerFont,fontsize=20)
			normaltext("all catalysts explode,", WHITE, (50,150), True,font=SmallerFont,fontsize=20)
			normaltext("clearing connected squares.", WHITE, (50,150), True,font=SmallerFont,fontsize=20)
			normaltext("", WHITE, (50,150), True,font=SmallerFont,fontsize=20)
			normaltext("Timer Extension:", PINK, (50,150), True,font=SmallerFont,fontsize=20)
			normaltext("Placing another catalyst", WHITE, (50,150), True,font=SmallerFont,fontsize=20)
			normaltext("will increase the time", WHITE, (50,150), True,font=SmallerFont,fontsize=20)
			normaltext("until they explode.", WHITE, (50,150), True,font=SmallerFont,fontsize=20)
			normaltext("", WHITE, (50,150), True,font=SmallerFont,fontsize=20)
			normaltext("Use this to clear", WHITE, (50,150), True,font=SmallerFont,fontsize=20)
			normaltext("many blocks quickly.", WHITE, (50,150), True,font=SmallerFont,fontsize=20)
		case 2:
			normaltext("Rainbow Tutorial", YELLOW, (50,30), False)
			normaltext("Rainbow Square:", PINK, (50,150), True,font=SmallerFont,fontsize=20)
			normaltext("connects to all other", WHITE, (50,150), True,font=SmallerFont,fontsize=20)
			normaltext("colors of squares.", WHITE, (50,150), True,font=SmallerFont,fontsize=20)
			normaltext("", WHITE, (50,150), True,font=SmallerFont,fontsize=20)
			normaltext("They can be used to", WHITE, (50,150), True,font=SmallerFont,fontsize=20)
			normaltext("connect chains of", WHITE, (50,150), True,font=SmallerFont,fontsize=20)
			normaltext("different colors.", WHITE, (50,150), True,font=SmallerFont,fontsize=20)
			normaltext("", WHITE, (50,150), True,font=SmallerFont,fontsize=20)
			normaltext("Use these to extend", WHITE, (50,150), True,font=SmallerFont,fontsize=20)
			normaltext("your combos or clear", WHITE, (50,150), True,font=SmallerFont,fontsize=20)
			normaltext("many colors at once!", WHITE, (50,150), True,font=SmallerFont,fontsize=20)
		case 3:
			normaltext("Combo Tutorial", YELLOW, (50,30), False)
			normaltext("Long Chains:", PINK, (50,150), True,font=SmallerFont,fontsize=20)
			normaltext("Squares farther from", WHITE, (50,150), True,font=SmallerFont,fontsize=20)
			normaltext("their connected", WHITE, (50,150), True,font=SmallerFont,fontsize=20)
			normaltext("catalysts are worth", WHITE, (50,150), True,font=SmallerFont,fontsize=20)
			normaltext("many more points.", WHITE, (50,150), True,font=SmallerFont,fontsize=20)
			normaltext("", WHITE, (50,150), True,font=SmallerFont,fontsize=20)
			normaltext("Make long chains of", WHITE, (50,150), True,font=SmallerFont,fontsize=20)
			normaltext("connected squares to", WHITE, (50,150), True,font=SmallerFont,fontsize=20)
			normaltext("earn massive scores!", WHITE, (50,150), True,font=SmallerFont,fontsize=20)
		case 4:
			normaltext("Bomb Tutorial", YELLOW, (50,30), False)
			normaltext("Bombs:", PINK, (50,150), True,font=SmallerFont,fontsize=20)
			normaltext("When connected to a", WHITE, (50,150), True,font=SmallerFont,fontsize=20)
			normaltext("catalyst, a bomb will", WHITE, (50,150), True,font=SmallerFont,fontsize=20)
			normaltext("connect to all nearby", WHITE, (50,150), True,font=SmallerFont,fontsize=20)
			normaltext("squares of the same", WHITE, (50,150), True,font=SmallerFont,fontsize=20)
			normaltext("color.", WHITE, (50,150), True,font=SmallerFont,fontsize=20)
			normaltext("", WHITE, (50,150), True,font=SmallerFont,fontsize=20)
			normaltext("They're excellent for", WHITE, (50,150), True,font=SmallerFont,fontsize=20)
			normaltext("clearing out many", WHITE, (50,150), True,font=SmallerFont,fontsize=20)
			normaltext("squares at once,", WHITE, (50,150), True,font=SmallerFont,fontsize=20)
			normaltext("", WHITE, (50,150), True,font=SmallerFont,fontsize=20)
			normaltext("but they don't", WHITE, (50,150), True,font=SmallerFont,fontsize=20)
			normaltext("increase your chain", WHITE, (50,150), True,font=SmallerFont,fontsize=20)
			normaltext("anywhere as fast as", WHITE, (50,150), True,font=SmallerFont,fontsize=20)
			normaltext("a continuous line.", WHITE, (50,150), True,font=SmallerFont,fontsize=20)
			normaltext("", WHITE, (50,150), True,font=SmallerFont,fontsize=20)
			normaltext("Rainbow Bombs:", PINK, (50,150), True,font=SmallerFont,fontsize=20)
			normaltext("Rainbow bombs are", WHITE, (50,150), True,font=SmallerFont,fontsize=20)
			normaltext("are rare, but can", WHITE, (50,150), True,font=SmallerFont,fontsize=20)
			normaltext("single-handedly", WHITE, (50,150), True,font=SmallerFont,fontsize=20)
			normaltext("clear large parts", WHITE, (50,150), True,font=SmallerFont,fontsize=20)
			normaltext("of the board.", WHITE, (50,150), True,font=SmallerFont,fontsize=20)
		case 5:
			normaltext("Hard Cascade/Mercy Tutorial", YELLOW, (50,30), False)
			normaltext("Controls", PINK, (50,150), True,font=SmallerFont,fontsize=20)
			normaltext("LSHIFT (Hold): Hard Cascade", PINK, (50,150), True,font=SmallerFont,fontsize=20)
			normaltext("", WHITE, (50,150), True,font=SmallerFont,fontsize=20)
			normaltext("Hard Cascade:", PINK, (50,150), True,font=SmallerFont,fontsize=20)
			normaltext("Dropped blocks will hit", WHITE, (50,150), True,font=SmallerFont,fontsize=20)
			normaltext("the ground instantly.", WHITE, (50,150), True,font=SmallerFont,fontsize=20)
			normaltext("", WHITE, (50,150), True,font=SmallerFont,fontsize=20)
			normaltext("This is automatically", WHITE, (50,150), True,font=SmallerFont,fontsize=20)
			normaltext("performed whenever", WHITE, (50,150), True,font=SmallerFont,fontsize=20)
			normaltext("catalysts are about", WHITE, (50,150), True,font=SmallerFont,fontsize=20)
			normaltext("to explode.", WHITE, (50,150), True,font=SmallerFont,fontsize=20)
			normaltext("", WHITE, (50,150), True,font=SmallerFont,fontsize=20)
			normaltext("Mercy: ", PINK, (50,150), True,font=SmallerFont,fontsize=20)
			normaltext("While a catalyst timer", WHITE, (50,150), True,font=SmallerFont,fontsize=20)
			normaltext("is active, triggering", WHITE, (50,150), True,font=SmallerFont,fontsize=20)
			normaltext("a Game Over by reaching", WHITE, (50,150), True,font=SmallerFont,fontsize=20)
			normaltext("the top of the board will", WHITE, (50,150), True,font=SmallerFont,fontsize=20)
			normaltext("end the timer and cause", WHITE, (50,150), True,font=SmallerFont,fontsize=20)
			normaltext("an explosion.", WHITE, (50,150), True,font=SmallerFont,fontsize=20)
			normaltext("", WHITE, (50,150), True,font=SmallerFont,fontsize=20)
			normaltext("Whether that explosion", WHITE, (50,150), True,font=SmallerFont,fontsize=20)
			normaltext("saves you is your issue.", WHITE, (50,150), True,font=SmallerFont,fontsize=20)

def menutext(itemtext, buttonmask = "null", txtcolorpressed = YELLOW, txtcolornormal = WHITE, source=(50,150), offset=True, font=DefaultFont, depth = 0, fontsize = 30, ismenutext = True) -> Rect: # Draws interactable text.
	"""
	Draws interactable text. Used consecutevely, it can create multiple lines.
	
	:itemtext: string. Text (Required)
	:buttonmask: string or Config. Used to easily change config. (Default: "null")
	:txtcolorpressed: tuple[3]. RGB values for text color when highlighted. (Default: (255,255,0))
	:txtcolornormal: tuple[3]. RGB values for text color when not highlighted. (Default: (255,255,255))
	:source: tuple(2). Coordinates for top left corner of text. (Default: (0,50))
	:offset: bool. Whether or not to increment offset. (Default: True)
	:font: pygame.font. (Default: DefaultFont)
	:depth: int. like offset but for x.
	"""
	global window, buttonlist, menuitemoffset
	if ismenutext: buttonlist.append(buttonmask)
	color = txtcolorpressed if cursor_pos == menuitemoffset else txtcolornormal
	textbox = font.render(itemtext, True, color)
	window.blit(textbox,(source[0] + depth * 20, source[1] + menuitemoffset * fontsize))
	if offset:
		menuitemoffset += 1
		
	textrect = textbox.get_rect(topleft = (source[0] + depth * 20, source[1] + (menuitemoffset-1) * fontsize))
	screenupdaterects.append(textrect)
	return textrect

def normaltext(itemtext: str, txtcolor= WHITE, source = (0,0), offset = True, font = DefaultFont,fontsize = 30) -> Rect: # Draws non-interactable text consecutively.
	"""
	Draws non-interactable text. Used consecutevely, it can create multiple lines. This still doesn't properly render. >:(
	
	:itemtext: string. Text (Required)
	:txtcolor: tuple[3]. RGB values for text color. (Default: (255,255,255))
	:source: tuple(2). Coordinates for top left corner of text. (Default: (0,0))
	:offset: bool. Whether or not to increment offset. (Default: True)
	:font: pygame.font. (Default: DefaultFont)
	"""
	
	#menutext(itemtext, txtcolornormal = txtcolor, source=source, offset=offset, font=font, fontsize = fontsize, ismenutext = False)
	
	global window, textoffset
	textbox = font.render(itemtext, True, txtcolor)
	
	window.blit(textbox,(source[0], source[1] + textoffset * fontsize))
	if offset:
		textoffset += 1
	textrect = textbox.get_rect(topleft = (source[0], source[1] + (textoffset-1) * fontsize))
	screenupdaterects.append(textrect)
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

			resize_board()
	
	#pygame.display.update()
	if updatescreennextframe > 0:
		pygame.display.update()
		updatescreennextframe -= 1
	else:
		pygame.display.update(screenupdaterects)
	screenupdaterects = []
	fps.tick(60)
	

pygame.quit()
sys.exit()