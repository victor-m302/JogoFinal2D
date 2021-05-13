import pygame
import sys
import random
import csv
import os
import settings

def read_csv(filename):
    map = []
    with open(os.path.join(filename)) as data:
        data = csv.reader(data, delimiter=',')
        for row in data:
            map.append(list(row))
    return map

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
    def __init__(self, base_images_path, number_of_images, x_pos, y_pos, resize, speed, sprite_speed, tiles):
        super().__init__(base_images_path, number_of_images, x_pos, y_pos, resize)
        self.speed = speed
        self.sprite_speed = sprite_speed 
        self.movement_y = 0 
        self.movement_x = 0 
        self.life = 3
        self.momentum_y = 0
        self.air_timer = 0   
        self.tiles = tiles
        self.scroll_x = 0
        self.scroll_y = 0
    
    def screen_constrain(self):
        if self.rect.top <= 0:  
            self.rect.top = 0
        if self.rect.bottom >= settings.screen_height:
            self.rect.bottom = settings.screen_height 
        if self.rect.left <= 0:
            self.rect.left = 0
        if self.rect.right >= settings.screen_width:
            self.rect.right = settings.screen_width

    def update(self):
        self.current_sprite += self.sprite_speed

        if self.current_sprite >= len(self.sprites):
            self.current_sprite = 0

        self.image = self.sprites[int(self.current_sprite)]

        self.draw_player()
        
        #self.screen_constrain()
    
    def draw_player(self):
        player_movement = [0, 0]

        player_movement[0] = self.movement_x
        player_movement[1] = self.movement_y

        player_movement[1] += self.momentum_y
        self.momentum_y += 0.2
        if self.momentum_y > 3:
            self.momentum_y = 3

        collisions = self.move(player_movement)

        if collisions['bottom']:
            self.momentum_y = 0
            self.air_timer = 0
        else:
            self.air_timer += 1

        settings.display.blit(self.image,(self.rect.x-self.scroll_x,self.rect.y-self.scroll_y))

    def collision_test(self):
        hit_list = []
        for tile in self.tiles:
            if self.rect.colliderect(tile):
                hit_list.append(tile)
        return hit_list

    def move(self, movement):
        collision_types = {'top': False, 'bottom': False, 'right': False, 'left': False}
        self.rect.x += movement[0]
        hit_list = self.collision_test()
        for tile in hit_list:
            if movement[0] > 0:
                self.rect.right = tile.left
                collision_types['right'] = True
            elif movement[0] < 0:
                self.rect.left = tile.right
                collision_types['left'] = True
        self.rect.y += movement[1]
        hit_list = self.collision_test()
        for tile in hit_list:
            if movement[1] > 0:
                self.rect.bottom = tile.top
                collision_types['bottom'] = True
            elif movement[1] < 0:
                self.rect.top = tile.bottom
                collision_types['top'] = True
        return collision_types
    # def move(self, movement):
    #     collision_types = {'top': False, 'bottom': False, 'right': False, 'left': False}
    #     self.rect.x += movement[0]

    #     if pygame.sprite.spritecollide(self, self.tiles, False):
    #         collided_tiles = pygame.sprite.spritecollide(
    #         self, self.tiles, False)
    #         for tile in collided_tiles:    
    #             if movement[0] > 0:
    #                 self.rect.right = tile.rect.left
    #                 collision_types['right'] = True
    #             elif movement[0] < 0:
    #                 self.rect.left = tile.rect.right
    #                 collision_types['left'] = True

    #     self.rect.y += movement[1]
    #     if pygame.sprite.spritecollide(self, self.tiles, False):
    #         collided_tiles = pygame.sprite.spritecollide(
    #         self, self.tiles, False)
    #         for tile in collided_tiles:    
    #             if movement[1] > 0:
    #                 self.rect.bottom = tile.rect.top
    #                 collision_types['bottom'] = True
    #             elif movement[1] < 0:
    #                 self.rect.top = tile.rect.bottom
    #                 collision_types['top'] = True

    #     return collision_types

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

class GameManager():
    def __init__(self, player_group):
        self.player_group = player_group
    
    def run_game(self):
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

class Element(AnimatedBlock):
    def __init__(self, base_images_path, number_of_images, x_pos, y_pos, resize, sprite_speed):
        super().__init__(base_images_path, number_of_images, x_pos, y_pos, resize)
        self.sprite_speed = sprite_speed

    def update(self):
        self.current_sprite += self.sprite_speed

        if self.current_sprite >= len(self.sprites):
            self.current_sprite = 0

        self.image = self.sprites[int(self.current_sprite)]

class Tile(pygame.sprite.Sprite):
    def __init__(self, image_path, initial_x_pos, initial_y_pos):
        super().__init__()
        self.image = pygame.image.load(image_path).convert_alpha() 
        self.rect = self.image.get_rect(center=(initial_x_pos, initial_y_pos))
        self.initial_x_pos = initial_x_pos
        self.initial_y_pos = initial_y_pos
    
    def draw_tile(self, scroll_x, scroll_y):
        settings.display.blit(self.image, (self.initial_x_pos - scroll_x, self.initial_y_pos - scroll_y))

class TileMap():
    def __init__(self, tiles, tile_rects):
        super().__init__()
        self.tiles = tiles
    
    def draw_map(self, scroll_x, scroll_y):
        for tile in self.tiles:
            tile.draw_tile(scroll_x, scroll_y)

