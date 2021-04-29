import pygame
import sys
import random
import settings

class Block(pygame.sprite.Sprite):
    def __init__(self, image_path, x_pos, y_pos):
        super().__init__()
        self.image = pygame.image.load(image_path).convert_alpha()  # carrega o sprite
        self.rect = self.image.get_rect(center=(x_pos, y_pos)) # desenha o retangulo em volta da imagem

class AnimatedBlock(pygame.sprite.Sprite): # classe base
    def __init__(self, base_images_path, number_of_images, x_pos, y_pos, resize):
        super().__init__()
        self.sprites = []

        for i in range(number_of_images):
            image_path = base_images_path + str(i + 1) + ".png"
            image = pygame.image.load(image_path).convert_alpha()
            resized_image = pygame.transform.scale(image, (int(image.get_rect().width * resize), int(image.get_rect().height * resize)))
            self.sprites.append(resized_image)

        self.current_sprite = 0
        self.image = self.sprites[self.current_sprite]

        self.rect = self.image.get_rect()
        self.rect.center = [x_pos, y_pos]

class Player(AnimatedBlock):
    def __init__(self, base_images_path, number_of_images, x_pos, y_pos, resize, speed, sprite_speed):
        super().__init__(base_images_path, number_of_images, x_pos, y_pos, resize)
        self.speed = speed
        self.sprite_speed = sprite_speed 
        self.movement_y = 0 
        self.movement_x = 0 
        self.life = 3
    
    def screen_constrain(self):
        if self.rect.top <= 0:  
            self.rect.top = 0
        if self.rect.bottom >= settings.screen_height:
            self.rect.bottom = settings.screen_height 
        if self.rect.left <= 0:
            self.rect.left = 0
        if self.rect.right >= settings.screen_width/2 + self.rect.width/2:
            self.rect.right = settings.screen_width/2 + self.rect.width/2

    def update(self):
        print(settings.moving_bg)
        if (settings.moving_bg >= 0 and self.movement_x > 0):
            settings.moving_bg += self.movement_x
        if (settings.moving_bg >= 10 and self.movement_x < 0):
            settings.moving_bg += self.movement_x
        self.rect.x += self.movement_x
        
        self.current_sprite += self.sprite_speed

        if self.current_sprite >= len(self.sprites):
            self.current_sprite = 0

        self.image = self.sprites[int(self.current_sprite)]
        
        self.screen_constrain() 


class AutoMovingBackground(Block):
    def __init__(self, image_path, x_pos, y_pos, moving_speed):
        super().__init__(image_path, x_pos, y_pos)
        self.moving_speed = moving_speed
        self.moving_x = 0
        self.relative_x = 0
    
    def update(self):
        self.moving_x -= self.moving_speed
        self.relative_x = self.moving_x % self.rect.width
        settings.screen.blit(self.image, (self.relative_x - self.rect.width, 0))

        if self.relative_x < settings.screen_width:
            settings.screen.blit(self.image, (self.relative_x, 0))

class MovingBackground(Block):
    def __init__(self, image_path, x_pos, y_pos):
        super().__init__(image_path, x_pos, y_pos)
        self.moving_speed = 0
        self.moving_x = 0
        self.relative_x = 0
        self.initial_left = self.rect.left
    
    def update(self):
        if settings.moving_bg >= 10:
            self.moving_x -= self.moving_speed
            self.relative_x = self.moving_x % self.rect.width
        else:
            self.moving_x = 0
            self.relative_x = 0

        settings.screen.blit(self.image, (self.relative_x - self.rect.width, 0))

        if self.relative_x < settings.screen_width:
            settings.screen.blit(self.image, (self.relative_x, 0))    

class GameManager():
    def __init__(self, player_group):
        self.player_group = player_group
    
    def run_game(self):
        self.player_group.draw(settings.screen)

        self.player_group.update()

    def reset_game(self):
        print("")

class Mouse(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.Surface([1, 1])
        self.image.fill((255, 255, 255))
        self.rect = self.image.get_rect()

    def update(self):
        self.rect.center = pygame.mouse.get_pos()

class Button(AnimatedBlock):
    def __init__(self, base_images_path, number_of_images, x_pos, y_pos, resize, sprite_speed):
        super().__init__(base_images_path, number_of_images, x_pos, y_pos, resize)
        self.sprite_speed = sprite_speed

    def update(self):
        self.current_sprite += self.sprite_speed

        if self.current_sprite >= len(self.sprites):
            self.current_sprite = 0

        self.image = self.sprites[int(self.current_sprite)]

class Text(AnimatedBlock):
    def __init__(self, base_images_path, number_of_images, x_pos, y_pos, resize, sprite_speed):
        super().__init__(base_images_path, number_of_images, x_pos, y_pos, resize)
        self.sprite_speed = sprite_speed

    def update(self):
        self.current_sprite += self.sprite_speed

        if self.current_sprite >= len(self.sprites):
            self.current_sprite = 0

        self.image = self.sprites[int(self.current_sprite)]