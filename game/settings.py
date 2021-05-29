import pygame
import sys
import random

# Setup padrão
pygame.mixer.pre_init(44100, -16, 2, 512)
pygame.init()
clock = pygame.time.Clock()

# Janela principal
screen_width = 960  # largura
screen_height = 720  # altura

screen = pygame.display.set_mode((screen_width, screen_height), 0, 32)

display = pygame.Surface((600, 400))

pygame.display.set_caption("Journey in the Land of Zombies | ゾンビの国の旅")  # titulo

bg_color = pygame.Color("#76d7ea")  # cor de fundo
font_color = pygame.Color("#ffffff") # cor da fonte
basic_font = pygame.font.Font("fonts/8-BIT-WONDER.ttf", 20)  # carrega a fonte

slow_time = 1

# sons de efeito
laser_sound = pygame.mixer.Sound(
    "audio/laser.wav")
destroy_sound = pygame.mixer.Sound("audio/destroy.wav")
hit_sound = pygame.mixer.Sound("audio/hit.wav")
button_sound = pygame.mixer.Sound("audio/button.wav") 
slow_time_sound = pygame.mixer.Sound("audio/slow_time.mp3") 
time_resume_sound = pygame.mixer.Sound("audio/time_resume.mp3") 
zombie_theme = pygame.mixer.Sound("audio/zombiegame_low_audio.mp3") 

# score do jogo
score = 0
moving_bg = 0

# collision wall
collision_level = 0
collision_wall = 0


# FASE 01 - TOTAL 288x48 == 239x48
# FASE 02 - 80 x 32
# FASE 03 - 144 x 64 - 144 x 58
# FASE 04 - 103 x 80 - 103 x 67
# FASE 05 - 160 x 32 - 160 x 17