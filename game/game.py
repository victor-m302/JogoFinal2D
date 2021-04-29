import pygame
import sys
import random
import settings
import engine

class GameState():
    def __init__(self):
        self.state = "menu"
        self.is_running = True
        self.background_group = pygame.sprite.Group()
        self.moving_background_group = pygame.sprite.Group()
        self.player_group = pygame.sprite.GroupSingle()
        self.game_manager = engine.GameManager(self.player_group)

        farback = engine.AutoMovingBackground("assets/backgrounds/farback.png", 0, 0, 3)
        stars = engine.AutoMovingBackground("assets/backgrounds/stars.png", 0, 0, 1)
        self.background_group.add(farback)
        self.background_group.add(stars)

        self.moving_background = engine.MovingBackground("assets/backgrounds/city.png", 0, 0)
        self.moving_background_group.add(self.moving_background)

    def state_manager(self):
        if self.state == "menu":
            self.menu()
        elif self.state == "lost_level":
            self.lost_level()
        elif self.state == "singleplayer":
            self.singleplayer()
    
    def menu(self):
        self.is_running = True
        title = engine.Text("assets/title/title", 4,
                            settings.screen_width/2, 100, 1, 0.07)

        text_group = pygame.sprite.Group()
        text_group.add(title)

        singleplayer_button = engine.Button(
            "assets/sg_btn/singleplayer", 13, settings.screen_width/2, 400, 0.6, 0.07)
        
        multiplayer_button = engine.Button(
            "assets/mp_btn/multiplayer", 12, settings.screen_width/2, 550, 0.6, 0.07)

        button_group = pygame.sprite.Group()
        button_group.add(singleplayer_button)
        button_group.add(multiplayer_button)

        mouse = engine.Mouse()
        mouse_group = pygame.sprite.Group()
        mouse_group.add(mouse)

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
                            print("singleplayer")
                            self.state = "singleplayer"
                            self.is_running = False
                        elif collision_button.bottom <= 800:
                            settings.button_sound.play()
                            print("multiplayer")
                            self.state = "menu"
                            self.is_running = False
                        
            
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

    def singleplayer(self):
        self.is_running = True
        settings.score = 0

        player = engine.Player("assets/player/player", 6, 100, settings.screen_height, 2, 4, 0.05)
        self.player_group.add(player)

        # self.game_manager.reset_game()

        while self.is_running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                
                # se apertou alguma tecla
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        self.state = "menu"
                        # self.game_manager.reset_game()
                        self.is_running = False

                    if event.key == pygame.K_LEFT:
                        player.movement_x -= player.speed
                        self.moving_background.moving_speed -= player.speed/2
                    if event.key == pygame.K_RIGHT:
                        player.movement_x += player.speed
                        self.moving_background.moving_speed += player.speed/2

                # se soltou alguma tecla
                if event.type == pygame.KEYUP:
                    if event.key == pygame.K_LEFT:
                        player.movement_x += player.speed
                        self.moving_background.moving_speed += player.speed/2
                    if event.key == pygame.K_RIGHT:
                        player.movement_x -= player.speed
                        self.moving_background.moving_speed -= player.speed/2

            self.moving_background_group.draw(settings.screen)
            self.moving_background_group.update()

            self.game_manager.run_game()

            pygame.display.update()
            settings.clock.tick(120)
    
  