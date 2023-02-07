import pygame
from settings import *


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
    self.hearts = PLAYER_START_HEARTS
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
