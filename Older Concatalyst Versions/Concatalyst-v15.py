"""
Concatalyst

Code by: Lucina Riley / Kontonkitsune
Last Updated: 22/7/2023

This is an action-puzzle game about making really long chains and then blowing them up.


Bugs:

Bombtimer goes off screen when doing shit



To Do:

High scores
Scores per preset
Different presets give different scores
Custom preset doesn't give a high score

Color Schemes

Ingame timer

Ability to change some basic parameters (Start level, end level, squares per level) in a preset without switching to custom difficulty

Preset Ideas:

Assorted Chaos

Trash Heap (Few colors, but very high trash chance)




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
	def __init__(self, value = 0, max = 0, min = 0, scale = 1, boolean = False, needupdate = False, tooltip = None):
		self.value = value
		self.max = max
		self.min = min
		self.scale = scale
		self.boolean = boolean
		self.needupdate = needupdate
		self.tooltip = tooltip
		
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
		if self.boolean:
			return "True" if self.value else "False"
		else:
			return f"{self.value}; Min: {self.min} Max: {self.max}"
	def __boolean__(self):
		return self.value

class Preset:
	def __init__(self,*settings,displayname=None,desc=None,startgame=False,settutoriallevel=-1,startboard=0,startwithtimer=0):
		self.displayname = displayname
		self.desc = desc
		self.settings = settings
		self.settutoriallevel = settutoriallevel
		self.startgame = startgame
		self.startboard = startboard
		self.startwithtimer = startwithtimer
	def apply(self):
		if not self.displayname is None:
			global selectedpreset
			selectedpreset = self.displayname
		if self.settutoriallevel != -1:
			global tutoriallevel
			tutoriallevel = self.settutoriallevel
		
		for x in self.settings:
			print(x)
			if isinstance(x,(list,tuple)):
				setting, value = x
				print(setting,value)
				setting.set(value)
		
		if self.startgame:
			global game_state
			game_state = "game"
			init_board(self.startboard,self.startwithtimer)
		
class Block:
	"""
	A class containing four cells arranged in a square.
	
	The literal building block of the game.
	"""
	def __init__(self, *args):
		self.tl = args[0]
		self.tr = args[1]
		self.bl = args[2]
		self.br = args[3]
		
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
				
class Board: # variable-depth array
	def __init__(self, width, height,filltype = 0):
		if filltype == 2:
			self.cells = [ [ [Square(),0,0] 		for y in range(height)] 		for x in range(width)]
		elif filltype == 1:
			self.cells = [[Square() for y in range(height)] for x in range(width)]
		else:
			self.cells = [[0 for y in range(height)] for x in range(width)]
		self.width = width
		self.height = height
		
		
	def __getitem__(self,index):
		if len(index) == 2:
			x,y = index
			if isinstance(self.cells[x][y],list):
				return self.cells[x][y][0]
			else:
				return self.cells[x][y]
		else:
			x,y,z = index
			return self.cells[x][y][z]
	def __setitem__(self,index,value):
		if len(index) == 2:
			x,y = index
			if isinstance(self.cells[x][y],list):
				self.cells[x][y][0] = value
			else:
				self.cells[x][y] = value
		else:
			x,y,z = index
			self.cells[x][y][z] = value
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
keypressvalid = 0 # True on frames where a key should be able to be pressed (for continuous movement)
selectedpreset = "Normal"
tutorialsection = 0
supersecretthings = False

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
GameBoard = Board(BOARD_SIZE_X,BOARD_SIZE_Y + 4,2) # The game board. It's a bit bigger than it looks.

ConcatalystTitleBoard = Board(43,9,2)

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
fastcascade = False
immunity = 0

# Timers and Counters
clock = 0 # General ingame timer, used for a lot of stuff.
grace = 100 
catalysttimer = 400
timesinceexplode = 0
blockssincelastcatalyst = 0
catalystssincelastclear = 0
blockssincelastbomb = 0
blockssincelasteraser = 0


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
configMenuSpecialsCatalysts = Config(0,4,4,boolean=True)
configMenuSpecialsBombs = Config(0,4,5,boolean=True)
configMenuSpecialsErasers = Config(0,4,6,boolean=True)

configMenuBoard = Config(0,3,5,boolean=True)
optionsMenu = Config(0,1,4,boolean=True)
tutorialsMenu = Config(0,1,5,boolean=True)

# Visual
blockSize = Config(BLOCK_SIZE,100,10,5,tooltip="Block size (Visual).") 
titleBoardRefresh = Config(300,1500,50,50,tooltip="How long to wait after an explosion before resetting the board (Main Menu).")
drawExtras = Config(1,-1,-1,boolean=True,tooltip="Whether an outline should appear around the area of a bomb explosion.")
connectionType = Config(2,2,0,1,tooltip="How connected squares should be drawn.")
connectionThickness = Config(5,10,1,1)
pulseIntensity = Config(50,100,5,5)
pulseSpeed = Config(10,30,1,1)
pulseFrequency = Config(50,100,5,5)

# Board
boardHeight = Config(BOARD_SIZE_Y,24,8,1,needupdate=True,tooltip="Height of the board")
boardWidth = Config(BOARD_SIZE_X,24,4,1,needupdate=True,tooltip="Width of the board")

testBoardSelection = Config(0,1,0,1) # How 

# Gameplay
startLevel = Config(1,1000,1,1,tooltip="Which level you should start on.") # Starting level
doLevelUp = Config(1,-1,-1,boolean=True,tooltip="Whether you should be able to level up.")
squaresPerLevel = Config(20,100,1,1,tooltip="How many squares must be cleared in order to increase your level by one.")
endLevel = Config(100,1000,0,10,tooltip="Which level the game should end on.")
gracePeriod = Config(100,1000,0,10, tooltip = "How long a block can idle at the starting position before beginning to fall.") 

numberColors = Config(5,12,2,1,tooltip="How many colors can generate on the board. (Not including rainbow/trash)")

rainbowEnable = Config(1,-1,-1,boolean=True,tooltip="Whether rainbow squares should spawn.")
rainbowChance = Config(10,100,1,1, tooltip = "The chance that a square is rainbow.")

trashEnable = Config(0,-1,-1,boolean=True,tooltip="Whether trash squares should spawn.")
trashChance = Config(1,100,1,2, tooltip = "The chance that a square is trash.")

catalystChance = Config(-5,100,-50,1, tooltip = "Base chance for any block to be a catalyst")
catalystChanceIncrease = Config(5,10,0,1,tooltip="How much the catalyst chance should increase by for every non-catalyst block recieved.")
catalystTimer = Config(400,1200,50,50,needupdate=True,tooltip="The time between the first catalyst being placed and all catalysts exploding.")

bombEnable = Config(0,-1,-1,boolean=True,tooltip="Whether bombs should spawn.")
bombChance = Config(-2,100,-100,1,tooltip="Base chance for any block to be a catalyst")
bombChanceIncrease = Config(1,10,0,1,tooltip="How much the bomb chance should increase by for every non-bomb block recieved.") 
bombRange = Config(4,5,0,1,tooltip="How far away a bomb should reach")
bombChain = Config(1,-1,-1,boolean=True,tooltip="Whether bombs are allowed to continue chains or if they can only remove nearby blocks.")

eraserEnable = Config(0,-1,-1,boolean=True,tooltip="Whether erasers should spawn.")
eraserChance = Config(-10,100,-100,1,tooltip="Base chance for any block to be a catalyst.")
eraserChanceIncrease = Config(1,10,0,1,tooltip="How much the eraser chance should increase by for every non-eraser block recieved.")
eraserChain = Config(0,-1,-1,boolean=True,tooltip="Whether erasers are allowed to continue chains or if they can only remove nearby blocks.")
eraserRainbowEnable = Config(1,-1,-1,boolean=True,tooltip="How much the eraser chance should increase by for every non-eraser block recieved.")
eraserTargetsTrash = Config(0,-1,-1,boolean=True,tooltip="Whether erasers of all colors should be able to target trash squares.")

"""-------------------Custom Boards--------------------"""


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
	( 3, 3, 2,-2,-2,-2,-2,-2,-2,-2)),
	
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
	( 5, 1, 3, 2, 5, 3, 5, 2, 4, 5),
	( 3, 4, 2, 6, 1, 2, 1, 4, 5, 6),
	( 1, 6, 2, 4, 5, 1, 6, 2, 4, 5),
	( 2, 5, 4, 3, 6, 2, 5, 4, 3, 6),
	(-2,-2,-2,-2,-2,-2,-2,-2,-2,-2),
	(-2,-2,-2,-2,Square(-2,3),-2,-2,-2,-2,-2),
	(-2,-2,-2,-2,-2,-2,-2,-2,-2,-2))
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


"""--------------------------------Presets-----------------------------------------"""

def applyDefaultPreset():
	"""Sets config options to default values"""
	global tutoriallevel
	tutoriallevel = -1
	
	
	startLevel.set(1)
	doLevelUp.set(1)
	squaresPerLevel.set(20)
	endLevel.set(100)
	
	boardHeight.set(16)
	boardWidth.set(10)
	numberColors.set(5)
	gracePeriod.set(100)
	
	rainbowEnable.set(1)
	rainbowChance.set(10)
	trashEnable.set(0)
	trashChance.set(1)
	catalystChance.set(-5) 
	catalystChanceIncrease.set(5) 
	catalystTimer.set(400)
	bombEnable.set(0)
	bombChance.set(-2)
	bombChanceIncrease.set(1)
	bombRange.set(4)
	bombChain.set(1)
	eraserEnable.set(0)
	eraserChance.set(-10)
	eraserChanceIncrease.set(1)
	eraserChain.set(0)
	eraserRainbowEnable.set(1)
	eraserTargetsTrash.set(0)

# Preset declarations
presetDifficultyCasual = Preset((numberColors,4),(gracePeriod,150),(rainbowChance,15),(catalystChance,-10),(catalystChanceIncrease,10),(catalystTimer,400),displayname="Casual",desc="Easiest difficulty, for inexperienced players who want to learn the mechanics.")
presetDifficultyEasy = Preset((gracePeriod,150),(rainbowChance,15),(catalystChance,-10),(catalystChanceIncrease,10),(catalystTimer,400),displayname="Easy",desc="For players who just want to take it a bit easy.")
presetDifficultyNormal = Preset(displayname="Normal",desc="The standard Concatalyst game.")
presetDifficultyHard = Preset((squaresPerLevel,25),(boardHeight,16),(boardWidth,12),(numberColors,6),(gracePeriod,75),(rainbowChance,7),(catalystChance,-4),(catalystChanceIncrease,4),(catalystTimer,500),displayname="Hard",desc="For players who want more of a challenge.")
presetDifficultyExtreme = Preset((squaresPerLevel,30),(boardHeight,18),(boardWidth,14),(numberColors,7),(gracePeriod,50),(rainbowChance,5),(catalystChance,-8),(catalystChanceIncrease,4),(catalystTimer,600),displayname="Extreme",desc="For experienced players who think Hard is Easy.")
presetDifficultyAbsurd = Preset((squaresPerLevel,40),(boardHeight,20),(boardWidth,14),(numberColors,8),(gracePeriod,30),(rainbowChance,5),(catalystChance,-6),(catalystChanceIncrease,3),(catalystTimer,800),displayname="Absurd",desc="For experienced players who think Extreme is Casual.")

presetFunSpaceproblems = Preset((squaresPerLevel,30),(boardHeight,24),(boardWidth,16),(numberColors,8),(gracePeriod,150),(rainbowChance,15),(catalystChance,-10),(catalystChanceIncrease,10),displayname="Space Problems",desc="Larger board, more colors to deal with.")

presetTutorialBasic = Preset((doLevelUp,0),(numberColors,2),(gracePeriod,150),(rainbowEnable,0),(catalystChance,-25),(catalystChanceIncrease,25),(catalystTimer,100),displayname="Basic Tutorial",desc="Learn the basic loop of the game.",startgame=True,settutoriallevel=0)
presetTutorialCatalysts = Preset((doLevelUp,0),(numberColors,2),(gracePeriod,150),(rainbowEnable,0),(catalystChance,0),(catalystChanceIncrease,25),(catalystTimer,200),displayname="Catalyst Tutorial",desc="How to use catalysts effectively.",startgame=True,settutoriallevel=1)
presetTutorialRainbow = Preset((doLevelUp,0),(numberColors,3),(gracePeriod,150),(rainbowChance,25),(catalystChance,10),(catalystChanceIncrease,10),displayname="Rainbow Tutorial",desc="Learn how to chain colors together with Rainbow squares.",startgame=True,startboard=tutorialboards[0],settutoriallevel=2)
presetTutorialCombo = Preset((doLevelUp,0),(numberColors,4),(gracePeriod,150),(rainbowChance,15),(catalystChance,0),(catalystChanceIncrease,10),displayname="Combo Tutorial",desc="Learn how to score more points.",startgame=True,startboard=tutorialboards[1],settutoriallevel=3)
presetTutorialBombs = Preset((doLevelUp,0),(numberColors,4),(gracePeriod,150),(rainbowChance,5),(catalystChance,0),(catalystChanceIncrease,10),(catalystTimer,200),(bombEnable,1),(bombChance,0),(bombChanceIncrease,5),displayname="Bomb Tutorial",desc="FIXME.",startgame=True,startboard=tutorialboards[2],settutoriallevel=4)
presetTutorialMercy = Preset((doLevelUp,0),(numberColors,4),(gracePeriod,150),(rainbowChance,15),(catalystChance,0),(catalystChanceIncrease,10),(catalystTimer,1200),displayname="Mercy Tutorial",desc="FIXME",startgame=True,startboard=tutorialboards[3],startwithtimer=1,settutoriallevel=5)
presetTutorialTrash = Preset((doLevelUp,0),(numberColors,4),(gracePeriod,150),(rainbowChance,15),(catalystChance,0),(catalystChanceIncrease,10),(trashEnable,1),(trashChance,5),(bombEnable,1),(bombChance,0),(bombChanceIncrease,2),displayname="Trash Tutorial",desc="FIXME",startgame=True,startboard=tutorialboards[4],startwithtimer=1,settutoriallevel=6)
presetTutorialErasers = Preset((doLevelUp,0),(numberColors,5),(gracePeriod,150),(trashEnable,1),(trashChance,10),(bombEnable,1),(eraserEnable,1),(eraserChance,0),(eraserChanceIncrease,3),displayname="Eraser Tutorial",desc="FIXME",startgame=True,startboard=tutorialboards[5],settutoriallevel=7)

# Preset lists

tutorialpresets = (presetTutorialBasic,presetTutorialCatalysts,presetTutorialRainbow,presetTutorialCombo,presetTutorialBombs,presetTutorialMercy,presetTutorialTrash,presetTutorialErasers)


# window declaration
window = pygame.display.set_mode((WIDTH, HEIGHT),RESIZABLE)
pygame.display.set_caption('Concatalyst (Alpha v16)')
gamelogo = pygame.image.load("concatalystlogo.png").convert()
pygame.display.set_icon(gamelogo)
pygame.event.set_allowed([QUIT, KEYDOWN])

pygamekeys = pygame.key.get_pressed()
keys = {"CONFIRM":0,"CANCEL":0,"LEFT":0,"RIGHT":0,"UP":0,"DOWN":0,"ESCAPE":0,"SHIFT":0}

try:
	backgroundImage = pygame.image.load("BackgroundImage.jpg").convert()
	loadedbackground = True
except:
	loadedbackground = False

# Optimization Flags
updatescreennextframe = 2
needtocascade = False
screenupdaterects = []


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
		if rainbowEnable.value and random.randint(0,100) < rainbowChance.value:
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
		elif eraserEnable.value and random.randint(1,100) <= eraserChance.value + blockssincelasteraser * eraserChanceIncrease.value:
			special = 3
			if tiletype == -1 and eraserRainbowEnable.value:
				tiletype == -2
		else:
			special = 0
	
	tile = Square(tiletype,special)
	return tile

def compare_squares(localGameBoard, x: int, y: int, x2: int, y2: int) -> bool: # Checks if two squares are considered "connected" and can be cleared together. NOT COMMUTATIVE
	if isinbounds(localGameBoard,x,y) and isinbounds(localGameBoard,x2,y2):
		if localGameBoard[x,y].color == -2 and localGameBoard[x,y].special != 3:	
			return False
		if localGameBoard[x,y].color == 0 or localGameBoard[x2,y2].color == 0:
			return False
		
		if localGameBoard[x,y].color == localGameBoard[x2,y2].color:
			return True
		if localGameBoard[x,y].color == -1:
			return True
		if localGameBoard[x2,y2].color == -1:
			return True
		
		if localGameBoard[x2,y2].color == -2:
			if eraserTargetsTrash.value:
				return True
			if localGameBoard[x,y].special == 3 and localGameBoard[x,y].color > 0:
				return False
			return True
		
	return False

def isinbounds(localGameBoard, x: int, y: int) -> bool: # Checks if the given coordinates are within bounds
	if x < 0 or x >= localGameBoard.width or y < 0 or y >= localGameBoard.height:
		return False
	else:
		return True

def create_block(type="random",color=0,special=-1) -> Block:
	global blockssincelastcatalyst, blockssincelastbomb, blockssincelasteraser
	
	if special == -1:
		if random.randint(1,100) <= catalystChance.value + blockssincelastcatalyst * catalystChanceIncrease.value:
			special = 1
		elif bombEnable.value and random.randint(1,100) <= bombChance.value + blockssincelastbomb * bombChanceIncrease.value:
			special = 2
		elif eraserEnable.value and random.randint(1,100) <= eraserChance.value + blockssincelasteraser * eraserChanceIncrease.value:
			special = 3
	
	
	colorsets = []
	for x in range(0,5):
		if random.randint(1,100) <= rainbowChance.value:
			if special == 3 and eraserRainbowEnable.value: colorsets.append(-2)
			else: colorsets.append(-1)
		if trashEnable.value and random.randint(1,100) <= trashChance.value and special != 1 and special != 2:
			colorsets.append(-2)
		else:
			colorsets.append(random.randint(1,numberColors.value))
	piecetype = list(PieceDict[random.choice(PieceWeights) if type == "random" else type])
	
	genblock = [colorsets[piecetype[0]],
					colorsets[piecetype[1]],
					colorsets[piecetype[2]],
					colorsets[piecetype[3]]]
	newblock = Block(Square(genblock[0]),Square(genblock[1]),Square(genblock[2]),Square(genblock[3]))
	
	
	
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
	
	if special == 3:
		newblock.setspecial(3)
		blockssincelasteraser = 0
	else:
		blockssincelasteraser += 1
		
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
	
	if test_for_death(GameBoard): # Make sure you aren't placing the block inside another block
		if catalysttimer > 0:
			catalysttimer = 1
		else:
			game_over()
	
	for x in range(0,2):
		for y in range(0,2):
			GameBoard[block_pos_x + x,block_pos_y + y - 1] = extrablocks[0][x,y]
	
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

def init_board(boardtoload=0,startwithcats=0) -> None: # Initializes the board
	"""This function initializes the game."""
	
	global GameBoard
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
	blockssincelasteraser = 0 if game_state == "game" else 3
	
	GameBoard = Board(boardWidth.value,boardHeight.value + 4,2)
	
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
	elif startwithcats:
		catalysttimer = catalystTimer.value
	else:
		catalysttimer = -1
	
	board_update_connected(GameBoard)
	
	if boardtoload != 0:
		load_board(GameBoard,boardtoload)

def init_concatalyst_board():
	for y in range(0,len(concatalystboardlayout)):
		for x in range(0,len(concatalystboardlayout[0])):
			ConcatalystTitleBoard[x,y] = Square(concatalystboardlayout[4-y][x])
	ConcatalystTitleBoard[2,4] = Square(2,1)
	board_update_connected(ConcatalystTitleBoard)

def clear_board(board: Board,squares=True,clearconnected=True,addtoexplode=False) -> None:
	if clearconnected:
		for x in range(0,board.width):
			for y in range(0,board.height):
				if addtoexplode:
					board[x,y,2] = board[x,y,1]
				
				if squares:
					board[x,y,1].set(0,0)
				else:
					board[x,y,1] = 0
	else:
		for x in range(0,board.width):
			for y in range(0,board.height):
				if squares:
					board[x,y].set(0,0)
				else:
					board[x,y] = 0

def board_update_connected(localInputBoard): # Searches through the board and figures out which blocks are connected to catalysts.
	"""
	Searches through the board and returns a board of all cells connected to catalysts.
	
	
	"""
	global catalysttimer
	
	stack = []
	
	for x in range(0,localInputBoard.width):
		for y in range(0,localInputBoard.height):
			if localInputBoard[x,y].special == 1:
				if catalysttimer < 0:
					catalysttimer = catalystTimer.value
				localInputBoard[x,y,1] = 1
				stack.append((x,y))
			else:
				localInputBoard[x,y,1] = 0
	
	while len(stack) > 0:
		x = stack[0][0]
		y = stack[0][1]
		stack.pop(0)
		# Catalyst / Normal logic
		if not isinbounds(localInputBoard,x,y): continue
		
		if localInputBoard[x,y].special == 2:
			connectablelocations = []
			for x2 in range(x - bombRange.value, x + bombRange.value + 1):
				for y2 in range(y - bombRange.value, y + bombRange.value + 1):
					connectablelocations.append((x2,y2))
		elif localInputBoard[x,y].special == 3:
			connectablelocations = []
			for x2 in range(0, localInputBoard.width):
				for y2 in range(0, localInputBoard.height):
					connectablelocations.append((x2,y2))
		else:
			connectablelocations = ((x+1,y),(x-1,y),(x,y+1),(x,y-1))
		
		for p in connectablelocations:
			if isinbounds(localInputBoard,p[0],p[1]) and localInputBoard[p[0],p[1]].special != 1: 
				if (localInputBoard[p[0],p[1],1] == 0 or localInputBoard[p[0],p[1],1] > localInputBoard[x,y,1] + 1) and compare_squares(localInputBoard,x,y,p[0],p[1]):
					if not (localInputBoard[x,y].special == 2 and not bombChain.value):
						stack.append((p[0],p[1]))
					localInputBoard[p[0],p[1],1] = localInputBoard[x,y,1] + 1
	
def clear_connected_squares(localGameBoard) -> tuple: # Deletes squares connected to catalysts and returns point values
	"""
	
	
	"""
	global timesinceexplode
	timesinceexplode = 0
	score = 0
	squares = 0
	highestchain = 0
	pointspersquare = BASE_POINTS
	for x in range(0,localGameBoard.width):
		for y in range(0,localGameBoard.height):
			if localGameBoard[x,y,1] != 0:
				localGameBoard[x,y].set(0,0)
				squares += 1
				if localGameBoard[x,y,1] > highestchain:
					highestchain = localGameBoard[x,y,1]
				score += int(10 + localGameBoard[x,y,1]**2)
	return score, squares, highestchain

def cascade_board(localGameBoard, hard_cascade = False,deletebottom=False,onlycheck=False):
	gravityflag = False
	cascadeflag = False
	successful = False
	for x in range(0,localGameBoard.width):
		#First check if anything is wrong in the column
		gravityflag = False # Becomes true when the search finds an empty space
		cascadeflag = False # Becomes true when the search finds a non-empty space above an empty space
		
		if deletebottom:
			localGameBoard[x,0].set(0,0)
		
		for y in range(0,localGameBoard.height):
			
			if gravityflag and localGameBoard[x,y].color != 0:
				cascadeflag = True
			elif localGameBoard[x,y].color == 0:
				gravityflag = True
		
		#if something is wrong with the column, it will go through each block until it finds empty space, then if it finds blocks above that it will pull them to the first black space it will continue progressively.
		gravityflag = False
		if not onlycheck and cascadeflag:
			successful = True
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
	return successful

def explode_board(localGameBoard) -> None: # 
	global score, longestchain, squarescleared, catalystssincelastclear, updatescreennextframe
	cascade_board(localGameBoard,True)
	board_update_connected(localGameBoard)
	previousscores.insert(0,tuple(clear_connected_squares(localGameBoard) + tuple([clock])))
	clear_board(localGameBoard,False,clearconnected=True,addtoexplode=True)
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

def test_for_death(inputBoard = 0) -> bool:
	if inputBoard == 0: inputBoard = GameBoard
	startx = inputBoard.width // 2 - 1
	starty = inputBoard.height - 4
	for x in range(startx,startx+2):
		for y in range(starty,starty+2):
			if inputBoard[x,y].color != 0:
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
				draw_square(ConcatalystTitleBoard[x,y],x,y,blocksize=12,source=(40,100),gameboard=ConcatalystTitleBoard)
				
	screenupdaterects.append(Rect(38,38,525,64)) # Concatalyst Title Board

def draw_game(drawupnext=False) -> None:
	"""This function draws the game."""
	global textoffset
	
	#window.fill(BLACK)
	if loadedbackground:
		window.blit(backgroundImage,(0,0))
	else:
		window.fill(BLACK)
	#Draw the board
	draw_board(GameBoard,drawupnext=drawupnext,drawlines=True)
	
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
	
	
		
	if not drawupnext:
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

def draw_board(board, source=0, blocksize=0,drawupnext=False,drawlines=False,linethickness=0):
	if source == 0: source = (leftscreen,bottomscreen)
	if blocksize == 0: blocksize = blockSize.value
	if linethickness == 0: linethickness = connectionThickness.value
	
	bottomscreenreplace = source[1] - (board.height - 4) * blocksize
	rightscreenreplace = source[0] + (board.width) * blocksize
	
	
	for x in range(0,board.width):
		for y in range(0,(board.height - 2) ):
			draw_square(board[x,y],x,y,board, blocksize = blocksize, source=source)
	
	for x in range(0,board.width):
		for y in range(0,(board.height - 2) ):
			if board[x,y] != 0:
				draw_square_overlays(board[x,y],x,y,board, blocksize = blocksize, source=source,linethickness=linethickness)
	
	
	if drawupnext:
		#Draw Up Next
		if len(extrablocks) > 1:
			for z in range(1,len(extrablocks)):
				for x in range(0,2):
					for y in range(0,2):
						excolor = get_square_color(extrablocks[z][x,y])
						draw_square(		 extrablocks[z][x,y],x - 3, board.height - 3 + y - (3 * z), board, connected = False)
						draw_square_overlays(extrablocks[z][x,y],x - 3, board.height - 3 + y - (3 * z), board, connected = False)
		
		#Draw the active block
		for x in range(0,2):
			for y in range(0,2):
				excolor = get_square_color(extrablocks[0][x,y])
				draw_square(		 extrablocks[0][x,y],	(x + block_pos_x),	(y + block_pos_y - 1), board, connected = False)
				draw_square_overlays(extrablocks[0][x,y],	(x + block_pos_x),	(y + block_pos_y - 1), board, connected = False)
	
	#Lines
	
	if drawlines:
		for x in range(0,board.width + 1 ):
			pygame.draw.line(window,WHITE,
				((source[0] + (blocksize * x)),source[1]),
				((source[0] + (blocksize * x)),bottomscreenreplace))
		for y in range(0,board.height -3):
			pygame.draw.line(window,WHITE,
				(source[0],(bottomscreenreplace + (blocksize * y))),
				(rightscreenreplace,(bottomscreenreplace + (blocksize * y))))
	
	screenupdaterects.append(Rect(source[0] - blocksize,source[1] - (board.height) * blocksize, (board.width + 2) * blocksize,(board.height + 2) * blocksize))

def draw_square(square, x: int,y: int, gameboard=0, blocksize = 0, connected = True, source=0) -> None:
	"""
	This function draws squares.
	
	:square: Square or tuple[3] (RGB).
	:x: int
	:y: int
	:blocksize: int. what size all blocks should be treated as. Default: blockSize.value.
	:connected: boolean. Whether the block should be considered part of a board. Default: True
	:source: 0 or tuple[2] (position). Origin point for position calculations. Default: (leftscreen,bottomscreen)
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
	
	if connected and gameboard[x,y] == 0:
		if gameboard[x,y,2]:
			squarecolor = hsv_to_rgb(60 - 5 * gameboard[x,y,2],10 * gameboard[x,y,2],255)
			squarecolor = change_color_brightness(squarecolor, 40 * gameboard[x,y,2]  - 4 * timesinceexplode)
			if sum(squarecolor) > 40:
				pygame.draw.rect(window,squarecolor,pygame.Rect((
					(squaretopleftx, squaretoplefty),
					(blocksize,blocksize))))	
	else:
		if connectionType.value == 0 and (special == 1 or connected and gameboard[x,y,1] > 0):
			catalystcoloroffset = pulseIntensity.value * (abs( (( - clock * pulseSpeed.value ) + ( pulseFrequency.value * gameboard[x,y,1] )) % 600 - 300) - 150 ) // 150
			squarecolor = change_color_brightness(squarecolor,catalystcoloroffset)
	
		pygame.draw.rect(window,squarecolor,pygame.Rect((
					(squaretopleftx, squaretoplefty),
					(blocksize,blocksize))))	
	
		if rainbow:
			rainbowoutlinecolor = SILVER
			match special:
				case 0: rainbowoutlinecolor = SILVER
				case 1: rainbowoutlinecolor = GOLD
				case 2: rainbowoutlinecolor = GOLD
			pygame.draw.rect(window,rainbowoutlinecolor,pygame.Rect((
						(squaretopleftx, squaretoplefty),
						(blocksize,blocksize))),blocksize // 6)	

def draw_square_overlays(square, x: int,y: int, gameboard=0 , blocksize = 0, connected = True, source=0, linethickness=0) -> None:
	"""
	This function draws the catalyst connections.
	
	:square: Square or tuple[3] (RGB).
	:x: int
	:y: int
	:blocksize: int. what size all blocks should be treated as. Default: blockSize.value.
	:connected: boolean. Whether the block should be considered part of a board. Default: True
	:source: 0 or tuple[2] (position). Origin point for position calculations. Default: (leftscreen,bottomscreen)
	:gameboard: Board. Default: GameBoard
	
	"""
	if blocksize == 0: blocksize = blockSize.value
	if linethickness == 0: linethickness = connectionThickness.value
	if source:
		squaretopleftx = source[0] + (blocksize * x)
		squaretoplefty = source[1] - (blocksize * (y+1))
		
	else:
		squaretopleftx = leftscreen + (blocksize * x)
		squaretoplefty = bottomscreen - (blocksize * (y+1))
	
	if gameboard == 0: gameboard = GameBoard
		
	if isinstance(square,Square):
		squarecolor = get_square_color(square)
		special = square.special
		rainbow = (square.color == -1)
			
	else:
		squarecolor = square
		special = 0
		connected = False
		rainbow = False
	
	
	if special:
		excolor = hsv_to_rgb(clock - 5 * gameboard[x,y,1],10 * gameboard[x,y,1],min(30 * gameboard[x,y,1],255))
		
		match special:
			case 1:
				pygame.draw.circle(window,excolor, (squaretopleftx + blocksize // 2, squaretoplefty + blocksize // 2 ), blocksize // 4)
			case 2:
				pygame.draw.circle(window,excolor, (squaretopleftx + blocksize // 2, squaretoplefty + blocksize // 2 ), blocksize // 2 - 5,3)
				
				if drawExtras.value and connected and gameboard[x,y,1] > 0:
					draw_bomb_radius(gameboard,x,y,blocksize)
			case 3:
				pygame.draw.rect(window,excolor,pygame.Rect((
						(squaretopleftx + blocksize // 4, squaretoplefty + blocksize // 4),
						(blocksize // 2,blocksize // 2))),blocksize // 8)
				
	
	if connected and gameboard[x,y,1] > 0:
		if connectionType.value == 1: # Crosses
			if True:
				excolor = hsv_to_rgb(clock - 5 * gameboard[x,y,1],10 * gameboard[x,y,1],min(30 * gameboard[x,y,1],255))
			else:
				excolor = BLACK
			pygame.draw.line(window,excolor,
				(squaretopleftx + blocksize // 2,	squaretoplefty),
				(squaretopleftx + blocksize // 2,	squaretoplefty + blocksize),		linethickness)
			pygame.draw.line(window,excolor,
				(squaretopleftx,					squaretoplefty + blocksize // 2),
				(squaretopleftx + blocksize,		squaretoplefty + blocksize // 2),	linethickness)
		
		elif connectionType.value == 2: # Wires
			
			isolatedsquare = True
			for p in ((-1,0),(0,-1),(1,0),(0,1)):
				if (connected and gameboard[x,y,1] > 0) and isinbounds(gameboard,x + p[0],y + p[1]) and compare_squares(gameboard,x,y,x+p[0],y+p[1]):
					if abs(gameboard[x+p[0],y+p[1],1] - gameboard[x,y,1]) == 1: isolatedsquare = False
					if (gameboard[x+p[0],y+p[1],1] - gameboard[x,y,1]) == 1:
						if True:
							excolor = hsv_to_rgb(clock - 5 * gameboard[x,y,1],10 * gameboard[x,y,1],min(30 * gameboard[x,y,1],255))
						else:
							excolor = BLACK
						pygame.draw.line(window,excolor,	(squaretopleftx + blocksize // 2,	squaretoplefty + blocksize // 2),(squaretopleftx + blocksize // 2 + p[0] * blocksize,	squaretoplefty + blocksize // 2 - p[1] * blocksize),linethickness)
			
			if isolatedsquare and special == 0:
				if True:
					excolor = hsv_to_rgb(clock - 5 * gameboard[x,y,1],10 * gameboard[x,y,1],min(30 * gameboard[x,y,1],255))
				else:
					excolor = BLACK
				pygame.draw.circle(window,excolor, (squaretopleftx + blocksize // 2, squaretoplefty + blocksize // 2 ), linethickness // 2 + 1)

def draw_bomb_radius(gameboard: Board, x: int, y:int, blocksize = 0):
	if not blocksize: blocksize = blockSize.value
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
	
	excolor = hsv_to_rgb(clock - 5 * gameboard[x,y,1],10 * gameboard[x,y,1],min(30 * gameboard[x,y,1],255))
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
	
	global clock, catalysttimer, timesinceexplode
	
	clock += 1
	timesinceexplode += 1
	catalysttimer -= 1
	
	if fastcascade or clock % 3 == 0:
		if game_state == "main_menu":
			cascade_board(GameBoard,deletebottom=catalysttimer <= -titleBoardRefresh.value * 2 // 3)
		elif game_state == "death_menu":
			cascade_board(GameBoard,deletebottom=True)
		else:
			if not cascade_board(GameBoard):
				if test_for_death(GameBoard): # Make sure you aren't placing the block inside another block
					if catalysttimer > 0:
						catalysttimer = 1
					else:
						game_over()
					
	if catalysttimer == 0:
		explode_board(GameBoard)
	
	if catalysttimer > 0 and catalysttimer % 10 == 0:
		board_update_connected(GameBoard)
	
	if game_state == "main_menu" and catalysttimer <= -titleBoardRefresh.value:
		init_board()
		catalysttimer = catalystTimer.value

def global_key_press_tracker() -> None:
	global pygamekeys, keys
	pygamekeys = pygame.key.get_pressed()
	
	if (pygamekeys[K_z] or pygamekeys[K_e] or pygamekeys[K_RETURN] or pygamekeys[K_KP_ENTER] or pygamekeys[K_SPACE]):
		keys["CONFIRM"] += 1
	else: keys["CONFIRM"] = 0
	
	if (pygamekeys[K_BACKSPACE] or pygamekeys[K_q] or pygamekeys[K_x]):
		keys["CANCEL"] += 1
	else: keys["CANCEL"] = 0
	
	if (pygamekeys[K_ESCAPE] or pygamekeys[K_p] or pygamekeys[K_KP_MINUS]):
		keys["ESCAPE"] += 1
	else: keys["ESCAPE"] = 0
	
	if (pygamekeys[K_LSHIFT] or pygamekeys[K_RSHIFT]):
		keys["SHIFT"] += 1
	else: keys["SHIFT"] = 0
	
	if (pygamekeys[K_UP] or pygamekeys[K_w] or pygamekeys[K_KP8]):
		keys["UP"] += 1
	else: keys["UP"] = 0
	
	if (pygamekeys[K_DOWN] or pygamekeys[K_s] or pygamekeys[K_KP2]):
		keys["DOWN"] += 1
	else: keys["DOWN"] = 0
	
	if (pygamekeys[K_RIGHT] or pygamekeys[K_d] or pygamekeys[K_KP6]):
		keys["RIGHT"] += 1
	else: keys["RIGHT"] = 0
	
	if (pygamekeys[K_LEFT] or pygamekeys[K_a] or pygamekeys[K_KP4]):
		keys["LEFT"] += 1
	else: keys["LEFT"] = 0
	
def getkey(key,delay=30,cont=5) -> bool:
	if keys[key] != 1 and delay < 0:
		return False
	
	if keys[key] == 1 or (keys[key] >= delay and keys[key] % cont == 0):
		return True
	
	return False
	
def global_controls() -> None:
	global keydowntimer, game_state, updatescreennextframe, timesinceexplode
	
	global fastcascade 
	fastcascade = keys["SHIFT"]
	if keys["SHIFT"]:
		timesinceexplode += 1
	if getkey("ESCAPE",delay=-1):
		if game_state == "pause_menu":
			game_state = "game"
			updatescreennextframe = 2
		if game_state == "game":
			game_state = "pause_menu"
			updatescreennextframe = 2

def game_processing() -> None: # Ingame event handling
	"""This function does most of the game's event handling."""
	global keys, game_state, keypressvalid
	global block_pos_x, block_pos_y, grace, block_fall_progress
	global extrablocks
	
	global_board_updates()
	global_controls()
	
	outofbounds = (block_pos_y < 1 or block_pos_y > GameBoard.height - 3 or block_pos_x < 0 or block_pos_x >= GameBoard.width - 1) 
	
	
	
	if getkey("CONFIRM"):
		extrablocks[0] = rotate_block(extrablocks[0])
	if getkey("CANCEL"):
		extrablocks[0] = rotate_block(extrablocks[0],clockwise=False)
	if getkey("UP",-1):
		place_block()
		
		
	#Necessary to prevent out of bounds crashing
	if getkey("RIGHT",20) and block_pos_x < GameBoard.width - 2:
		if outofbounds or GameBoard[block_pos_x + 2,block_pos_y] == 0 and GameBoard[block_pos_x + 2,block_pos_y - 1] == 0:
			block_pos_x += 1
	if getkey("LEFT",20) and block_pos_x > 0:
		if outofbounds or GameBoard[block_pos_x - 1,block_pos_y] == 0 and GameBoard[block_pos_x - 1,block_pos_y - 1] == 0:
			block_pos_x -= 1
	if getkey("DOWN",20):
		if outofbounds or GameBoard[block_pos_x,block_pos_y - 2] == 0 and GameBoard[block_pos_x + 1,block_pos_y - 2] == 0 and block_pos_y >= 2:
			block_pos_y -= 1
			block_fall_progress = 0
		else:
			place_block()
	
	if doLevelUp.value and squarescleared > squaresPerLevel.value * level:
		level_up()
	
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
	
	
	# draw the game
	draw_game(drawupnext=True)
	
def menu_processing() -> None:
	"""This function controls the menu."""
	global game_state, cursor_pos, updatescreennextframe, screenupdaterects, clock, selectedpreset, tutoriallevel
	global catalysttimer, timesinceexplode
	
	if game_state == "main_menu" or game_state == "death_menu":
		global_board_updates()
		draw_game()
	else:
		clock += 1
		timesinceexplode += 1
		draw_game()
	global_controls()
	
	
	if game_state == "main_menu":
		main_menu_text()
		draw_board(ConcatalystTitleBoard,source=(40,100),blocksize=12,linethickness=3)
	elif game_state == "pause_menu":
		pause_menu_text()
	elif game_state == "death_menu":
		game_over_menu_text()
	elif game_state == "win_menu":
		game_over_menu_text(True)
	 # Display Board
	
	# move cursor
	if getkey("UP"):
		updatescreennextframe = 2
		cursor_pos -= 1
		if cursor_pos < 0:
			cursor_pos = len(buttonlist) - 1
	if getkey("DOWN"):
		updatescreennextframe = 2
		cursor_pos += 1
		if cursor_pos > len(buttonlist) - 1:
			cursor_pos = 0

	if cursor_pos > len(buttonlist) - 1:
		cursor_pos = len(buttonlist) - 1
	
	
	
	if isinstance(buttonlist[cursor_pos],Config):
		if buttonlist[cursor_pos].boolean:
			if getkey("LEFT") or getkey("RIGHT") or getkey("CONFIRM"):
				updatescreennextframe = 2
				buttonlist[cursor_pos].toggle()
				if buttonlist[cursor_pos].needupdate:
					init_board()
				if buttonlist[cursor_pos].value:
					if buttonlist[cursor_pos].max != -1: cursor_pos = buttonlist[cursor_pos].max
				else:
					if buttonlist[cursor_pos].min != -1: cursor_pos = buttonlist[cursor_pos].min
		else:
			if getkey("RIGHT"): 
				updatescreennextframe = 2
				buttonlist[cursor_pos].increment()
				selectedpreset = "custom"
				if buttonlist[cursor_pos].needupdate:
					init_board()
			if getkey("LEFT"):
				updatescreennextframe = 2
				buttonlist[cursor_pos].decrement()
				selectedpreset = "custom"
				if buttonlist[cursor_pos].needupdate:
					init_board()
	elif isinstance(buttonlist[cursor_pos],Preset):
		if getkey("CONFIRM"):
			updatescreennextframe = 2
			apply_preset(buttonlist[cursor_pos])
		
	else:
		if getkey("CONFIRM"):
			updatescreennextframe = 2
			do_button(buttonlist[cursor_pos])

def do_button(buttonID) -> None:
	global tutoriallevel, game_state, catalysttimer, selectedpreset
	match buttonID:
			case "startgamestandard":
				game_state = "game"
				tutoriallevel = -1
				init_board()
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
			case other:
				if type(buttonID) == str and buttonID != "null":
					apply_preset(buttonID)

def apply_preset(preset):
	if isinstance(preset,Preset):
		applyDefaultPreset()
		preset.apply()

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
	menutext(f"Play Game ({selectedpreset})","startgamestandard",txtcolornormal=GREEN)
	if gamemodeMenu.value:
		menutext("-Game Modes",gamemodeMenu,txtcolornormal=PINK)
		nestlevel += 1
		menutext(f"Start Level: {startLevel.value}",startLevel,depth=nestlevel)
		menutext("Standard","startgamestandard",txtcolornormal=GREEN,depth=nestlevel)
		menutext("Endless","startgameendless",txtcolornormal=GREEN,depth=nestlevel)
		menutext("Single Level","singlelevelendless",txtcolornormal=GREEN,depth=nestlevel)
	elif presetsMenu.value:
		menutext("-Game Presets",presetsMenu,txtcolornormal=PINK)
		nestlevel += 1
		menutext(f"Preset: {selectedpreset}",depth=nestlevel)
		if presetsMenuDifficulty.value:
			menutext("-Difficulty",presetsMenuDifficulty,txtcolornormal=BLUE,depth=nestlevel)
			nestlevel += 1
			menutext("Casual",presetDifficultyCasual,txtcolornormal=ROSEGOLD if selectedpreset == "Casual" else WHITE,depth=nestlevel)
			menutext("Easy",presetDifficultyEasy,txtcolornormal=ROSEGOLD if selectedpreset == "Easy" else WHITE,depth=nestlevel)
			menutext("Normal",presetDifficultyNormal,txtcolornormal=ROSEGOLD if selectedpreset == "Normal" else WHITE,depth=nestlevel)
			menutext("Hard",presetDifficultyHard,txtcolornormal=ROSEGOLD if selectedpreset == "Hard" else WHITE,depth=nestlevel)
			menutext("Extreme",presetDifficultyExtreme,txtcolornormal=ROSEGOLD if selectedpreset == "Extreme" else WHITE,depth=nestlevel)
			menutext("Absurd",presetDifficultyAbsurd,txtcolornormal=ROSEGOLD if selectedpreset == "Absurd" else WHITE,depth=nestlevel)
		elif presetsMenuOther.value:
			menutext("-Other",presetsMenuOther,txtcolornormal=BLUE,depth=nestlevel)
			nestlevel += 1
			menutext("More Space More Problems","Space Problems",txtcolornormal=ROSEGOLD if selectedpreset == "Space Problems" else WHITE,depth=nestlevel)
		else:
			
			menutext("Difficulty",presetsMenuDifficulty,txtcolornormal=BLUE,depth=nestlevel)
			menutext("Other",presetsMenuOther,txtcolornormal=BLUE,depth=nestlevel)
	elif configMenu.value:
		menutext("-Game Config",configMenu,txtcolornormal=PINK,depth=nestlevel)
		nestlevel += 1
		menutext("Refresh Title","reinitialize",depth=nestlevel)
		if configMenuGameplay.value:
			menutext("-Gameplay",configMenuGameplay,txtcolornormal=BLUE,depth=nestlevel)
			nestlevel += 1
			menutext(f"Level Increase: {'On' if doLevelUp.value else 'Off'}",doLevelUp,depth=nestlevel,txtcolornormal=CYAN)
			if doLevelUp.value:
				menutext(f"Blocks per Level: {squaresPerLevel.value}",squaresPerLevel,depth=nestlevel+1)
				menutext(f"Ending level: {endLevel.value}",endLevel,depth=nestlevel+1)
			menutext(f"Grace Period: {gracePeriod.value}",gracePeriod,depth=nestlevel)
			menutext(f"Colors: {numberColors.value}",numberColors,depth=nestlevel)
		elif configMenuSpecials.value:
			menutext("-Specials",configMenuSpecials,txtcolornormal=BLUE,depth=nestlevel)
			nestlevel += 1
			if configMenuSpecialsCatalysts.value:
				menutext("-Catalysts",configMenuSpecialsCatalysts,txtcolornormal=RED,depth=nestlevel)
				nestlevel += 1
				menutext(f"Catalyst Chance (%): {catalystChance.value}",catalystChance,depth=nestlevel)
				menutext(f"+ Cat Chance (%): {catalystChanceIncrease.value}",catalystChanceIncrease,depth=nestlevel)
				menutext(f"Catalyst Timer: {catalystTimer.value}",catalystTimer,depth=nestlevel)
			elif configMenuSpecialsBombs.value:
				menutext("-Bombs",configMenuSpecialsBombs,txtcolornormal=RED,depth=nestlevel)
				nestlevel += 1
				menutext(f"Bombs: {'On' if bombEnable.value else 'Off'}",bombEnable,depth=nestlevel)
				menutext(f"Bomb Chance (%): {bombChance.value}",bombChance,depth=nestlevel)
				menutext(f"+ Bomb Chance (%): {bombChanceIncrease.value}",bombChanceIncrease,depth=nestlevel)
				menutext(f"Bomb Range: {bombRange.value}",bombRange,depth=nestlevel)
				menutext(f"Bomb Chain: {'On' if bombChain.value else 'Off'}",bombChain,depth=nestlevel)
			elif configMenuSpecialsErasers.value:
				menutext("-Erasers",configMenuSpecialsErasers,txtcolornormal=RED,depth=nestlevel)
				nestlevel += 1
				menutext(f"Erasers: {'On' if eraserEnable.value else 'Off'}",eraserEnable,depth=nestlevel)
				menutext(f"Eraser Chance (%): {eraserChance.value}",eraserChance,depth=nestlevel)
				menutext(f"+ Erase Chance (%): {eraserChanceIncrease.value}",eraserChanceIncrease,depth=nestlevel)
				menutext(f"Eraser Chain: {'On' if eraserChain.value else 'Off'}",eraserChain,depth=nestlevel)
				menutext(f"Rainbow Erasers: {'On' if eraserRainbowEnable.value else 'Off'}",eraserRainbowEnable,depth=nestlevel)
				menutext(f"All Erase Trash: {'On' if eraserTargetsTrash.value else 'Off'}",eraserTargetsTrash,depth=nestlevel)
			else:
				menutext("Catalysts",configMenuSpecialsCatalysts,txtcolornormal=RED,depth=nestlevel)
				menutext("Bombs",configMenuSpecialsBombs,txtcolornormal=RED,depth=nestlevel)
				menutext("Erasers",configMenuSpecialsErasers,txtcolornormal=RED,depth=nestlevel)
				menutext(f"Rainbow: {'On' if rainbowEnable.value else 'Off'}",rainbowEnable,depth=nestlevel)
				menutext(f"Rainbow Chance: {rainbowChance.value}",rainbowChance,depth=nestlevel)
				menutext(f"Trash: {'On' if trashEnable.value else 'Off'}",trashEnable,depth=nestlevel)
				menutext(f"Trash Chance: {trashChance.value}",trashChance,depth=nestlevel)
				
			
			
			
		elif configMenuBoard.value:
			menutext("-Board",configMenuBoard,txtcolornormal=BLUE,depth=nestlevel)
			nestlevel += 1
			menutext(f"Board Width: {boardWidth.value}",boardWidth,depth=nestlevel)
			menutext(f"Board Height: {boardHeight.value}",boardHeight,depth=nestlevel)
		else:
			menutext("Gameplay",configMenuGameplay,txtcolornormal=BLUE,depth=nestlevel)
			menutext("Specials",configMenuSpecials,txtcolornormal=BLUE,depth=nestlevel)
			menutext("Board",configMenuBoard,txtcolornormal=BLUE,depth=nestlevel)
	elif optionsMenu.value:
		menutext("-Options",optionsMenu,txtcolornormal=PINK,depth=nestlevel)
		nestlevel += 1
		menutext(f"Block Size: {blockSize.value}",blockSize,depth=nestlevel)
		menutext(f"Title Refresh: {titleBoardRefresh.value}",titleBoardRefresh,depth=nestlevel)
		menutext(f"Draw Bomb Range: {'On' if drawExtras.value else 'Off'}",drawExtras,depth=nestlevel)
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
		menutext("-Tutorials",tutorialsMenu,txtcolornormal=PINK)
		nestlevel += 1
		for x in tutorialpresets:
			menutext(x.displayname,x,txtcolornormal=CYAN,depth=nestlevel)
		'''menutext("Basic","tutorialbasic",txtcolornormal=CYAN,depth=nestlevel)
		menutext("Catalysts","tutorialcatalysts",txtcolornormal=CYAN,depth=nestlevel)
		menutext("Rainbow Squares","tutorialrainbow",txtcolornormal=CYAN,depth=nestlevel)
		menutext("Combos","tutorialcombo",txtcolornormal=CYAN,depth=nestlevel)
		menutext("Bombs","tutorialbombs",txtcolornormal=CYAN,depth=nestlevel)
		menutext("Hard Cascade/Mercy","tutorialmercy",txtcolornormal=CYAN,depth=nestlevel)
		menutext("Trash Squares","tutorialtrash",txtcolornormal=CYAN,depth=nestlevel)
		menutext("Erasers","tutorialerasers",txtcolornormal=CYAN,depth=nestlevel)'''
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
	if len(buttonlist) > cursor_pos: 
		if isinstance(buttonlist[cursor_pos],Config)  and not buttonlist[cursor_pos].tooltip is None:
			multitext(buttonlist[cursor_pos].tooltip,30,YELLOW,(50,600),True,SmallerFont,20)
		elif isinstance(buttonlist[cursor_pos],Preset)  and not buttonlist[cursor_pos].desc is None:
			multitext(buttonlist[cursor_pos].desc,30,YELLOW,(50,600),True,SmallerFont,20)

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
				menutext("Restart",presetTutorialBasic)
				menutext("Next tutorial",presetTutorialCatalysts)
			case 1:
				menutext("Restart",presetTutorialCatalysts)
				menutext("Next tutorial",presetTutorialRainbow)
				menutext("Previous tutorial",presetTutorialBasic)
			case 2:
				menutext("Restart",presetTutorialRainbow)
				menutext("Next tutorial",presetTutorialCombo)
				menutext("Previous tutorial",presetTutorialCatalysts)
			case 3:
				menutext("Restart",presetTutorialCombo)
				menutext("Next tutorial",presetTutorialBombs)
				menutext("Previous tutorial",presetTutorialRainbow)
			case 4:
				menutext("Restart",presetTutorialBombs)
				menutext("Next tutorial",presetTutorialMercy)
				menutext("Previous tutorial",presetTutorialCombo)
			case 5:
				menutext("Restart",presetTutorialMercy)
				menutext("Next tutorial",presetTutorialTrash)
				menutext("Previous tutorial",presetTutorialBombs)
			case 6:
				menutext("Restart",presetTutorialTrash)
				menutext("Next tutorial",presetTutorialErasers)
				menutext("Previous tutorial",presetTutorialMercy)
			case 7:
				menutext("Restart",presetTutorialErasers)
				#menutext("Next tutorial","tutorialmercy")
				menutext("Previous tutorial",presetTutorialTrash)
				
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
	global buttonlist, menuitemoffset, window, textoffset, selectedpreset
	
	buttonlist = []
	textoffset = 0
	match selectedpreset:
		case "Basic Tutorial":
			normaltext("Basic Tutorial", YELLOW, (50,30), False)
			
			normaltext("Controls", PINK, (50,150), True,font=SmallerFont,fontsize=20)
			multitext("Arrow keys/WASD to move.\nZXQE to rotate the block.\nUP to drop a piece.\nESCAPE to pause.\n", 20, WHITE, (50,150), True,SmallerFont,20,True)
			
			normaltext("Game Over:", PINK, (50,150), True,font=SmallerFont,fontsize=20)
			multitext("Don't let your stack reach the top or it's game over.", 20, WHITE, (50,150), True,SmallerFont,20,True)
			
			normaltext("Catalysts:", PINK, (50,150), True,font=SmallerFont,fontsize=20)
			multitext("Catalysts will clear all connected blocks of the same color.", 20, WHITE, (50,150), True,SmallerFont,20,True)
			
			normaltext("Chains:", PINK, (50,150), True,font=SmallerFont,fontsize=20)
			multitext("Connect many squares of the same color and use catalysts to clear them!", 20, WHITE, (50,150), True,SmallerFont,20,True)
		case "Catalyst Tutorial":
			normaltext("Catalyst Tutorial", YELLOW, (50,30), False)
			
			normaltext("Catalyst Explosion:", PINK, (50,150), True,font=SmallerFont,fontsize=20)
			multitext("When the red lines leave the bottom of the screen, all catalysts explode, clearing connected squares.", 20, WHITE, (50,150), True,SmallerFont,20,True)
			
			normaltext("Timer Extension:", PINK, (50,150), True,font=SmallerFont,fontsize=20)
			multitext("Placing another catalyst will increase the time until they explode.\n\nUse this to clear many squares at once!", 20, WHITE, (50,150), True,SmallerFont,20,True)
			
			
		case "Rainbow Tutorial":
			normaltext("Rainbow Tutorial", YELLOW, (50,30), False)
			
			normaltext("Rainbow Square:", PINK, (50,150), True,font=SmallerFont,fontsize=20)
			multitext("Rainbow squares connect to all other square colors.\n\nThey can be used to connect chains of different colors.\n\nUse these to extend your combos or clear many colors at once!", 20, WHITE, (50,150), True,SmallerFont,20,True)
		case "Combo Tutorial":
			normaltext("Combo Tutorial", YELLOW, (50,30), False)
			normaltext("Long Chains:", PINK, (50,150), True,font=SmallerFont,fontsize=20)
			multitext("Squares farther from their connected catalysts are worth many more points.\n\nMake long chains of connected squares to earn massive scores!", 20, WHITE, (50,150), True,SmallerFont,20,True)
			normaltext("Controls", PINK, (50,150), True,font=SmallerFont,fontsize=20)
			normaltext("SHIFT (Hold): Fast Cascade", WHITE, (50,150), True,font=SmallerFont,fontsize=20)
			normaltext("", WHITE, (50,150), True,font=SmallerFont,fontsize=20)
			
		case "Bomb Tutorial":
			normaltext("Bomb Tutorial", YELLOW, (50,30), False)
			normaltext("Bombs:", PINK, (50,150), True,font=SmallerFont,fontsize=20)
			multitext("When connected to a catalyst, a bomb will connect to all nearby squares of the same color.\n\nThey're excellent for clearing out many squares at once.\n\nHowever, they don't increase your chain anywhere near as fast as a continuous line.", 20, WHITE, (50,150), True,SmallerFont,20,True)
			
			normaltext("Rainbow Bombs:", PINK, (50,150), True,font=SmallerFont,fontsize=20)
			multitext("Rainbow bombs are rare, but can single-handedly clear out large parts of the board.", 20, WHITE, (50,150), True,SmallerFont,20,True)
		case "Mercy Tutorial":
			normaltext("Mercy Tutorial", YELLOW, (50,30), False)
			
			normaltext("Mercy:", PINK, (50,150), True,font=SmallerFont,fontsize=20)
			multitext("There are a few systems in place to make the game a bit easier, but they can be disabled.", 20, WHITE, (50,150), True,SmallerFont,20,True)
			
			normaltext("Above the Board:", PINK, (50,150), True,font=SmallerFont,fontsize=20)
			multitext("You can actually place blocks above the board, and so long as it does not enter the spawning space, it will not trigger a Game Over.", 20, WHITE, (50,150), True,SmallerFont,20,True)
			
			normaltext("Emergency Explosion:", PINK, (50,150), True,font=SmallerFont,fontsize=20)
			multitext("While the catalyst timer is active, triggering a Game Over by reaching the top of the board will instead instantly end the timer and explode all catalysts.\n\nWhether that explosion saves you is your own issue.", 20, WHITE, (50,150), True,SmallerFont,20,True)
			
		case "Trash Tutorial":
			normaltext("Trash Tutorial", YELLOW, (50,30), False)
			normaltext("Trash:", PINK, (50,150), True,font=SmallerFont,fontsize=20)
			multitext("Trash squares are an obstacle.\n\nAny color can connect to trash squares, but trash squares cannot continue a chain, even with other trash squares.", 20, WHITE, (50,150), True,SmallerFont,20,True)
			normaltext("Trash & Bombs:", PINK, (50,150), True,font=SmallerFont,fontsize=20)
			multitext("Bombs are an excellent way to remove trash squares, as any color of bomb can chain to trash squares.", 20, WHITE, (50,150), True,SmallerFont,20,True)
		case "Eraser Tutorial":
			normaltext("Erasers Tutorial", YELLOW, (50,30), False)
			normaltext("Erasers:", PINK, (50,150), True,font=SmallerFont,fontsize=20)
			multitext("When connected to a catalyst, an eraser will wipe out all squares of the same color on the board.", 20, WHITE, (50,150), True,SmallerFont,20,True)
			
			normaltext("Erasers & Rainbows:", PINK, (50,150), True,font=SmallerFont,fontsize=20)
			multitext("By default settings, erasers cannot connect to rainbow squares.\n\nIn addition, any rainbow erasers are instead converted into trash erasers.", 20, WHITE, (50,150), True,SmallerFont,20,True)
			
			normaltext("Erasers & Trash:", PINK, (50,150), True,font=SmallerFont,fontsize=20)
			multitext("By default, Trash erasers are the only erasers which can connect to trash squares.\n\nNotably, any square color can connect to a trash eraser.", 20, WHITE, (50,150), True,SmallerFont,20,True)
		case "tutorialcombo2":
			
			
			normaltext("Fast Cascade:", PINK, (50,150), True,font=SmallerFont,fontsize=20)
			multitext("All blocks will fall much faster. In addition, explosion effects will occur much faster.", 20, WHITE, (50,150), True,SmallerFont,20,True)
			
			normaltext("Catalyst Cascade:", PINK, (50,150), True,font=SmallerFont,fontsize=20)
			multitext("Just before a catalyst explosion occurs, all blocks currently in the air will fall to the ground instantly.\n\nDon't worry about being fast enough for something to fall!", 20, WHITE, (50,150), True,SmallerFont,20,True)
			

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
	if cursor_pos == menuitemoffset:
		itemtext += " <-"
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

def multitext(itemtext: str, charsperline=30, txtcolor= WHITE, source = (0,0), offset = True, font = DefaultFont,fontsize = 30,extraoffset=False):
	
	characternum = 0
	tempstr = ""
	for x in itemtext:
		if characternum > charsperline and x == ' ' or x == "\n":
			normaltext(tempstr, txtcolor=txtcolor,source=source,offset=offset,font=font,fontsize=fontsize)
			tempstr = ""
			characternum = 0
			continue
		tempstr += x
		characternum += 1
	if tempstr != "":
		normaltext(tempstr, txtcolor=txtcolor,source=source,offset=offset,font=font,fontsize=fontsize)
	if extraoffset:
		global textoffset
		textoffset += 1

init_board()
init_concatalyst_board()
# game loop
while running:
	#operationlength = time.perf_counter_ns()
	
	global_key_press_tracker()
	
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