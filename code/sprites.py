import pygame
from settings import *
from random import choice, random

class Upgrade(pygame.sprite.Sprite):
	def __init__(self,pos,upgrade_type,groups):
		super().__init__(groups)
		self.upgrade_type = upgrade_type
		self.image = pygame.image.load(f'../graphics/upgrades/{upgrade_type}.png').convert_alpha()
		self.rect = self.image.get_rect(midtop = pos)

		self.pos = pygame.math.Vector2(self.rect.topleft)
		self.speed = 300

	def update(self,dt):
		self.pos.y += self.speed * dt
		self.rect.y = round(self.pos.y)

		if self.rect.top > WINDOW_HEIGHT + 100:
			self.kill()

class Projectile(pygame.sprite.Sprite):
	def __init__(self,pos,surface,groups):
		super().__init__(groups)
		self.image = surface
		self.rect = self.image.get_rect(midbottom = pos)

		self.pos = pygame.math.Vector2(self.rect.topleft)
		self.speed = 300

	def update(self,dt):
		self.pos.y -= self.speed * dt
		self.rect.y = round(self.pos.y)

		if self.rect.bottom <= -100:
			self.kill()

class Player(pygame.sprite.Sprite):
	def __init__(self,groups,surfacemaker):
		super().__init__(groups)

		# setup
		self.display_surface = pygame.display.get_surface()
		self.surfacemaker = surfacemaker

		# note - a lot of magic numbers here. Notable 28 comes from 2*14 - the pixel height of the topleft and bottomleft
		player_pad_height = max(28, (WINDOW_HEIGHT // 20) // 4 * 3)
		self.image = surfacemaker.get_surf('player',(WINDOW_WIDTH // 10, player_pad_height))

		# position and rect
		self.rect = self.image.get_rect(midbottom = (WINDOW_WIDTH // 2,WINDOW_HEIGHT - 20))
		self.pos = pygame.math.Vector2(self.rect.topleft)


		# hitbox - slightly larger to make edge-collisions a bit more friendly
		self.player_width_hitbox_padding = PLAYER_WIDTH_HITBOX_PADDING
		self.hitbox = self.rect.inflate(self.player_width_hitbox_padding,0)

		# direction and speed
		self.direction = pygame.math.Vector2()
		self.speed = PLAYER_SPEED
  
		# properties
		self.hearts = 3
		self.points = 0
		self.score_update_since_last = True

		# laser
		self.laser_amount = 0
		self.laser_surf = pygame.image.load('../graphics/other/laser.png').convert_alpha()
		self.laser_rects = []

	def add_points(self, amount):
		self.points += amount
		self.score_update_since_last = True

	def input(self):
		keys = pygame.key.get_pressed()
		if keys[pygame.K_RIGHT]:
			self.direction.x = 1
		elif keys[pygame.K_LEFT]:
			self.direction.x = -1
		elif keys[pygame.K_PAGEUP]:
			self.player_width_hitbox_padding += 2
			self.inflate_pad(2)
		elif keys[pygame.K_PAGEDOWN]:
			self.player_width_hitbox_padding -= 2
			self.inflate_pad(-2)
		else:
			self.direction.x = 0

	def screen_constraint(self):
		if self.rect.right > WINDOW_WIDTH:
			self.rect.right = WINDOW_WIDTH
			self.pos.x = self.rect.x
		if self.rect.left < 0:
			self.rect.left = 0
			self.pos.x = self.rect.x

	def inflate_pad(self, amount, inflate_rect = False):
		self.hitbox.inflate_ip(amount, 0)
		if inflate_rect:
			self.rect.inflate_ip(amount, 0)
			self.image = self.surfacemaker.get_surf('player',(self.rect.width,self.rect.height))
			self.pos.x = self.rect.x

	def upgrade(self,upgrade_type):
		if upgrade_type == 'speed':
			self.speed += 50
			
		if upgrade_type == 'heart':
			self.hearts += 1

		if upgrade_type == 'size':
			self.inflate_pad(self.rect.width * 0.1, True)

		if upgrade_type == 'laser':
			self.laser_amount += 1

	def remove_upgrade(self,upgrade_type):
		if upgrade_type == 'speed':
			self.speed -= 50
		
		## should not
		if upgrade_type == 'heart':
			self.hearts -= 1

		if upgrade_type == 'size':
			self.inflate_pad(-self.rect.width * 0.1, True)

		if upgrade_type == 'laser':
			self.laser_amount -= 1

	def display_lasers(self):
		self.laser_rects = []
		if self.laser_amount > 0:
			divider_length = self.rect.width / (self.laser_amount + 1)
			for i in range(self.laser_amount):
				x = self.rect.left + divider_length * (i + 1)
				laser_rect = self.laser_surf.get_rect(midbottom = (x,self.rect.top))
				self.laser_rects.append(laser_rect)

			for laser_rect in self.laser_rects:
				self.display_surface.blit(self.laser_surf,laser_rect)

	def display_debug(self):
		# rect and hitbox
		if self.hitbox.width > self.rect.width:
			pygame.draw.rect(self.display_surface, "brown1", self.hitbox)
		
		pygame.draw.rect(self.display_surface, "green", self.rect)
  
		if self.hitbox.width <= self.rect.width:
			pygame.draw.rect(self.display_surface, "brown1", self.hitbox)

		# blue guides
		rect = pygame.Rect(0,WINDOW_HEIGHT - 10, 10, 10)
		pygame.draw.rect(self.display_surface, "blue", rect)

		rect = pygame.Rect(WINDOW_WIDTH // 2 - 5, WINDOW_HEIGHT - 10, 10, 10)
		pygame.draw.rect(self.display_surface, "blue", rect)
  
		rect = pygame.Rect(WINDOW_WIDTH - 10, WINDOW_HEIGHT - 10, 10, 10)
		pygame.draw.rect(self.display_surface, "blue", rect)
   
	def update(self,dt):
		self.old_hitbox = self.hitbox.copy()
		self.input()
		self.pos.x += self.direction.x * self.speed * dt
		self.rect.x = round(self.pos.x)
		self.hitbox.centerx = self.rect.centerx
		self.screen_constraint()
		self.display_lasers()

class Ball(pygame.sprite.Sprite):
	def __init__(self,groups,player,blocks,on_loose_heart):
		super().__init__(groups)

		# collision objects
		self.player = player
		self.blocks = blocks

		# graphics setup
		self.image = pygame.image.load('../graphics/other/ball.png').convert_alpha()

		# position setup
		self.rect = self.image.get_rect(midbottom = player.rect.midtop)
		self.old_rect = self.rect.copy()
		self.pos = pygame.math.Vector2(self.rect.topleft)
		self.direction = pygame.math.Vector2((choice((1,-1)),-1))
		self.speed = BALL_INIT_SPEED
  
		# save game reset callback
		self.on_loose_heart = on_loose_heart

		# active
		self.active = False

		# sounds
		self.impact_sound = pygame.mixer.Sound('../sounds/impact.wav')
		self.impact_sound.set_volume(0.1)

		self.fail_sound = pygame.mixer.Sound('../sounds/fail.wav')
		self.fail_sound.set_volume(0.1)

	def reset(self):  
		self.active = False
		self.direction.y = -1
		self.player.hearts -= 1
		self.speed = BALL_INIT_SPEED
   
	def window_collision(self,direction):
		if direction == 'horizontal':
			if self.rect.left < 0:
				self.rect.left = 0
				self.pos.x = self.rect.x
				self.direction.x *= -1

			if self.rect.right > WINDOW_WIDTH:
				self.rect.right = WINDOW_WIDTH
				self.pos.x = self.rect.x
				self.direction.x *= -1

		if direction == 'vertical':
			if self.rect.top < 0:
				self.rect.top = 0
				self.pos.y = self.rect.y
				self.direction.y *= -1

			if self.rect.bottom > WINDOW_HEIGHT:
				self.fail_sound.play()
				self.on_loose_heart()
				
	def collision(self,direction):
		# find overlapping objects 
		overlap_sprites = pygame.sprite.spritecollide(self,self.blocks,False)
		if self.rect.colliderect(self.player.hitbox):
			overlap_sprites.append(self.player)
   
		if overlap_sprites:
			if direction == 'horizontal':
				for sprite in overlap_sprites:
					# ball collides on left of sprite
					if self.rect.right >= sprite.hitbox.left and self.old_rect.right <= sprite.old_hitbox.left:
						# move to border of sprite
						self.rect.right = sprite.hitbox.left - 1
						self.pos.x = self.rect.x
						# adjust direction
						self.direction.x *= -1
						self.impact_sound.play()

					if self.rect.left <= sprite.hitbox.right and self.old_rect.left >= sprite.old_hitbox.right:
						self.rect.left = sprite.hitbox.right + 1
						self.pos.x = self.rect.x
						self.direction.x *= -1
						self.impact_sound.play()

					if getattr(sprite,'health',None):
						sprite.get_damage(1)

	   	#For vertical collision from above (only with the pad?), we divide it into zones and set direction according to the hit-zone
			if direction == 'vertical':
				for sprite in overlap_sprites:
					# ball collides sprite from above
					if self.rect.bottom >= sprite.hitbox.top and self.old_rect.bottom <= sprite.old_hitbox.top:
       			# move to border of sprite
						self.rect.bottom = sprite.hitbox.top - 1
						self.pos.y = self.rect.y
						# handle player-pad specially
						if sprite == self.player:
							# determine fraction of width for ball position
							pos_fraction = (self.rect.centerx - sprite.hitbox.left) / sprite.hitbox.width
							# adjust direction of sprite
							for (limit, (dx, dy)) in COLLISION_DIRECTION_VECTORS.items():
								if(pos_fraction > limit):
									if(dy == -1):
										self.direction.y *= -1
									else:
										# we simply set the direction directly
										self.direction.y = dy
										self.direction.x = dx
									break
						else:
							self.direction.y *= -1
						self.impact_sound.play()

					if self.rect.top <= sprite.hitbox.bottom and self.old_rect.top >= sprite.old_hitbox.bottom:
						self.rect.top = sprite.hitbox.bottom + 1
						self.pos.y = self.rect.y
						self.direction.y *= -1
						self.impact_sound.play()

					if getattr(sprite,'health',None):
						sprite.get_damage(1)

	def update(self,dt):
		if self.active:

			if self.direction.magnitude() != 0:
				self.direction = self.direction.normalize()

			# create old rect
			# TODO: Migrate to separate hitbox and old_hitbox for Ball also
			self.old_rect = self.rect.copy()

			# horizontal movement + collision
			self.pos.x += self.direction.x * self.speed * dt
			self.rect.x = round(self.pos.x)
			self.collision('horizontal')
			self.window_collision('horizontal')

			# vertical movement + collision
			self.pos.y += self.direction.y * self.speed * dt
			self.rect.y= round(self.pos.y)
			self.collision('vertical')
			self.window_collision('vertical')
		else:
			self.rect.midbottom = self.player.rect.midtop
			self.pos = pygame.math.Vector2(self.rect.topleft)

class Block(pygame.sprite.Sprite):
	def __init__(self,block_type,pos,groups,surfacemaker,player,create_upgrade):
		super().__init__(groups)
		self.surfacemaker = surfacemaker
		self.player = player
		(health, block_name, points) = BLOCK_DEFS[block_type]
		self.image = self.surfacemaker.get_surf(block_name,(BLOCK_WIDTH, BLOCK_HEIGHT))
		self.rect = self.image.get_rect(topleft = pos)
		self.hitbox = self.rect.copy()
		self.old_hitbox = self.rect.copy()

		# damage information
		self.health = health
	
		# points
		self.points = points

		# upgrade
		self.create_upgrade = create_upgrade

	def get_damage(self,amount):
		self.health -= amount

		if self.health > 0:
			self.image = self.surfacemaker.get_surf(BLOCK_TYPE_BY_HEALTH[self.health],(BLOCK_WIDTH, BLOCK_HEIGHT))
		else:
			if random() < UPGRADE_CHANCE:
				self.create_upgrade(self.rect.center)
			self.player.add_points(self.points)
			self.kill()