def Debug( msg ):
	print msg

DIRECTION_UP = 0
DIRECTION_DOWN = 1
DIRECTION_LEFT = 2
DIRECTION_RIGHT = 3

from events import *

#------------------------------------------------------------------------------
class EventManager:
	"""this object is responsible for coordinating most communication
	between the Model, View, and Controller."""
	def __init__(self):
		from weakref import WeakKeyDictionary
		self.listeners = WeakKeyDictionary()
		self.eventQueue= []
		self.listenersToAdd = []
		self.listenersToRemove = []

	#----------------------------------------------------------------------
	def RegisterListener( self, listener ):
		self.listenersToAdd.append(listener)

	#----------------------------------------------------------------------
	def ActuallyUpdateListeners(self):
		for listener in self.listenersToAdd:
			self.listeners[ listener ] = 1
		for listener in self.listenersToRemove:
			if listener in self.listeners:
				del self.listeners[ listener ]

	#----------------------------------------------------------------------
	def UnregisterListener( self, listener ):
		self.listenersToRemove.append(listener)
		
	#----------------------------------------------------------------------
	def Post( self, event ):
		self.eventQueue.append(event)
		if isinstance(event, TickEvent):
			# Consume the event queue every Tick.
			self.ActuallyUpdateListeners()
			self.ConsumeEventQueue()
		else:
			Debug( "     Message: " + event.name )

	#----------------------------------------------------------------------
	def ConsumeEventQueue(self):
		i = 0
		while i < len( self.eventQueue ):
			event = self.eventQueue[i]
			for listener in self.listeners:
				# Note: a side effect of notifying the listener
				# could be that more events are put on the queue
				# or listeners could Register / Unregister
				old = len(self.eventQueue)
				listener.Notify( event )
			i += 1
			if self.listenersToAdd:
				self.ActuallyUpdateListeners()
		#all code paths that could possibly add more events to 
		# the eventQueue have been exhausted at this point, so 
		# it's safe to empty the queue
		self.eventQueue= []


#------------------------------------------------------------------------------
class KeyboardController:
	"""..."""
	def __init__(self, evManager, playerName=None):
		'''playerName is an optional argument; when given, this
		keyboardController will control only the specified player
		'''
		self.evManager = evManager
		self.evManager.RegisterListener( self )

		self.activePlayer = None
		self.playerName = playerName
		self.players = []

	#----------------------------------------------------------------------
	def Notify(self, event):
		if isinstance( event, PlayerJoinEvent ):
			self.players.append( event.player )
			if event.player.name == self.playerName:
				self.activePlayer = event.player
			if not self.playerName and not self.activePlayer:
				self.activePlayer = event.player

		if isinstance( event, GameSyncEvent ):
			game = event.game
			self.players = game.players[:] # copy the list
			if self.playerName and self.players:
				self.activePlayer = [p for p in self.players
				              if p.name == self.playerName][0]

		#if isinstance( event, SetControlPlayerEvent ):
			#player = event.player
			#self.activePlayer = player

		if isinstance( event, TickEvent ):
			#Handle Input Events
			for event in pygame.event.get():
				ev = None
				if event.type == QUIT:
					ev = QuitEvent()
				elif event.type == KEYDOWN \
				     and event.key == K_ESCAPE:
					ev = QuitEvent()
				elif event.type == KEYDOWN \
				     and event.key == K_p:
					import random
					rng = random.Random()
					name = str( rng.randrange(1,100) )
					if self.playerName:
						name = self.playerName
					playerData = {'name':name}
					ev = PlayerJoinRequest(playerData)

				elif event.type == KEYDOWN \
				     and event.key == K_o:
					self.activePlayer = self.players[1]
					self.players.reverse()

				elif event.type == KEYDOWN \
				     and event.key == K_c:
					if not self.activePlayer:
						continue
					charactor, sector = self.activePlayer.GetPlaceData()
					ev = CharactorPlaceRequest( 
					  self.activePlayer, 
					  charactor,
					  sector )

				elif event.type == KEYDOWN \
				     and event.key == K_UP:
					if not self.activePlayer:
						continue
					direction = DIRECTION_UP
					data = self.activePlayer.GetMoveData()
					ev = CharactorMoveRequest( 
					  self.activePlayer, 
					  data[0], 
					  direction )

				elif event.type == KEYDOWN \
				     and event.key == K_DOWN:
					if not self.activePlayer:
						continue
					direction = DIRECTION_DOWN
					data = self.activePlayer.GetMoveData()
					ev = CharactorMoveRequest( 
					  self.activePlayer, 
					  data[0], 
					  direction )

				elif event.type == KEYDOWN \
				     and event.key == K_LEFT:
					if not self.activePlayer:
						continue
					direction = DIRECTION_LEFT
					data = self.activePlayer.GetMoveData()
					ev = CharactorMoveRequest( 
					  self.activePlayer, 
					  data[0], 
					  direction )

				elif event.type == KEYDOWN \
				     and event.key == K_RIGHT:
					if not self.activePlayer:
						continue
					direction = DIRECTION_RIGHT
					data = self.activePlayer.GetMoveData()
					ev = CharactorMoveRequest( 
					  self.activePlayer, 
					  data[0], 
					  direction )

				elif event.type == KEYDOWN:
					ev = GameStartRequest()

				if ev:
					self.evManager.Post( ev )


#------------------------------------------------------------------------------
class CPUSpinnerController:
	"""..."""
	def __init__(self, evManager):
		self.evManager = evManager
		self.evManager.RegisterListener( self )

		self.keepGoing = 1

	#----------------------------------------------------------------------
	def Run(self):
		while self.keepGoing:
			event = TickEvent()
			self.evManager.Post( event )

	#----------------------------------------------------------------------
	def Notify(self, event):
		if isinstance( event, QuitEvent ):
			#this will stop the while loop from running
			self.keepGoing = False


import pygame
from pygame.locals import *

#------------------------------------------------------------------------------
class StatusBarSprite(pygame.sprite.Sprite):
	def __init__(self, evManager, group=None):
		pygame.sprite.Sprite.__init__(self, group)

		self.evManager = evManager
		self.evManager.RegisterListener( self )

		self.font = pygame.font.Font(None, 30)
		self.text = '.'
		self.image = self.font.render( self.text, 1, (255,0,0))
		self.rect  = self.image.get_rect()
		self.rect.move_ip( (0, 414) )

	#----------------------------------------------------------------------
	def update(self):
		self.image = self.font.render( self.text, 1, (255,0,0))
		self.rect  = self.image.get_rect()
		self.rect.move_ip( (0, 414) )

	#----------------------------------------------------------------------
	def Notify(self, event):
		if not isinstance( event, TickEvent ):
			self.text = event.name

#------------------------------------------------------------------------------
class SectorSprite(pygame.sprite.Sprite):
	def __init__(self, sector, group=None):
		pygame.sprite.Sprite.__init__(self, group)
		self.image = pygame.Surface( (128,128) )
		self.image.fill( (0,255,128) )

		self.sector = sector

#------------------------------------------------------------------------------
class CharactorSprite(pygame.sprite.Sprite):
	counter = 0
	def __init__(self, charactor, group=None, color=(0,0,0)):
		pygame.sprite.Sprite.__init__(self, group)

		charactorSurf = pygame.Surface( (64,64) )
		charactorSurf = charactorSurf.convert_alpha()
		charactorSurf.fill((0,0,0,0)) #make transparent
		pygame.draw.circle( charactorSurf, color, (32,32), 32 )
		self.image = charactorSurf
		self.rect  = charactorSurf.get_rect()

		self.order = CharactorSprite.counter
		CharactorSprite.counter += 1

		self.charactor = charactor
		self.moveTo = None

	#----------------------------------------------------------------------
	def update(self):
		if self.moveTo:
			self.rect.center = self.moveTo
			self.moveTo = None
			# offset the rect so that charactors don't draw exactly on
			# top of each other.
			self.rect.move_ip(self.order, self.order)

#------------------------------------------------------------------------------
class PygameView:
	def __init__(self, evManager):
		self.evManager = evManager
		self.evManager.RegisterListener( self )

		self.charactorColors = [ (255,0,0), (0,255,0) ]

		pygame.init()
		self.window = pygame.display.set_mode( (424,440) )
		pygame.display.set_caption( 'Example Game' )
		self.background = pygame.Surface( self.window.get_size() )
		self.background.fill( (0,0,0) )

		font = pygame.font.Font(None, 30)
		text = """Press SPACE BAR to start"""
		textImg = font.render( text, 1, (255,0,0))
		self.background.blit( textImg, (0,0) )
		text = """      P for new player"""
		textImg = font.render( text, 1, (255,0,0))
		self.background.blit( textImg, (0,1*font.get_linesize()) )
		text = """      C for new charactor"""
		textImg = font.render( text, 1, (255,0,0))
		self.background.blit( textImg, (0,2*font.get_linesize()) )
		text = """      O to switch players"""
		textImg = font.render( text, 1, (255,0,0))
		self.background.blit( textImg, (0,3*font.get_linesize()) )

		self.window.blit( self.background, (0,0) )
		pygame.display.flip()

		self.backSprites = pygame.sprite.RenderUpdates()
		self.frontSprites = pygame.sprite.RenderUpdates()


	#----------------------------------------------------------------------
	def ShowMap(self, gameMap):
		# clear the screen first
		self.background.fill( (0,0,0) )
		self.window.blit( self.background, (0,0) )
		pygame.display.flip()

		# use this squareRect as a cursor and go through the
		# columns and rows and assign the rect 
		# positions of the SectorSprites
		squareRect = pygame.Rect( (-128,10, 128,128 ) )

		column = 0
		for sector in gameMap.sectors:
			if column < 3:
				squareRect = squareRect.move( 138,0 )
			else:
				column = 0
				squareRect = squareRect.move( -(138*2), 138 )
			column += 1
			newSprite = SectorSprite( sector, self.backSprites )
			newSprite.rect = squareRect
			newSprite = None

		statusBarSprite = StatusBarSprite(self.evManager,self.backSprites)

	#----------------------------------------------------------------------
	def ShowCharactor(self, charactor):
		sector = charactor.sector
		if not sector:
			print "Charactor is not in a sector.  cannot show"
			return

		charactorSprite = self.GetCharactorSprite( charactor )
		if not charactorSprite:
			charactorSprite = CharactorSprite( self.frontSprites )
		sectorSprite = self.GetSectorSprite( sector )
		charactorSprite.rect.center = sectorSprite.rect.center

	#----------------------------------------------------------------------
	def MoveCharactor(self, charactor):
		charactorSprite = self.GetCharactorSprite( charactor )

		sector = charactor.sector
		sectorSprite = self.GetSectorSprite( sector )

		charactorSprite.moveTo = sectorSprite.rect.center

	#----------------------------------------------------------------------
	def GetCharactorSprite(self, charactor):
		#there will be only one
		for s in self.frontSprites.sprites():
			if s.charactor is charactor:
				return s

		col = self.charactorColors[0]
		print "new color: ", col
		self.charactorColors.reverse()
		return CharactorSprite(charactor, self.frontSprites, col)

	#----------------------------------------------------------------------
	def GetSectorSprite(self, sector):
		for s in self.backSprites:
			if hasattr(s, "sector") and s.sector == sector:
				return s


	#----------------------------------------------------------------------
	def Notify(self, event):
		if isinstance( event, TickEvent ):
			#Draw Everything
			self.backSprites.clear( self.window, self.background )
			self.frontSprites.clear( self.window, self.background )

			self.backSprites.update()
			self.frontSprites.update()

			dirtyRects1 = self.backSprites.draw( self.window )
			dirtyRects2 = self.frontSprites.draw( self.window )
			
			dirtyRects = dirtyRects1 + dirtyRects2
			pygame.display.update( dirtyRects )


		elif isinstance( event, MapBuiltEvent ):
			gameMap = event.map
			self.ShowMap( gameMap )

		elif isinstance( event, CharactorPlaceEvent ):
			self.ShowCharactor( event.charactor )

		elif isinstance( event, CharactorMoveEvent ):
			self.MoveCharactor( event.charactor )

		elif isinstance( event, GameSyncEvent ):
			print 'Pygame View syncing to game state', event, event.game.__dict__
			game = event.game
			if game.state == Game.STATE_PREPARING:
				return
			print 'Pygame View syncing to game state'
			self.ShowMap( game.map )
			for player in game.players:
				for charactor in player.charactors:
					self.ShowCharactor( charactor )

#------------------------------------------------------------------------------
class Game:
	"""..."""

	STATE_PREPARING = 'preparing'
	STATE_RUNNING = 'running'
	STATE_PAUSED = 'paused'

	#----------------------------------------------------------------------
	def __init__(self, evManager):
		self.evManager = evManager
		self.evManager.RegisterListener( self )

		self.state = Game.STATE_PREPARING
		
		self.players = [ ]
		self.maxPlayers = 2
		self.map = Map( evManager )

	#----------------------------------------------------------------------
	def Start(self):
		self.map.Build()
		self.state = Game.STATE_RUNNING
		ev = GameStartedEvent( self )
		self.evManager.Post( ev )

	#----------------------------------------------------------------------
	def AddPlayer(self, player):
		self.players.append( player )
		player.SetGame( self )
		ev = PlayerJoinEvent( player )
		self.evManager.Post( ev )


	#----------------------------------------------------------------------
	def Notify(self, event):
		if isinstance( event, GameStartRequest ):
			if self.state == Game.STATE_PREPARING:
				self.Start()

		if isinstance( event, PlayerJoinRequest ):
			if self.state != Game.STATE_PREPARING:
				print "Players can not join after Game start"
				return
			if len(self.players) >= self.maxPlayers:
				print "Maximum players already joined"
				return
			player = Player( self.evManager )
			player.SetData( event.playerDict )
			self.AddPlayer( player )


#------------------------------------------------------------------------------
class Player(object):
	"""..."""
	def __init__(self, evManager):
		self.evManager = evManager
		self.game = None
		self.name = ""
		self.evManager.RegisterListener( self )

		self.charactors = [ Charactor(evManager) ]

	#----------------------------------------------------------------------
	def __str__(self):
		return '<Player %s %s>' % (self.name, id(self))

	#----------------------------------------------------------------------
	def GetPlaceData( self ):
		charactor = self.charactors[0]
		gameMap = self.game.map
		sector =  gameMap.sectors[gameMap.startSectorIndex]
		return [charactor, sector]

	#----------------------------------------------------------------------
	def GetMoveData( self ):
		return [self.charactors[0]]

	#----------------------------------------------------------------------
	def SetGame( self, game ):
		self.game = game

	#----------------------------------------------------------------------
	def SetData( self, playerDict ):
		self.name = playerDict['name']

	#----------------------------------------------------------------------
	def Notify(self, event):
		pass
		#if isinstance( event, PlayerJoinEvent):
			#if event.player is self:

#------------------------------------------------------------------------------
class Charactor:
	"""..."""

	STATE_INACTIVE = 0
	STATE_ACTIVE = 1

	def __init__(self, evManager):
		self.evManager = evManager
		self.evManager.RegisterListener( self )

		self.sector = None
		self.state = Charactor.STATE_INACTIVE

	#----------------------------------------------------------------------
	def __str__(self):
		return '<Charactor %s>' % id(self)

	#----------------------------------------------------------------------
	def Move(self, direction):
		if self.state == Charactor.STATE_INACTIVE:
			return

		if self.sector.MovePossible( direction ):
			newSector = self.sector.neighbors[direction]
			self.sector = newSector
			ev = CharactorMoveEvent( self )
			self.evManager.Post( ev )

	#----------------------------------------------------------------------
	def Place(self, sector):
		self.sector = sector
		self.state = Charactor.STATE_ACTIVE

		ev = CharactorPlaceEvent( self )
		self.evManager.Post( ev )

	#----------------------------------------------------------------------
	def Notify(self, event):
		if isinstance( event, CharactorPlaceRequest ) \
		 and event.charactor == self:
			self.Place( event.sector )

		elif isinstance( event, CharactorMoveRequest ) \
		  and event.charactor == self:
			self.Move( event.direction )

#------------------------------------------------------------------------------
class Map:
	"""..."""

	STATE_PREPARING = 0
	STATE_BUILT = 1


	#----------------------------------------------------------------------
	def __init__(self, evManager):
		self.evManager = evManager
		#self.evManager.RegisterListener( self )

		self.state = Map.STATE_PREPARING

		self.sectors = []
		self.startSectorIndex = 0

	#----------------------------------------------------------------------
	def Build(self):
		for i in range(9):
			self.sectors.append( Sector(self.evManager) )

		self.sectors[3].neighbors[DIRECTION_UP] = self.sectors[0]
		self.sectors[4].neighbors[DIRECTION_UP] = self.sectors[1]
		self.sectors[5].neighbors[DIRECTION_UP] = self.sectors[2]
		self.sectors[6].neighbors[DIRECTION_UP] = self.sectors[3]
		self.sectors[7].neighbors[DIRECTION_UP] = self.sectors[4]
		self.sectors[8].neighbors[DIRECTION_UP] = self.sectors[5]

		self.sectors[0].neighbors[DIRECTION_DOWN] = self.sectors[3]
		self.sectors[1].neighbors[DIRECTION_DOWN] = self.sectors[4]
		self.sectors[2].neighbors[DIRECTION_DOWN] = self.sectors[5]
		self.sectors[3].neighbors[DIRECTION_DOWN] = self.sectors[6]
		self.sectors[4].neighbors[DIRECTION_DOWN] = self.sectors[7]
		self.sectors[5].neighbors[DIRECTION_DOWN] = self.sectors[8]

		self.sectors[1].neighbors[DIRECTION_LEFT] = self.sectors[0]
		self.sectors[2].neighbors[DIRECTION_LEFT] = self.sectors[1]
		self.sectors[4].neighbors[DIRECTION_LEFT] = self.sectors[3]
		self.sectors[5].neighbors[DIRECTION_LEFT] = self.sectors[4]
		self.sectors[7].neighbors[DIRECTION_LEFT] = self.sectors[6]
		self.sectors[8].neighbors[DIRECTION_LEFT] = self.sectors[7]

		self.sectors[0].neighbors[DIRECTION_RIGHT] = self.sectors[1]
		self.sectors[1].neighbors[DIRECTION_RIGHT] = self.sectors[2]
		self.sectors[3].neighbors[DIRECTION_RIGHT] = self.sectors[4]
		self.sectors[4].neighbors[DIRECTION_RIGHT] = self.sectors[5]
		self.sectors[6].neighbors[DIRECTION_RIGHT] = self.sectors[7]
		self.sectors[7].neighbors[DIRECTION_RIGHT] = self.sectors[8]

		self.state = Map.STATE_BUILT

		ev = MapBuiltEvent( self )
		self.evManager.Post( ev )

#------------------------------------------------------------------------------
class Sector:
	"""..."""
	def __init__(self, evManager):
		self.evManager = evManager
		#self.evManager.RegisterListener( self )

		self.neighbors = range(4)

		self.neighbors[DIRECTION_UP] = None
		self.neighbors[DIRECTION_DOWN] = None
		self.neighbors[DIRECTION_LEFT] = None
		self.neighbors[DIRECTION_RIGHT] = None

	#----------------------------------------------------------------------
	def MovePossible(self, direction):
		if self.neighbors[direction]:
			return 1


#------------------------------------------------------------------------------
def main():
	"""..."""
	evManager = EventManager()

	keybd = KeyboardController( evManager )
	spinner = CPUSpinnerController( evManager )
	pygameView = PygameView( evManager )
	game = Game( evManager )
	
	spinner.Run()

if __name__ == "__main__":
	main()
