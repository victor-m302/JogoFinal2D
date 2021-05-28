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

class CharacterBlock(pygame.sprite.Sprite): # classe base
    def __init__(self, base_images_path_left, base_images_path_right, number_of_images, x_pos, y_pos, resize):
        super().__init__()
        self.sprites_left = []
        self.sprites_right = []

        for i in range(number_of_images):
            image_path = base_images_path_left + str(i + 1) + ".png"
            image = pygame.image.load(image_path).convert_alpha()
            resized_image = pygame.transform.scale(image, (int(image.get_rect().width * resize), int(image.get_rect().height * resize)))
            self.sprites_left.append(resized_image)
        
        for i in range(number_of_images):
            image_path = base_images_path_right + str(i + 1) + ".png"
            image = pygame.image.load(image_path).convert_alpha()
            resized_image = pygame.transform.scale(image, (int(image.get_rect().width * resize), int(image.get_rect().height * resize)))
            self.sprites_right.append(resized_image)

        self.current_sprite = 0
        self.image = self.sprites_right[self.current_sprite]

        self.rect = self.image.get_rect()
        self.rect.center = [x_pos, y_pos]

class Enemy(AnimatedBlock):
    def __init__(self, base_images_path, number_of_images, x_pos, y_pos, resize, sprite_speed, tiles, player):
        super().__init__(base_images_path, number_of_images, x_pos, y_pos, resize)
        self.CHASING_PLAYER = False
        self.speed = random.uniform(1, 3)
        self.sprite_speed = sprite_speed 
        self.movement_y = 0 
        self.movement_x = self.speed
        self.tiles = tiles
        self.player = player
        self.life = 3
        self.momentum_y = 0
        self.air_timer = 0   
        self.scroll_x = 0
        self.scroll_y = 0
        self.initial_x_position = x_pos
        self.initial_y_position = y_pos
    
    def screen_constrain(self):
        if self.rect.bottom >= settings.screen_height:
            self.kill() 

    def update(self):
        self.current_sprite += self.sprite_speed

        if self.current_sprite >= len(self.sprites):
            self.current_sprite = 0

        self.image = self.sprites[int(self.current_sprite)]

        self.draw_enemy()
        
        self.screen_constrain()
    
    def enemy_ai(self):
        if not self.CHASING_PLAYER and abs(self.player.sprite.rect.x - self.rect.x) <= 100:
            self.CHASING_PLAYER = True

        if self.CHASING_PLAYER:
            if self.player.sprite.rect.x >= self.rect.x:
                self.movement_x = self.speed * 1.25
            else:
                self.movement_x = -self.speed 
        elif abs(self.initial_x_position - self.rect.x) >= 200:
            if abs(self.movement_x) > 0:
                self.movement_x *= -1
            else:
                self.movement_x = self.speed
        else:
            self.movement_x = 0   
    
    def draw_enemy(self):
        enemy_movement = [0, 0]

        self.enemy_ai()

        enemy_movement[0] = self.movement_x
        enemy_movement[1] = self.movement_y

        enemy_movement[1] += self.momentum_y
        self.momentum_y += 0.2
        if self.momentum_y > 3:
            self.momentum_y = 3

        collisions = self.move(enemy_movement)

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

class Player(CharacterBlock):
    def __init__(self, base_images_path_left, base_images_path_right,number_of_images, x_pos, y_pos, resize, speed, sprite_speed, tiles, enemy_group, default_image):
        super().__init__(base_images_path_left, base_images_path_right, number_of_images, x_pos, y_pos, resize)
        self.LEFT_KEY = False
        self.RIGHT_KEY = False
        self.FACING_LEFT = False
        self.FACING_RIGHT = True
        self.RESTING = True
        self.SHOOTING = False
        self.speed = speed
        self.sprite_speed = sprite_speed 
        self.enemy_group = enemy_group
        self.movement_y = 0 
        self.movement_x = 0 
        self.life = 3
        self.momentum_y = 0
        self.air_timer = 0   
        self.tiles = tiles
        self.scroll_x = 0
        self.scroll_y = 0
        self.friction_right, self.friction_left = -.045, -.1
        self.acceleration = 0
        self.default_image = 0
    

    def set_Default_img(self,base_image_path,resize):
            image_path = base_image_path #path da imagem com nome do arquivo e tipo
            image = pygame.image.load(image_path).convert_alpha()
            resized_image = pygame.transform.scale(image, (int(image.get_rect().width * resize), int(image.get_rect().height * resize)))
            return resized_image
            #image = pygame.image.load('/feira/banana.png').convert_alpha()


    def screen_constrain(self):
        if self.rect.bottom >= settings.screen_height:
            self.rect.bottom = 0 

    def update(self):
        if self.movement_x > 0.8 or self.movement_x < -0.1: # se movendo pra frente ou tras 
            self.current_sprite += self.sprite_speed

            if self.current_sprite >= len(self.sprites_left):
                self.current_sprite = 0

            if self.FACING_RIGHT:
                self.image = self.sprites_right[int(self.current_sprite)]
            elif self.FACING_LEFT:
                self.image = self.sprites_left[int(self.current_sprite)]
        else: #parado

            self.current_sprite = 0
            if self.FACING_RIGHT:
                self.image = self.set_Default_img('./assets/player/player1_R.png',1)
            elif self.FACING_LEFT:
                self.image = self.set_Default_img('./assets/player/player1_L.png',1)

            if self.FACING_RIGHT and self.SHOOTING:
                self.image = self.set_Default_img('./assets/player/player_shootR.png',1)
            elif self.FACING_LEFT and self.SHOOTING:
                self.image = self.set_Default_img('./assets/player/player_shootL.png',1)
            


        self.draw_player()  
        self.screen_constrain()
        self.collision()


        '''
        else: #parado
            self.current_sprite = 0
            if self.FACING_RIGHT:
                self.image = self.sprites_right[0]
            elif self.FACING_LEFT:
                self.image = self.sprites_left[0]
        '''
    def collision(self):
        if pygame.sprite.spritecollide(self, self.enemy_group, False):
            collided_enemies = pygame.sprite.spritecollide(
                self, self.enemy_group, False)

            pygame.mixer.Sound.play(settings.destroy_sound)

            for collided_enemy in collided_enemies:
                collided_enemy.kill()
                self.life -= 1
    
    def draw_player(self):
        self.horizontal_movement()
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

    def horizontal_movement(self): 
        self.acceleration = 0
        if self.LEFT_KEY:
            self.acceleration -= .4
        elif self.RIGHT_KEY:
            self.acceleration += .25
        
        if self.FACING_LEFT:
            self.acceleration += self.movement_x * self.friction_left
        elif self.FACING_RIGHT:
            self.acceleration += self.movement_x * self.friction_right
        self.movement_x += self.acceleration
        self.limit_velocity(4)

    def limit_velocity(self, max_velocity):
        min(-max_velocity, max(self.movement_x, max_velocity))
        # if abs(self.movement_x) > max_velocity:
        #     if self.movement_x > 0:
        #         self.movement_x = max_velocity
        #     else:
        #         self.movement_x = -max_velocity
        if abs(self.movement_x) < .01: self.movement_x = 0

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
    def __init__(self, player_group, enemy_group):
        self.player_group = player_group
        self.enemy_group = enemy_group
    
    def run_game(self):
        self.player_group.update()
        self.enemy_group.update()

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

