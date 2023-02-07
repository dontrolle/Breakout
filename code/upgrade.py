import pygame
from settings import *


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
