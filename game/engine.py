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

class Enemy(CharacterBlock):
    def __init__(self, base_images_path_left, base_images_path_right, number_of_images, x_pos, y_pos, resize, sprite_speed, tiles, player):
        super().__init__(base_images_path_left, base_images_path_right, number_of_images, x_pos, y_pos, resize)
        self.CHASING_PLAYER = False
        self.FACING_RIGHT = True
        self.FACING_LEFT = False
        self.speed = random.uniform(1, 3)
        self.sprite_speed = sprite_speed 
        self.movement_y = 0 
        self.movement_x = self.speed * 1.25
        self.tiles = tiles
        self.player = player
        self.initial_life = random.randint(10, 15)
        self.life = self.initial_life
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
        if (self.life == 0):
            self.kill()

        self.current_sprite += self.sprite_speed

        if self.current_sprite >= len(self.sprites_left):
            self.current_sprite = 0

        if self.FACING_RIGHT:
            self.image = self.sprites_right[int(self.current_sprite)]
        elif self.FACING_LEFT:
            self.image = self.sprites_left[int(self.current_sprite)]

        self.draw_enemy()
        
        self.screen_constrain()
    
    def enemy_ai(self):
        if not self.CHASING_PLAYER and abs(self.player.sprite.rect.x - self.rect.x) <= 200:
            self.CHASING_PLAYER = True

        if self.CHASING_PLAYER:
            if self.player.sprite.rect.x >= self.rect.x:
                self.FACING_RIGHT = True
                self.FACING_LEFT = False
                self.movement_x = self.speed * 1.25

            else:
                self.FACING_RIGHT = False
                self.FACING_LEFT = True
                self.movement_x = -self.speed 

        else:
            if self.FACING_RIGHT and (self.rect.x - self.initial_x_position) <= 200:
                self.movement_x = self.speed * 1.5
            else:
                self.FACING_RIGHT = False
                self.FACING_LEFT = True

            if self.FACING_LEFT and (self.rect.x - self.initial_x_position) >= -200:
                self.movement_x = -self.speed
            else:
                self.FACING_RIGHT = True
                self.FACING_LEFT = False
    
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
    def __init__(self, base_images_path_left, base_images_path_right, number_of_images, x_pos, y_pos, resize, speed, sprite_speed, tiles, enemy_group):
        super().__init__(base_images_path_left, base_images_path_right, number_of_images, x_pos, y_pos, resize)
        self.LEFT_KEY = False
        self.RIGHT_KEY = False
        self.FACING_LEFT = False
        self.FACING_RIGHT = True
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
        self.player_shooting = [pygame.image.load('assets/player/shootingR.png'), pygame.image.load('assets/player/shootingL.png')]
        self.player_standing = [pygame.image.load('assets/player/standingR.png'), pygame.image.load('assets/player/standingL.png')]
    
    def screen_constrain(self):
        if self.rect.bottom >= settings.screen_height:
            self.life = 0

    def update(self):
        if self.SHOOTING:
            if self.FACING_RIGHT:
                self.image = self.player_shooting[0]
            if self.FACING_LEFT:
                self.image = self.player_shooting[1]

        elif self.movement_x > 0.8 or self.movement_x < -0.1:
            self.current_sprite += self.sprite_speed

            if self.current_sprite >= len(self.sprites_left):
                self.current_sprite = 0

            if self.FACING_RIGHT:
                self.image = self.sprites_right[int(self.current_sprite)]
            elif self.FACING_LEFT:
                self.image = self.sprites_left[int(self.current_sprite)]
        else:
            self.current_sprite = 0
            if self.FACING_RIGHT:
                self.image = self.player_standing[0]
            elif self.FACING_LEFT:
                self.image = self.player_standing[1]

        self.draw_player()  
        self.screen_constrain()
        self.collision()

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

class Bullet(Block):
    def __init__(self, image_path, x_pos, y_pos, shoot_speed, enemy_group, player_group):
        super().__init__(image_path, x_pos, y_pos)
        self.is_active = False
        self.shoot_speed = shoot_speed
        self.enemy_group = enemy_group
        self.player_group = player_group
        self.scroll_x = 0
        self.scroll_y = 0
        self.initial_pos_x = x_pos

    def update(self):
        self.rect.x += self.shoot_speed
        self.draw_bullet()
        self.collision()

    def draw_bullet(self):
        settings.display.blit(self.image,(self.rect.x-self.scroll_x,self.rect.y-self.scroll_y))

    def collision(self):
        if abs(self.initial_pos_x - self.rect.x) >= 700:
            self.kill()

        # definição da colisão
        if pygame.sprite.spritecollide(self, self.enemy_group, False):
            collided_enemies = pygame.sprite.spritecollide(
                self, self.enemy_group, False)

            settings.score += 100 * len(collided_enemies)
            pygame.mixer.Sound.play(settings.destroy_sound)

            for collided_enemy in collided_enemies:
                self.kill()
                if collided_enemy.life - 1 == 0:
                    settings.score += 100 * collided_enemy.initial_life

                collided_enemy.life -= 1

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
    def __init__(self, player_group, enemy_group, bullet_group):
        self.player_group = player_group
        self.enemy_group = enemy_group
        self.bullet_group = bullet_group
    
    def run_game(self):
        self.player_group.update()
        self.enemy_group.update()
        self.bullet_group.update()

        self.draw_score()
        self.draw_life()

    def reset_game(self):
        for player in self.player_group.sprites():
            player.kill()

        for bullet in self.bullet_group.sprites():
            bullet.kill()
        
        for enemy in self.enemy_group.sprites():
            enemy.kill()

    def draw_score(self):
        player_score = settings.basic_font.render(
            "SCORE " + str(settings.score), True, settings.font_color)

        player_score_rect = player_score.get_rect(
            midleft=(10, 20))

        settings.display.blit(player_score, player_score_rect)

    def draw_life(self):
        lifes_text = settings.basic_font.render(    
            "LIFES ", True, settings.font_color)

        if (self.player_group.sprite):
            self.draw_heart(self.player_group.sprite.life)

        lifes_text_rect = lifes_text.get_rect(
            midleft=(10, 46))

        settings.display.blit(lifes_text, lifes_text_rect)
    
    def draw_heart(self, life):
        heart = pygame.image.load('assets/heart.png')
        for i in range(life):
            settings.display.blit(heart, (i * 32 + 100, 32))

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

