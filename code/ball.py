from random import choice

import pygame
from settings import *


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
    # reset speed - TODO: too easy, or maybe configurable whether it's done?
    # self.speed = BALL_INIT_SPEED
   
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

      if self.rect.top > WINDOW_HEIGHT:
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
