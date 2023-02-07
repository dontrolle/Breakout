import pygame

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
