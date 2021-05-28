import pygame
import sys
import random
import settings
import engine
import csv
import os

true_scroll = [0, 0]

def read_csv(filename):
    map = []
    with open(os.path.join(filename)) as data:
        data = csv.reader(data, delimiter=',')
        for row in data:
            map.append(list(row))
    return map

game_map = read_csv('./maps/stage_one.csv')

class GameState():
    def __init__(self):
        self.state = "menu"
        self.is_running = True
        self.background_group = pygame.sprite.Group()
        self.player_group = pygame.sprite.GroupSingle()
        self.enemy_group = pygame.sprite.Group()
        self.bullet_group = pygame.sprite.Group()
        self.game_manager = engine.GameManager(self.player_group, self.enemy_group, self.bullet_group)
        farback = engine.AutoMovingBackground("assets/backgrounds/farback.png", 0, 0, 1)
        logo = engine.AutoMovingBackground("assets/backgrounds/logo.png", 0, 0, 0)
        self.background_group.add(farback)
        self.background_group.add(logo)
        self.player = {}
        self.tile_rects = []

    def state_manager(self):
        if self.state == "menu":
            self.menu()
        elif self.state == "lose_screen":
            self.lost_level()
        elif self.state == "level1":
            self.level1()

    def game_events(self):
        for event in pygame.event.get():
                if self.player.life <= 0:
                    self.state = "lose_screen"
                    self.game_manager.reset_game()
                    self.is_running = False
                    
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                
                # se apertou alguma tecla
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        self.state = "lose_screen"
                        self.game_manager.reset_game()
                        self.is_running = False

                    if event.key == pygame.K_LEFT:
                        self.player.LEFT_KEY = True
                        self.player.FACING_LEFT = True
                        self.player.FACING_RIGHT = False
                    if event.key == pygame.K_RIGHT:
                        self.player.RIGHT_KEY = True
                        self.player.FACING_RIGHT = True
                        self.player.FACING_LEFT = False
                    if event.key == pygame.K_UP:
                        if self.player.air_timer < 6:
                            self.player.momentum_y = -5
                    if event.key == pygame.K_SPACE:
                        if(len(self.bullet_group.sprites()) < 5):
                            self.player.SHOOTING = True
                            if self.player.FACING_RIGHT:
                                pygame.mixer.Sound.play(settings.laser_sound)
                                new_bullet = engine.Bullet(
                                    "assets/bulletR.png", self.player.rect.centerx + 20, self.player.rect.centery - 8, 8, self.enemy_group, self.player_group)
                                self.bullet_group.add(new_bullet)
                            elif self.player.FACING_LEFT:
                                pygame.mixer.Sound.play(settings.laser_sound)
                                new_bullet = engine.Bullet(
                                    "assets/bulletL.png", self.player.rect.centerx - 20, self.player.rect.centery - 8, -8, self.enemy_group, self.player_group)
                                self.bullet_group.add(new_bullet)
                # se soltou alguma tecla
                if event.type == pygame.KEYUP:
                    if event.key == pygame.K_LEFT:
                        self.player.LEFT_KEY = False
                    if event.key == pygame.K_RIGHT:
                        self.player.RIGHT_KEY = False
                    if event.key == pygame.K_SPACE:
                        self.player.SHOOTING = False
    
    def lost_level(self):
        self.is_running = True

        lost_level_text = settings.basic_font.render(
            "Your total score is " + str(settings.score), True, settings.font_color)
        lost_level_text_rect = lost_level_text.get_rect(
            center=(settings.screen_width/2, settings.screen_height/2 - 50))

        press_space_text = settings.basic_font.render(
            "Press space to return to the menu", True, settings.font_color)
        press_space_text_rect = press_space_text.get_rect(
            center=(settings.screen_width/2, settings.screen_height/2 + 50))

        while self.is_running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        settings.score = 0
                        self.state = "menu"
                        self.is_running = False

            settings.screen.fill((0, 0, 0))

            settings.screen.blit(lost_level_text, lost_level_text_rect)
            settings.screen.blit(press_space_text, press_space_text_rect)
            pygame.display.update()
            settings.clock.tick(120)
    
    def menu(self):
        self.is_running = True
        # title = engine.Element("assets/menu/title", 1, settings.screen_width/2, 50, 1, 0.07)

        text_group = pygame.sprite.Group()
        # text_group.add(title)
        

        singleplayer_button = engine.Button(
            "assets/sg_btn/singleplayer", 13, settings.screen_width/2, 400, 0.6, 0.07)
        
        #multiplayer_button = engine.Button("assets/mp_btn/multiplayer", 12, settings.screen_width/2, 550, 0.6, 0.07)

        button_group = pygame.sprite.Group()
        button_group.add(singleplayer_button)
        #button_group.add(multiplayer_button)

        mouse = engine.Mouse()
        mouse_group = pygame.sprite.Group()
        mouse_group.add(mouse)

        settings.zombie_theme.play()

        while self.is_running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                
                # se apertou alguma tecla
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        self.state = "menu"
                        self.is_running = False
                
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if pygame.sprite.spritecollide(mouse, button_group, False):
                        collision_button = pygame.sprite.spritecollide(
                            mouse, button_group, False)[0].rect
                        print(collision_button.bottom)
                        if collision_button.bottom <= 500:
                            settings.button_sound.play()
                            self.state = "level1"
                            self.is_running = False
                        # elif collision_button.bottom <= 800:
                        #     settings.button_sound.play()
                        #     print("multiplayer")
                        #     self.state = "menu"
                        #     self.is_running = False
                        
            
            settings.screen.fill(settings.bg_color)
            self.background_group.draw(settings.screen)
            self.background_group.update()

            button_group.draw(settings.screen)
            text_group.draw(settings.screen)
            mouse_group.draw(settings.screen)

            button_group.update()
            text_group.update()
            mouse_group.update()

            pygame.display.update()
            settings.clock.tick(120)

    def level1(self):
        self.is_running = True
        settings.score = 0
        settings.zombie_theme.fadeout(10)
        level_map = read_csv('./maps/stage_one.csv')

        self.player = {}
        tiles = []
        self.tile_rects = []
        
        y = 0
        for row in level_map:
            x = 0
            for tile in row:
                if tile == '9':
                    self.player = engine.Player("assets/player/left/l", "assets/player/right/r", 7, x * 32, y * 32, 1, 3, 0.3, self.tile_rects, self.enemy_group)
                    self.player_group.add(self.player)    
                elif tile == '8':
                    enemy = engine.Enemy("assets/enemy/class3/l", "assets/enemy/class3/r", 3, x * 32, y * 32, 1, 0.07, self.tile_rects, self.player_group)
                    self.enemy_group.add(enemy)
                elif tile != '-1':
                    new_tile = engine.Tile('./assets/tiles/tile' + tile + '.png', x * 32, y * 32)
                    tiles.append(new_tile)
                    self.tile_rects.append(pygame.Rect(x * 32, y * 32, 32, 32))
                x += 1
            y += 1

        tile_map = engine.TileMap(tiles, self.tile_rects)    

        while self.is_running:

            true_scroll[0] += (self.player.rect.x-true_scroll[0] - 202)/20
            true_scroll[1] += (self.player.rect.y-true_scroll[1] - 200)/20

            scroll = true_scroll.copy()
            scroll[0] = int(scroll[0])
            scroll[1] = int(scroll[1])

            settings.display.fill(settings.bg_color)

            bg_image = pygame.image.load('assets/backgrounds/night-city.png').convert()
            bg_scaled = pygame.transform.scale(bg_image, (960, 720))
            settings.display.blit(bg_scaled, (0, 0))

            self.player.scroll_x = scroll[0]
            self.player.scroll_y = scroll[1]

            for enemy in self.enemy_group:
                enemy.scroll_x = scroll[0]
                enemy.scroll_y = scroll[1]

            self.game_events()
            
            for bullet in self.bullet_group:
                    bullet.scroll_x = scroll[0]
                    bullet.scroll_y = scroll[1]
            
            settings.screen.fill(settings.bg_color)
            self.game_manager.run_game()
            tile_map.draw_map(scroll[0], scroll[1])
            surf = pygame.transform.scale(settings.display, (settings.screen_width, settings.screen_height))
            settings.screen.blit(surf, (0, 0))

            pygame.display.update()
            settings.clock.tick(120)
    
  