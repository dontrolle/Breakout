from random import random

import pygame
from settings import *


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