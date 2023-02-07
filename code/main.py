import json
import sys
import time
from operator import itemgetter
from os import makedirs
from pathlib import Path
from random import choice

import pygame
from crt import CRT
from settings import *
from sprites import Ball, Block, Player, Projectile, Upgrade
from surfacemaker import SurfaceMaker


class Game:
  def __init__(self):
    
    # general setup
    pygame.init()
    self.display_surface = pygame.display.set_mode((WINDOW_WIDTH,WINDOW_HEIGHT))
    pygame.display.set_caption('Breakout')
    self.clock = pygame.time.Clock()

    # background
    self.bg = self.create_bg()

    # sprite group setup
    self.all_sprites = pygame.sprite.Group()
    self.block_sprites = pygame.sprite.Group()
    self.upgrade_sprites = pygame.sprite.Group()
    self.projectile_sprites = pygame.sprite.Group()

    # setup
    self.surfacemaker = SurfaceMaker()
    self.player = Player(self.all_sprites,self.surfacemaker)
    self.stage_setup()
    self.ball = Ball(self.all_sprites,self.player,self.block_sprites,self.reset_after_life_loss)

    # debug info
    self.debug = True
    # ... with input delay
    self.last_debug_press = 0
  
    # highscores
    self.highscore_dir_path = Path.home().joinpath(HIGHSCORE_FILE_DIR)

    if not Path.exists(self.highscore_dir_path):
      makedirs(self.highscore_dir_path)
    
    self.highscore_file_path = self.highscore_dir_path.joinpath(HIGHSCORE_FILE_NAME)
    self.read_highscores()
  
    # hearts
    self.heart_surf = pygame.image.load('../graphics/other/heart.png').convert_alpha()
  
    # is game over?
    self.game_over = False
  
    # score
    self.score_font = pygame.font.Font('freesansbold.ttf', 24)
    self.text_surf = None
    self.text_rect = None
    self.player.score_update_since_last = True

    # messages
    self.message_font = pygame.font.Font('freesansbold.ttf', 42)
    self.player_name_prompt = self.message_font.render("Name:", True, 'chocolate')
    self.player_name_prompt_rect = self.player_name_prompt.get_rect()
    self.player_name_prompt_rect.center = (WINDOW_WIDTH // 2 - (self.player_name_prompt_rect.width // 2), WINDOW_HEIGHT // 2)
    self.game_over_text = self.message_font.render("Game Over", True, "crimson")
    self.game_over_text_rect = self.game_over_text.get_rect()
    self.game_over_text_rect.center = (WINDOW_WIDTH // 2, WINDOW_HEIGHT - self.game_over_text_rect.height - 60)  
  
    # projectile
    self.projectile_surf = pygame.image.load('../graphics/other/projectile.png').convert_alpha()
    self.can_shoot = True
    self.shoot_time = 0
  
    # upgrades
    self.upgrade_running_timers = []

    # ball
    self.last_speed_inc_time = 0
  
    # crt
    if(WITH_CRT):
      self.crt = CRT()
   
    # sounds and music
    self.music_on = False

    self.laser_sound = pygame.mixer.Sound('../sounds/laser.wav')
    self.laser_sound.set_volume(0.1)

    self.powerup_sound = pygame.mixer.Sound('../sounds/powerup.wav')
    self.powerup_sound.set_volume(0.1)

    self.powerdown_sound = pygame.mixer.Sound('../sounds/powerdown.wav')
    self.powerdown_sound.set_volume(0.1)

    self.laserhit_sound = pygame.mixer.Sound('../sounds/laser_hit.wav')
    self.laserhit_sound.set_volume(0.02)
  
    if(self.music_on):
      self.music = pygame.mixer.Sound('../sounds/music.wav')
      self.music.set_volume(0.1)
      self.music.play(loops = -1)

  def write_highscores(self):
    # ensure highscores are sorted after possibly inserting new ones
    self.sort_highscores()
    with open(self.highscore_file_path, 'w', encoding="utf-8") as f:
      json.dump(self.highscores[0:NO_OF_POSITIONS_IN_HIGHSCORE_FILE], f)
      if self.debug:   
        print("highscores saved:")
        print(self.highscores)
    
  def read_highscores(self):
    with open(self.highscore_file_path, encoding="utf-8") as f:
      self.highscores = json.load(f)
      # ensure highscores are sorted after loading
      self.sort_highscores()
      if self.debug:
        print("highscores loaded:")
        print(self.highscores)

  def sort_highscores(self):
    self.highscores = sorted(self.highscores, key=itemgetter(1), reverse=True)

  def create_upgrade(self,pos):
    upgrade_type = choice(UPGRADES)
    Upgrade(pos,upgrade_type,[self.all_sprites,self.upgrade_sprites])

  def create_bg(self):
    bg_original = pygame.image.load('../graphics/other/bg.png').convert()
    scale_factor = WINDOW_HEIGHT / bg_original.get_height()
    scaled_width = bg_original.get_width() * scale_factor
    scaled_height = bg_original.get_height() * scale_factor
    scaled_bg = pygame.transform.scale(bg_original,(scaled_width,scaled_height)) 
    return scaled_bg

  def stage_setup(self):
    # cycle through all rows and columns of BLOCK MAP
    for row_index, row in enumerate(BLOCK_MAP):
      for col_index, col in enumerate(row):
        if col != ' ':
          # find the x and y position for each individual block
          x = col_index * (BLOCK_WIDTH + GAP_SIZE) + GAP_SIZE // 2
          y = TOP_OFFSET + row_index * (BLOCK_HEIGHT + GAP_SIZE) + GAP_SIZE // 2
          Block(col,(x,y),[self.all_sprites,self.block_sprites],self.surfacemaker,self.player,self.create_upgrade)

  def display_hearts(self):
    for i in range(self.player.hearts):
      x = 2 + i * (self.heart_surf.get_width() + 2)
      self.display_surface.blit(self.heart_surf,(x,4))

  def display_score(self):
    # cache rendered surface (and rect) - adding a bit of complexity
    if self.player.score_update_since_last:
      self.text_surf = self.score_font.render(str(self.player.points), True, 'chocolate')
      self.text_rect = self.text_surf.get_rect()
      self.text_rect.x = WINDOW_WIDTH - self.text_rect.width - 4
      self.text_rect.y = 4
      self.player.score_update_since_last = False

    self.display_surface.blit(self.text_surf, self.text_rect)

  def display_debug(self):
    self.player.display_debug()
    fps_overlay = self.score_font.render("fps: " + str(int(self.clock.get_fps())), True, "yellow")
    fps_rect = fps_overlay.get_rect()
    fps_rect.x = WINDOW_WIDTH - fps_rect.width - 4
    fps_rect.y = WINDOW_HEIGHT - fps_rect.height - 4
    self.display_surface.blit(fps_overlay, fps_rect)

  def upgrade_collision(self):
    # this doesn't use the hitbox used for ball collisions, but I think that's ok
    overlap_sprites = pygame.sprite.spritecollide(self.player,self.upgrade_sprites,True)
    for sprite in overlap_sprites:
      self.player.upgrade(sprite.upgrade_type)
      self.powerup_sound.play()
      if(sprite.upgrade_type in TIMED_UPGRADES):
        time = pygame.time.get_ticks()
        self.upgrade_running_timers.append((time, sprite.upgrade_type))

  def create_projectile(self):
    self.laser_sound.play()
    for projectile in self.player.laser_rects:
      Projectile(
        projectile.midtop - pygame.math.Vector2(0,30),
        self.projectile_surf,
        [self.all_sprites, self.projectile_sprites])

  def laser_timer(self):
    if pygame.time.get_ticks() - self.shoot_time >= 500:
      self.can_shoot = True
  
  def upgrade_timers(self):
    to_remove = []
    for (index, (timer, upgrade_type)) in enumerate(self.upgrade_running_timers):
      if(pygame.time.get_ticks() - timer > TIMED_UPGRADES_LAST_IN_TICKS):
        self.player.remove_upgrade(upgrade_type)
        self.powerdown_sound.play()
        to_remove.append(index)
    # now remove timers that fired - in reverse order, to preserve indexes in self.upgrade_running_timers
    to_remove.reverse()
    for index in to_remove:
      del self.upgrade_running_timers[index]

  def ball_speed_timer(self):
    ticks = pygame.time.get_ticks()
    if ticks - self.last_speed_inc_time >= BALL_SPEED_INTERVAL:
      self.ball.speed += BALL_SPEED_INC
      self.last_speed_inc_time = ticks

  def projectile_block_collision(self):
    for projectile in self.projectile_sprites:
      overlap_sprites  = pygame.sprite.spritecollide(projectile,self.block_sprites,False)
      if overlap_sprites:
        for sprite in overlap_sprites:
          sprite.get_damage(1)
        projectile.kill()
        self.laserhit_sound.play()

  def reset_after_life_loss(self):
    # reset upgrade-timers and remove upgrades from player
    for ((_, upgrade_type)) in self.upgrade_running_timers:
        self.player.remove_upgrade(upgrade_type)
    
    self.upgrade_running_timers.clear()

    # reset ball and ball timer
    self.ball.reset()
    self.last_speed_inc_time = pygame.time.get_ticks()
  
  def prompt_for_player_name(self):
    self.display_surface.fill(0)
    self.display_surface.blit(self.player_name_prompt, self.player_name_prompt_rect)
    pygame.display.update()
    pygame.event.clear()
    # get name
    name = ""
    while True:
      for evt in pygame.event.get():
        if evt.type == pygame.KEYDOWN:
          if evt.unicode.isalpha():
            name += evt.unicode
          elif evt.key == pygame.K_BACKSPACE:
            name = name[:-1]
          elif evt.key == pygame.K_RETURN or evt.key == pygame.K_ESCAPE:
            return name
        elif evt.type == pygame.QUIT:
          pygame.quit()
          sys.exit()
      self.display_surface.fill(0)
      self.display_surface.blit(self.player_name_prompt, self.player_name_prompt_rect)
      name_block = self.message_font.render(name, True, "red")
      name_rect = name_block.get_rect()
      name_rect.left = self.player_name_prompt_rect.right + 5
      name_rect.bottom = self.player_name_prompt_rect.bottom
      self.display_surface.blit(name_block, name_rect)
      pygame.display.update()
 
  def end_game(self):
    player_name = self.prompt_for_player_name()
  
    if player_name and self.player.points > 0:
      self.highscores.append([player_name, self.player.points])
      self.write_highscores()

    # TODO: Give option of playing again
    # TODO: Show highscores (also at game start)
    play_again = False
    if not play_again:
      pygame.quit()
      sys.exit()

  def display_end_game_splash(self):
    self.display_surface.blit(self.game_over_text, self.game_over_text_rect)		

  def run(self):
    last_time = time.time()
    while True:
      
      # delta time
      dt = time.time() - last_time
      last_time = time.time()
   
      # advance fps clock
      self.clock.tick()
   
      if self.player.hearts <= 0:
        self.game_over = True

      # event loop
      for event in pygame.event.get():
        if event.type == pygame.QUIT or self.game_over:
          self.end_game()
        # note for future: I find it a bit hacky that keypresses are handled both here and in player
        if event.type == pygame.KEYDOWN:
          if event.key == pygame.K_SPACE:
            self.ball.active = True
            if self.can_shoot:
              self.create_projectile()
              self.can_shoot = False
              self.shoot_time = pygame.time.get_ticks()
          elif event.key == pygame.K_F12:
            if pygame.time.get_ticks() - self.last_debug_press >= 200:
              self.debug = not self.debug
              self.last_debug_press = pygame.time.get_ticks()

      # draw bg
      #self.display_surface.blit(self.bg,(0,0))
      self.display_surface.fill(0)
      
      # update the game
      self.all_sprites.update(dt)
      self.upgrade_collision()
      self.laser_timer()
      self.projectile_block_collision()
      self.upgrade_timers()
      self.ball_speed_timer()

      # draw the frame
      self.all_sprites.draw(self.display_surface)
      self.display_hearts()
      self.display_score()
      if self.game_over:
        self.display_end_game_splash()
      if self.debug:
        self.display_debug()

      # crt styling
      if WITH_CRT:
        self.crt.draw()

      # update window
      pygame.display.update()

if __name__ == '__main__':
  game = Game()
  game.run()
